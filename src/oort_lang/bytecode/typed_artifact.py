#! /usr/bin/env python

"""Typed module artifacts and the link-time loader (v7, design 19).

A v7 artifact is one compiled typed core module plus its export/import
surface. Artifacts never store host paths: the module id is a relative POSIX
path, ADT origins are rewritten to it, and position tables use it as the
filename. The loader validates import/export edges, merges ADT declarations,
remaps constructor and function ids, and produces one ``TypedProgram`` for
the existing typed VM.
"""

from __future__ import annotations

import dataclasses
from pathlib import Path
from typing import TYPE_CHECKING

from ..diagnostics.syntax_errors import UnsupportedSyntax
from ..hir.typed import (
    AdtConstructor,
    AdtDecl,
    AdtType,
    ContainerType,
    IrTypeLike,
    TypedFunction,
    TypedModule,
)
from ..semantics.core.prelude import CORE_PRELUDE_ORIGIN
from ..source.source_position import SourcePosition
from .serialize import MAGIC, ObcError, _Reader, _Writer
from .typed_compile import TypedProgram, TypedProto, compile_typed_module
from .typed_opcodes import (
    TypedOp,
    decode_a,
    decode_b,
    decode_bx,
    decode_c,
    decode_op,
    encode_abc,
    encode_abx,
)
from .typed_serialize import KIND_TYPED, _read_proto, _write_proto

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from ..hir.typed_link import TypedUnit

ARTIFACT_VERSION = 7
ABI_VERSION = 1

_EXPORT_CODES = {"function": 1, "adt": 2, "constructor": 3}
_IMPORT_CODES = {"module": 1, "function": 2, "adt": 3, "constructor": 4}
_EXPORT_KINDS = {value: key for key, value in _EXPORT_CODES.items()}
_IMPORT_KINDS = {value: key for key, value in _IMPORT_CODES.items()}


@dataclasses.dataclass(frozen=True, slots=True)
class TypedExport:
    kind: str  # "function" | "adt" | "constructor"
    name: str
    symbol: int
    adt_name: str = ""
    abi_hash: int = 0


@dataclasses.dataclass(frozen=True, slots=True)
class TypedImport:
    module_id: str
    kind: str  # "module" | "function" | "adt" | "constructor"
    name: str
    expected_abi_hash: int = 0


@dataclasses.dataclass(frozen=True, slots=True)
class TypedArtifact:
    module_id: str
    abi_version: int
    exports: tuple[TypedExport, ...]
    imports: tuple[TypedImport, ...]
    program: TypedProgram


def _origin_map(units: Sequence[TypedUnit]) -> dict[str, str]:
    """Map every module's source origin to its logical module id."""

    mapping: dict[str, str] = {}
    for unit in units:
        for decl in unit.module.adt_decls:
            if decl.origin == CORE_PRELUDE_ORIGIN:
                continue
            mapping.setdefault(decl.origin, unit.module_id)
    return mapping


def _artifact_origin(origin: str, module_id: str, origins: Mapping[str, str]) -> str:
    if origin == CORE_PRELUDE_ORIGIN:
        return origin
    try:
        return origins[origin]
    except KeyError as exc:
        raise UnsupportedSyntax(
            f"Unknown ADT origin {origin!r} in typed module '{module_id}'.",
            SourcePosition.from_location(1, 0, "", filename=module_id),
        ) from exc


def _normalize_type(
    ir_type: IrTypeLike,
    module_id: str,
    origins: Mapping[str, str],
) -> IrTypeLike:
    if isinstance(ir_type, AdtType):
        return AdtType(
            _artifact_origin(ir_type.origin, module_id, origins),
            ir_type.name,
            tuple(_normalize_type(argument, module_id, origins) for argument in ir_type.args),
        )
    if isinstance(ir_type, ContainerType):
        return ContainerType(
            ir_type.kind,
            tuple(_normalize_type(argument, module_id, origins) for argument in ir_type.args),
        )
    return ir_type


def _normalize_function(
    function: TypedFunction,
    module_id: str,
    origins: Mapping[str, str],
) -> TypedFunction:
    return dataclasses.replace(
        function,
        param_types=tuple(_normalize_type(t, module_id, origins) for t in function.param_types),
        ret_type=_normalize_type(function.ret_type, module_id, origins),
        register_types=tuple(
            None if t is None else _normalize_type(t, module_id, origins)
            for t in function.register_types
        ),
    )


def _normalize_module(
    module: TypedModule,
    module_id: str,
    origins: Mapping[str, str],
) -> TypedModule:
    decls = tuple(
        dataclasses.replace(
            decl,
            origin=_artifact_origin(decl.origin, module_id, origins),
            constructors=tuple(
                dataclasses.replace(
                    constructor,
                    payload=tuple(
                        _normalize_type(t, module_id, origins) for t in constructor.payload
                    ),
                )
                for constructor in decl.constructors
            ),
        )
        for decl in module.adt_decls
    )
    return TypedModule(
        main=_normalize_function(module.main, module_id, origins),
        functions=tuple(
            _normalize_function(function, module_id, origins) for function in module.functions
        ),
        adt_decls=decls,
    )


def _is_absolute_module_id(module_id: str) -> bool:
    if module_id.startswith(("/", "\\")):
        return True
    if len(module_id) >= 2 and module_id[1] == ":":
        return True
    return Path(module_id).is_absolute()


def build_typed_artifact(
    unit: TypedUnit,
    origins: Mapping[str, str] | None = None,
) -> TypedArtifact:
    """Compile one typed unit into a path-free module artifact."""

    if _is_absolute_module_id(unit.module_id):
        raise UnsupportedSyntax(
            f"Typed module id must be relative, got {unit.module_id!r}.",
            unit.module.main.hir.position,
        )
    if origins is None:
        origins = _origin_map((unit,))
    module = _normalize_module(unit.module, unit.module_id, origins)
    program = compile_typed_module(module)

    exports: list[TypedExport] = []
    for index, proto in enumerate(program.functions):
        exports.append(TypedExport("function", proto.name, index))
    constructor_id = 0
    for decl_index, decl in enumerate(program.adt_decls):
        exports.append(TypedExport("adt", decl.name, decl_index))
        for constructor in decl.constructors:
            exports.append(
                TypedExport(
                    "constructor",
                    constructor.name,
                    constructor_id,
                    adt_name=decl.name,
                )
            )
            constructor_id += 1

    imports = tuple(TypedImport(ref.module_id, ref.kind, ref.name) for ref in unit.imports)
    artifact = TypedArtifact(
        unit.module_id,
        ABI_VERSION,
        tuple(exports),
        imports,
        program,
    )
    _validate_artifact(artifact)
    return artifact


def _artifact_position(artifact: TypedArtifact) -> SourcePosition:
    if artifact.program.main.positions:
        return artifact.program.main.positions[0]
    return SourcePosition.from_location(1, 0, "", filename=artifact.module_id)


def _export_keys(artifact: TypedArtifact) -> set[tuple[str, str]]:
    return {(export.kind, export.name) for export in artifact.exports}


def _constructor_owner(artifact: TypedArtifact, symbol: int) -> tuple[str, str] | None:
    offset = 0
    for decl in artifact.program.adt_decls:
        for constructor in decl.constructors:
            if offset == symbol:
                return decl.name, constructor.name
            offset += 1
    return None


def _validate_artifact(artifact: TypedArtifact) -> None:
    if not artifact.module_id:
        raise ObcError("typed artifact has an empty module id")
    if _is_absolute_module_id(artifact.module_id):
        raise ObcError(f"typed artifact module id must be relative: {artifact.module_id!r}")
    if artifact.abi_version != ABI_VERSION:
        raise ObcError(f"unsupported typed module ABI version {artifact.abi_version}")

    functions = artifact.program.functions
    decls = artifact.program.adt_decls
    seen: set[tuple[str, str]] = set()
    for export in artifact.exports:
        if export.kind not in _EXPORT_CODES:
            raise ObcError(f"invalid typed export kind {export.kind!r}")
        key = (export.kind, export.name)
        if key in seen:
            raise ObcError(f"duplicate typed export {export.kind} {export.name!r}")
        seen.add(key)
        if export.kind == "function":
            if export.symbol >= len(functions) or functions[export.symbol].name != export.name:
                raise ObcError(f"typed function export {export.name!r} has a bad symbol")
            if export.adt_name:
                raise ObcError(f"typed function export {export.name!r} has an ADT name")
        elif export.kind == "adt":
            if export.symbol >= len(decls) or decls[export.symbol].name != export.name:
                raise ObcError(f"typed ADT export {export.name!r} has a bad symbol")
        else:
            owner = _constructor_owner(artifact, export.symbol)
            if owner is None or owner != (export.adt_name, export.name):
                raise ObcError(f"typed constructor export {export.name!r} has a bad symbol")

    seen_imports: set[tuple[str, str, str]] = set()
    for import_ in artifact.imports:
        if import_.kind not in _IMPORT_CODES:
            raise ObcError(f"invalid typed import kind {import_.kind!r}")
        if _is_absolute_module_id(import_.module_id):
            raise ObcError(f"typed import names an absolute module id: {import_.module_id!r}")
        import_key = (import_.module_id, import_.kind, import_.name)
        if import_key in seen_imports:
            raise ObcError(f"duplicate typed import {import_.module_id}::{import_.name}")
        seen_imports.add(import_key)


def _rewrite_proto(
    proto: TypedProto,
    constructor_map: dict[int, int],
    function_map: dict[int, int] | None = None,
) -> TypedProto:
    code: list[int] = []
    for word in proto.code:
        op = decode_op(word)
        if op is TypedOp.NEW_ADT:
            local = decode_b(word)
            if local not in constructor_map:
                raise UnsupportedSyntax(
                    f"Typed bytecode references unknown constructor id {local}.",
                    proto.positions[0],
                )
            word = encode_abc(op, decode_a(word), constructor_map[local], decode_c(word))
        elif op is TypedOp.DEF_FUN and function_map is not None:
            local = decode_bx(word)
            if local not in function_map:
                raise UnsupportedSyntax(
                    f"Typed bytecode defines unknown function id {local}.",
                    proto.positions[0],
                )
            word = encode_abx(op, decode_a(word), function_map[local])
        code.append(word)
    return dataclasses.replace(proto, code=tuple(code))


def _constructor_maps(
    units: Sequence[TypedArtifact],
) -> tuple[tuple[AdtDecl, ...], dict[str, dict[int, int]]]:
    merged: list[AdtDecl] = []
    index: dict[tuple[str, str], int] = {}
    for artifact in units:
        for decl in artifact.program.adt_decls:
            key = (decl.origin, decl.name)
            existing = index.get(key)
            if existing is not None:
                if merged[existing].constructors != decl.constructors:
                    raise UnsupportedSyntax(
                        f"Typed ADT '{decl.name}' from '{decl.origin}' has conflicting definitions.",
                        _artifact_position(artifact),
                    )
                continue
            index[key] = len(merged)
            merged.append(decl)

    bases: dict[tuple[str, str], int] = {}
    offset = 0
    for decl in merged:
        bases[(decl.origin, decl.name)] = offset
        offset += len(decl.constructors)

    maps: dict[str, dict[int, int]] = {}
    for artifact in units:
        mapping: dict[int, int] = {}
        local = 0
        for decl in artifact.program.adt_decls:
            base = bases[(decl.origin, decl.name)]
            for constructor_index in range(len(decl.constructors)):
                mapping[local] = base + constructor_index
                local += 1
        maps[artifact.module_id] = mapping
    return tuple(merged), maps


def _dependency_order(
    root: TypedArtifact,
    modules: Mapping[str, TypedArtifact],
) -> list[TypedArtifact]:
    order: list[TypedArtifact] = []
    state: dict[str, int] = {}

    def visit(artifact: TypedArtifact) -> None:
        status = state.get(artifact.module_id, 0)
        if status == 1:
            raise UnsupportedSyntax(
                f"Circular typed module import involving '{artifact.module_id}'.",
                _artifact_position(artifact),
            )
        if status == 2:
            return
        state[artifact.module_id] = 1
        for import_ in artifact.imports:
            dependency = modules.get(import_.module_id)
            if dependency is None:
                raise UnsupportedSyntax(
                    f"Typed module '{artifact.module_id}' imports missing module "
                    f"'{import_.module_id}'.",
                    _artifact_position(artifact),
                )
            if import_.kind != "module" and (import_.kind, import_.name) not in _export_keys(
                dependency
            ):
                raise UnsupportedSyntax(
                    f"Typed module '{dependency.module_id}' does not export "
                    f"{import_.kind} '{import_.name}'.",
                    _artifact_position(artifact),
                )
            visit(dependency)
        state[artifact.module_id] = 2
        order.append(artifact)

    visit(root)
    return order


def link_typed_artifacts(
    root: TypedArtifact,
    modules: Mapping[str, TypedArtifact],
) -> TypedProgram:
    """Validate import edges and link artifacts into one typed program."""

    table = dict(modules)
    table[root.module_id] = root
    order = _dependency_order(root, table)
    merged_decls, constructor_maps = _constructor_maps(order)

    functions: list[TypedProto] = []
    function_maps: dict[str, dict[int, int]] = {}
    owners: dict[str, str] = {}
    # Root functions first, matching the in-memory linker.
    for artifact in [order[-1], *order[:-1]]:
        mapping = constructor_maps[artifact.module_id]
        function_map: dict[int, int] = {}
        for index, proto in enumerate(artifact.program.functions):
            if proto.name in owners:
                raise UnsupportedSyntax(
                    f"Typed function name collision: '{proto.name}' in "
                    f"'{owners[proto.name]}' and '{artifact.module_id}'.",
                    proto.positions[0],
                )
            owners[proto.name] = artifact.module_id
            function_map[index] = len(functions)
            functions.append(_rewrite_proto(proto, mapping))
        function_maps[artifact.module_id] = function_map

    root_artifact = order[-1]
    main = _rewrite_proto(
        root_artifact.program.main,
        constructor_maps[root_artifact.module_id],
        function_maps[root_artifact.module_id],
    )
    return TypedProgram(main=main, functions=tuple(functions), adt_decls=merged_decls)


def build_typed_program(units: Sequence[TypedUnit]) -> TypedProgram:
    """Compile typed units (dependencies first) and link their artifacts."""

    origins = _origin_map(units)
    artifacts = [build_typed_artifact(unit, origins) for unit in units]
    modules: dict[str, TypedArtifact] = {}
    for artifact in artifacts:
        if artifact.module_id in modules:
            raise UnsupportedSyntax(
                f"Duplicate typed module id '{artifact.module_id}'.",
                _artifact_position(artifact),
            )
        modules[artifact.module_id] = artifact
    return link_typed_artifacts(artifacts[-1], modules)


# ----------------------------------------------------------------------
# v7 serialization
# ----------------------------------------------------------------------


def write_typed_artifact(artifact: TypedArtifact, path: str | Path) -> None:
    """Serialize a typed module artifact as a kind=1 v7 file."""

    _validate_artifact(artifact)
    w = _Writer()
    w._buf += MAGIC
    w.u8(KIND_TYPED)
    w.u8(ARTIFACT_VERSION)
    w.string(artifact.module_id)
    w.u16(artifact.abi_version)

    w.u32(len(artifact.exports))
    for export in artifact.exports:
        w.u8(_EXPORT_CODES[export.kind])
        w.string(export.name)
        w.string(export.adt_name)
        w.u32(export.symbol)
        w.i64(export.abi_hash)

    w.u32(len(artifact.imports))
    for import_ in artifact.imports:
        w.string(import_.module_id)
        w.u8(_IMPORT_CODES[import_.kind])
        w.string(import_.name)
        w.i64(import_.expected_abi_hash)

    decls = artifact.program.adt_decls
    w.u32(len(decls))
    for decl in decls:
        w.string(decl.origin)
        w.string(decl.name)
        w.u16(len(decl.constructors))
        for constructor in decl.constructors:
            w.string(constructor.name)
            w.u8(constructor.arity)

    adt_index = {(decl.origin, decl.name): index for index, decl in enumerate(decls)}
    functions = artifact.program.functions
    w.u32(len(functions))
    for proto in functions:
        _write_proto(w, proto, adt_index, filename=artifact.module_id)
    _write_proto(w, artifact.program.main, adt_index, filename=artifact.module_id)
    Path(path).write_bytes(w.bytes())


def read_typed_artifact(path: str | Path) -> TypedArtifact:
    """Read a kind=1 v7 typed module artifact."""

    data = Path(path).read_bytes()
    if not data.startswith(MAGIC):
        raise ObcError("not an OBC file")
    if len(data) < 5:
        raise ObcError("truncated OBC header")
    kind = data[3]
    version = data[4]
    if kind != KIND_TYPED:
        raise ObcError(f"expected typed bytecode (kind=1), got kind={kind}")
    if version != ARTIFACT_VERSION:
        raise ObcError(f"unsupported typed module artifact version {version}")

    r = _Reader(data[5:])
    module_id = r.string()
    abi_version = r.u16()

    exports: list[TypedExport] = []
    for _ in range(r.u32()):
        code = r.u8()
        if code not in _EXPORT_KINDS:
            raise ObcError(f"invalid typed export code {code}")
        kind_name = _EXPORT_KINDS[code]
        name = r.string()
        adt_name = r.string()
        symbol = r.u32()
        abi_hash = r.i64()
        exports.append(TypedExport(kind_name, name, symbol, adt_name=adt_name, abi_hash=abi_hash))

    imports: list[TypedImport] = []
    for _ in range(r.u32()):
        import_module = r.string()
        code = r.u8()
        if code not in _IMPORT_KINDS:
            raise ObcError(f"invalid typed import code {code}")
        imports.append(
            TypedImport(
                import_module,
                _IMPORT_KINDS[code],
                r.string(),
                expected_abi_hash=r.i64(),
            )
        )

    adt_decls: list[AdtDecl] = []
    for _ in range(r.u32()):
        origin = r.string()
        name = r.string()
        constructors = []
        for _ in range(r.u16()):
            constructor_name = r.string()
            arity = r.u8()
            constructors.append(AdtConstructor(constructor_name, arity=arity))
        adt_decls.append(AdtDecl(origin, name, tuple(constructors)))
    decls = tuple(adt_decls)

    functions = tuple(_read_proto(r, decls) for _ in range(r.u32()))
    main = _read_proto(r, decls)
    if r._pos != len(r._data):
        raise ObcError("trailing bytes in typed module artifact")

    artifact = TypedArtifact(
        module_id,
        abi_version,
        tuple(exports),
        tuple(imports),
        TypedProgram(main=main, functions=functions, adt_decls=decls),
    )
    _validate_artifact(artifact)
    return artifact


__all__ = [
    "ABI_VERSION",
    "ARTIFACT_VERSION",
    "TypedArtifact",
    "TypedExport",
    "TypedImport",
    "build_typed_artifact",
    "build_typed_program",
    "link_typed_artifacts",
    "read_typed_artifact",
    "write_typed_artifact",
]
