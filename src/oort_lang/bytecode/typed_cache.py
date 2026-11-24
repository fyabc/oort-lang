#! /usr/bin/env python

"""On-disk cache for typed module artifacts (OP 0030).

Entries are content-addressed under a versioned layout:

``<dir>/v<artifact>/abi<N>/<ab>/<cd>/<key>.obc``

The key covers source bytes, module id, compiler version, artifact/ABI
versions, codegen options and the interface hashes of direct dependencies.
Interface changes therefore miss immediately; implementation-only changes in
a dependency keep its dependents valid. Any damaged or incompatible entry is
treated as a miss and replaced.

Writes are single-flight per key: a lock file serialises concurrent compilers,
with a timeout fallback because atomic replace already keeps readers safe.
Each entry has a JSON sidecar with module/dependency metadata, and optional
size limits evict least-recently-used entries.
"""

from __future__ import annotations

import contextlib
import dataclasses
import hashlib
import json
import os
import shutil
import time
from pathlib import Path
from typing import TYPE_CHECKING

from .. import __version__
from .serialize import ObcError
from .typed_artifact import (
    ABI_VERSION,
    ARTIFACT_VERSION,
    TypedArtifact,
    read_typed_artifact,
    write_typed_artifact,
)

if TYPE_CHECKING:
    from collections.abc import Iterator, Mapping

    from ..hir.typed_link import TypedUnit

_CACHE_SCHEMA = "oort-cache-v1"
_CODEGEN_OPTIONS = ""  # reserved for target/optimization flags
_LOCK_STALE_SECONDS = 60.0
_LOCK_WAIT_SECONDS = 30.0
_LOCK_POLL_SECONDS = 0.01


@dataclasses.dataclass(frozen=True, slots=True)
class CacheStats:
    directory: Path
    entries: int
    size_bytes: int


def _dependency_key(dependencies: Mapping[str, int]) -> str:
    return "\n".join(
        f"{module_id}:{abi_hash}" for module_id, abi_hash in sorted(dependencies.items())
    )


class TypedArtifactCache:
    """A versioned, content-addressed directory of typed module artifacts."""

    def __init__(self, directory: str | Path, max_size: int | None = None):
        self.directory = Path(directory)
        self.max_size = max_size
        self.directory.mkdir(parents=True, exist_ok=True)
        self._version_dir = self.directory / f"v{ARTIFACT_VERSION}" / f"abi{ABI_VERSION}"
        self._tmp_dir = self.directory / "tmp"
        self._lock_dir = self.directory / "locks"

    def key(self, unit: TypedUnit, dependencies: Mapping[str, int]) -> str | None:
        if unit.path is None:
            return None
        source = unit.path.read_bytes()
        digest = hashlib.sha256()
        for part in (
            _CACHE_SCHEMA,
            str(ARTIFACT_VERSION),
            str(ABI_VERSION),
            __version__,
            _CODEGEN_OPTIONS,
            unit.module_id,
            _dependency_key(dependencies),
        ):
            digest.update(part.encode("utf-8"))
            digest.update(b"\0")
        digest.update(source)
        return digest.hexdigest()

    def path_for(self, unit: TypedUnit, dependencies: Mapping[str, int]) -> Path | None:
        key = self.key(unit, dependencies)
        if key is None:
            return None
        return self._version_dir / key[:2] / key[2:4] / f"{key}.obc"

    def load(self, unit: TypedUnit, dependencies: Mapping[str, int]) -> TypedArtifact | None:
        path = self.path_for(unit, dependencies)
        if path is None or not path.exists():
            return None
        try:
            artifact = read_typed_artifact(path)
        except (ObcError, OSError):
            return None
        if artifact.module_id != unit.module_id:
            return None
        try:
            os.utime(path, None)
        except OSError:
            pass
        return artifact

    def store(
        self,
        unit: TypedUnit,
        artifact: TypedArtifact,
        dependencies: Mapping[str, int],
    ) -> None:
        path = self.path_for(unit, dependencies)
        if path is None:
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        self._tmp_dir.mkdir(parents=True, exist_ok=True)
        temporary = self._tmp_dir / f"{path.name}.{os.getpid()}.tmp"
        write_typed_artifact(artifact, temporary)
        try:
            temporary.replace(path)
        finally:
            temporary.unlink(missing_ok=True)
        self._write_manifest(unit, path, dependencies)
        self._enforce_limit()

    @contextlib.contextmanager
    def entry_lock(self, unit: TypedUnit, dependencies: Mapping[str, int]) -> Iterator[str]:
        """Serialise compilation of one key.

        Yields ``"owned"`` (lock acquired), ``"ready"`` (another process
        produced the entry) or ``"timeout"`` (proceed without a lock).
        """

        key = self.key(unit, dependencies)
        if key is None:
            yield "timeout"
            return
        entry = self.path_for(unit, dependencies)
        assert entry is not None
        self._lock_dir.mkdir(parents=True, exist_ok=True)
        lock_path = self._lock_dir / f"{key}.lock"
        status = self._acquire(lock_path, entry)
        try:
            yield status
        finally:
            if status == "owned":
                lock_path.unlink(missing_ok=True)

    def _acquire(self, lock_path: Path, entry: Path) -> str:
        deadline = time.monotonic() + _LOCK_WAIT_SECONDS
        while True:
            if entry.exists():
                return "ready"
            try:
                descriptor = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            except FileExistsError:
                try:
                    age = time.time() - lock_path.stat().st_mtime
                except OSError:
                    continue
                if age > _LOCK_STALE_SECONDS:
                    lock_path.unlink(missing_ok=True)
                    continue
                if time.monotonic() >= deadline:
                    return "timeout"
                time.sleep(_LOCK_POLL_SECONDS)
                continue
            try:
                os.write(descriptor, f"{os.getpid()}\n".encode("ascii"))
            finally:
                os.close(descriptor)
            return "owned"

    def _write_manifest(
        self,
        unit: TypedUnit,
        path: Path,
        dependencies: Mapping[str, int],
    ) -> None:
        data = {
            "schema": _CACHE_SCHEMA,
            "module_id": unit.module_id,
            "compiler": __version__,
            "artifact_version": ARTIFACT_VERSION,
            "abi_version": ABI_VERSION,
            "dependencies": dict(sorted(dependencies.items())),
            "stored_at": int(time.time()),
        }
        temporary = self._tmp_dir / f"{path.stem}.{os.getpid()}.json.tmp"
        try:
            temporary.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            temporary.replace(path.with_suffix(".json"))
        except OSError:
            pass
        finally:
            temporary.unlink(missing_ok=True)

    def _enforce_limit(self) -> None:
        if not self.max_size or self.max_size <= 0 or not self._version_dir.exists():
            return
        entries = list(self._version_dir.rglob("*.obc"))
        sized: list[tuple[float, int, Path]] = []
        total = 0
        for path in entries:
            try:
                stat = path.stat()
            except OSError:
                continue
            sized.append((stat.st_mtime, stat.st_size, path))
            total += stat.st_size
        if total <= self.max_size:
            return
        sized.sort()
        while len(sized) > 1 and total > self.max_size:
            _, size, path = sized.pop(0)
            try:
                path.unlink()
            except OSError:
                continue
            path.with_suffix(".json").unlink(missing_ok=True)
            total -= size

    def stats(self) -> CacheStats:
        entries = 0
        size = 0
        if self._version_dir.exists():
            for path in self._version_dir.rglob("*.obc"):
                entries += 1
                try:
                    size += path.stat().st_size
                except OSError:
                    pass
        return CacheStats(self.directory, entries, size)

    def clean(self) -> int:
        """Remove cached artifacts for this schema version."""

        removed = 0
        if self._version_dir.exists():
            removed = sum(1 for path in self._version_dir.rglob("*") if path.is_file())
            shutil.rmtree(self._version_dir)
        for directory in (self._tmp_dir, self._lock_dir):
            if directory.exists():
                shutil.rmtree(directory, ignore_errors=True)
        return removed

    def __repr__(self) -> str:
        return f"TypedArtifactCache({str(self.directory)!r})"


__all__ = ["CacheStats", "TypedArtifactCache"]
