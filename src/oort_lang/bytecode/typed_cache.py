#! /usr/bin/env python

"""On-disk cache for typed module artifacts (P1c-3).

Cache entries are keyed by source bytes, module id, compiler version and the
artifact/ABI versions. A cached artifact whose pinned import hashes no longer
match its dependencies is rebuilt; the loader keeps rejecting genuinely
incompatible artifacts.
"""

from __future__ import annotations

import hashlib
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
    from ..hir.typed_link import TypedUnit


class TypedArtifactCache:
    """A directory of v8 artifacts keyed by source content."""

    def __init__(self, directory: str | Path):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def _key(self, unit: TypedUnit) -> str | None:
        if unit.path is None:
            return None
        source = unit.path.read_bytes()
        digest = hashlib.sha256()
        digest.update(source)
        digest.update(b"\0")
        digest.update(unit.module_id.encode("utf-8"))
        digest.update(b"\0")
        digest.update(__version__.encode("utf-8"))
        digest.update(b"\0")
        digest.update(str(ARTIFACT_VERSION).encode("ascii"))
        digest.update(b"\0")
        digest.update(str(ABI_VERSION).encode("ascii"))
        return digest.hexdigest()

    def path_for(self, unit: TypedUnit) -> Path | None:
        key = self._key(unit)
        return None if key is None else self.directory / f"{key}.obc"

    def load(self, unit: TypedUnit) -> TypedArtifact | None:
        path = self.path_for(unit)
        if path is None or not path.exists():
            return None
        try:
            artifact = read_typed_artifact(path)
        except (ObcError, OSError):
            return None
        if artifact.module_id != unit.module_id:
            return None
        return artifact

    def store(self, unit: TypedUnit, artifact: TypedArtifact) -> None:
        path = self.path_for(unit)
        if path is None:
            return
        temporary = path.with_suffix(".tmp")
        write_typed_artifact(artifact, temporary)
        temporary.replace(path)

    def __repr__(self) -> str:
        return f"TypedArtifactCache({str(self.directory)!r})"


__all__ = ["TypedArtifactCache"]
