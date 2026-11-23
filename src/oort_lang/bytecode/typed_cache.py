#! /usr/bin/env python

"""On-disk cache for typed module artifacts (OP 0030).

Entries are content-addressed under a versioned layout:

``<dir>/v8/abi<N>/<ab>/<cd>/<key>.obc``

The key covers source bytes, module id, compiler version, artifact/ABI
versions, codegen options and the interface hashes of direct dependencies.
Interface changes therefore miss immediately; implementation-only changes in
a dependency keep its dependents valid. Any damaged or incompatible entry is
treated as a miss and replaced.
"""

from __future__ import annotations

import dataclasses
import hashlib
import shutil
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
    from collections.abc import Mapping

    from ..hir.typed_link import TypedUnit

_CACHE_SCHEMA = "oort-cache-v1"
_CODEGEN_OPTIONS = ""  # reserved for target/optimization flags


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
    """A versioned, content-addressed directory of v8 artifacts."""

    def __init__(self, directory: str | Path):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self._version_dir = self.directory / "v8" / f"abi{ABI_VERSION}"
        self._tmp_dir = self.directory / "tmp"

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
        temporary = self._tmp_dir / f"{path.name}.tmp"
        write_typed_artifact(artifact, temporary)
        try:
            temporary.replace(path)
        finally:
            temporary.unlink(missing_ok=True)

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
            removed = sum(1 for _ in self._version_dir.rglob("*") if _.is_file())
            shutil.rmtree(self._version_dir)
        if self._tmp_dir.exists():
            shutil.rmtree(self._tmp_dir, ignore_errors=True)
        return removed

    def __repr__(self) -> str:
        return f"TypedArtifactCache({str(self.directory)!r})"


__all__ = ["CacheStats", "TypedArtifactCache"]
