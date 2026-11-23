#! /usr/bin/env python

"""Typed module artifacts and the link-time loader (v9, design 19).

A v9 artifact is one compiled typed core module plus its export/import
surface and an artifact-level constructor table. Artifacts never store host
paths: the module id is a relative POSIX path, ADT origins are rewritten to
it, and position tables use it as the filename.

``NEW_ADT`` operands index the artifact's constructor table. The loader
resolves each entry to a merged declaration/constructor pair, patches the
operand to a flat global id, merges ADT declarations, remaps ``DEF_FUN``
function ids, and produces one ``TypedProgram`` for the typed VM.
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
    ConstructorRef,
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
    from .typed_cache import TypedArtifactCache

ARTIFACT_VERSION = 9
ABI_VERSION = 1
LINKED_KIND = 2
LINKED_VERSION = 2
_LINKED_FILENAME = "<linked>"

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
    constructors: tuple[ConstructorRef, ...]
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


def _normalize_decl(decl: AdtDecl, module_id: str, origins: Mapping[str, str]) -> AdtDecl:
    return dataclasses.replace(
        decl,
        origin=_artifact_origin(decl.origin, module_id, origins),
        constructors=tuple(
            dataclasses.replace(
                constructor,
                payload=tuple(_normalize_type(t, module_id, origins) for t in constructor.payload),
            )
            for constructor in decl.constructors
        ),
    )


def _normalize_constructor_ref(
    ref: ConstructorRef, module_id: str, origins: Mapping[str, str]
) -> ConstructorRef:
    return dataclasses.replace(
        ref,
        origin=_artifact_origin(ref.origin, module_id, origins),
        payload=tuple(_normalize_type(t, module_id, origins) for t in ref.payload),
    )


def _module_constructor_refs(module: TypedModule) -> tuple[ConstructorRef, ...]:
    if module.constructors:
        return module.constructors
    return tuple(
        ConstructorRef(
            decl.origin, decl.name, constructor.name, constructor.arity, constructor.payload
        )
        for decl in module.adt_decls
        for constructor in decl.constructors
    )


def _normalize_module(
    module: TypedModule,
    module_id: str,
    origins: Mapping[str, str],
) -> TypedModule:
    decls: list[AdtDecl] = []
    seen: set[tuple[str, str]] = set()
    for decl in (*module.adt_decls, *module.external_decls):
        normalized = _normalize_decl(decl, module_id, origins)
        key = (normalized.origin, normalized.name)
        if key in seen:
            continue
        seen.add(key)
        decls.append(normalized)
    return TypedModule(
        main=_normalize_function(module.main, module_id, origins),
        functions=tuple(
            _normalize_function(function, module_id, origins) for function in module.functions
        ),
        adt_decls=tuple(decls),
        constructors=tuple(
            _normalize_constructor_ref(ref, module_id, origins)
            for ref in _module_constructor_refs(module)
        ),
    )


def _is_absolute_module_id(module_id: str) -> bool:
    if module_id.startswith(("/", "\\")):
        return True
    if len(module_id) >= 2 and module_id[1] == ":":
        return True
    return Path(module_id).is_absolute()


def _type_key(ir_type: IrTypeLike) -> str:
    if isinstance(ir_type, AdtType):
        args = ",".join(_type_key(argument) for argument in ir_type.args)
        return f"{ir_type.origin}::{ir_type.name}[{args}]"
    if isinstance(ir_type, ContainerType):
        args = ",".join(_type_key(argument) for argument in ir_type.args)
        return f"{ir_type.kind}[{args}]"
    return str(ir_type)


def _fnv1a(text: str) -> int:
    value = 0xCBF29CE484222325
    for byte in text.encode("utf-8"):
        value ^= byte
        value = (value * 0x100000001B3) & 0x7FFFFFFFFFFFFFFF
    return value


def _function_abi(proto: TypedProto) -> int:
    params = ",".join(_type_key(proto.types[index]) for index in proto.param_types)
    returns = _type_key(proto.types[proto.ret_type])
    return _fnv1a(f"fn({params})->{returns}")


def _adt_abi(decl: AdtDecl) -> int:
    constructors = "|".join(
        f"{constructor.name}({','.join(_type_key(t) for t in constructor.payload)})"
        for constructor in decl.constructors
    )
    return _fnv1a(f"adt:{decl.name}({constructors})")


def _constructor_ref_abi(ref: ConstructorRef) -> int:
    payload = ",".join(_type_key(t) for t in ref.payload)
    return _fnv1a(f"ctor:{ref.adt_name}.{ref.name}({payload})#{ref.arity}")


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
        exports.append(TypedExport("function", proto.name, index, abi_hash=_function_abi(proto)))
    for decl_index, decl in enumerate(program.adt_decls):
        if decl.origin == unit.module_id:
            exports.append(TypedExport("adt", decl.name, decl_index, abi_hash=_adt_abi(decl)))
    for symbol, ref in enumerate(module.constructors):
        if ref.origin == unit.module_id:
            exports.append(
                TypedExport(
                    "constructor",
                    ref.name,
                    symbol,
                    adt_name=ref.adt_name,
                    abi_hash=_constructor_ref_abi(ref),
                )
            )

    imports = tuple(TypedImport(ref.module_id, ref.kind, ref.name) for ref in unit.imports)
    artifact = TypedArtifact(
        unit.module_id,
        ABI_VERSION,
        tuple(exports),
        imports,
        module.constructors,
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


def _find_export(artifact: TypedArtifact, kind: str, name: str) -> TypedExport | None:
    for export in artifact.exports:
        if (export.kind, export.name) == (kind, name):
            return export
    return None


def module_abi_hash(artifact: TypedArtifact) -> int:
    """Hash all exports so namespace imports notice any interface change."""

    entries = sorted((export.kind, export.name, export.abi_hash) for export in artifact.exports)
    return _fnv1a("\n".join(f"{kind}:{name}:{abi}" for kind, name, abi in entries))


def _validate_artifact(artifact: TypedArtifact) -> None:
    if not artifact.module_id:
        raise ObcError("typed artifact has an empty module id")
    if _is_absolute_module_id(artifact.module_id):
        raise ObcError(f"typed artifact module id must be relative: {artifact.module_id!r}")
    if artifact.abi_version != ABI_VERSION:
        raise ObcError(f"unsupported typed module ABI version {artifact.abi_version}")

    functions = artifact.program.functions
    decls = artifact.program.adt_decls
    constructors = artifact.constructors
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
            if export.symbol >= len(constructors):
                raise ObcError(f"typed constructor export {export.name!r} has a bad symbol")
            ref = constructors[export.symbol]
            if (ref.adt_name, ref.name) != (export.adt_name, export.name):
                raise ObcError(f"typed constructor export {export.name!r} has a bad symbol")

    seen_constructors: set[tuple[str, str, str]] = set()
    for ref in constructors:
        if _is_absolute_module_id(ref.origin) and ref.origin != CORE_PRELUDE_ORIGIN:
            raise ObcError(f"typed constructor names an absolute module id: {ref.origin!r}")
        constructor_key = (ref.origin, ref.adt_name, ref.name)
        if constructor_key in seen_constructors:
            raise ObcError(f"duplicate typed constructor {ref.origin}::{ref.adt_name}::{ref.name}")
        seen_constructors.add(constructor_key)

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


def _merged_decls(artifacts: Sequence[TypedArtifact]) -> tuple[AdtDecl, ...]:
    merged: list[AdtDecl] = []
    index: dict[tuple[str, str], int] = {}
    for artifact in artifacts:
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
    return tuple(merged)


def _constructor_maps(
    artifacts: Sequence[TypedArtifact],
    merged: tuple[AdtDecl, ...],
) -> dict[str, dict[int, int]]:
    decl_by_key = {(decl.origin, decl.name): decl for decl in merged}
    bases: dict[tuple[str, str], int] = {}
    offset = 0
    for decl in merged:
        bases[(decl.origin, decl.name)] = offset
        offset += len(decl.constructors)

    maps: dict[str, dict[int, int]] = {}
    for artifact in artifacts:
        mapping: dict[int, int] = {}
        for local, ref in enumerate(artifact.constructors):
            key = (ref.origin, ref.adt_name)
            target_decl = decl_by_key.get(key)
            if target_decl is None:
                raise UnsupportedSyntax(
                    f"Typed constructor '{ref.name}' refers to missing ADT "
                    f"'{ref.origin}::{ref.adt_name}'.",
                    _artifact_position(artifact),
                )
            ctor_index = next(
                (
                    index
                    for index, constructor in enumerate(target_decl.constructors)
                    if constructor.name == ref.name
                ),
                None,
            )
            if ctor_index is None:
                raise UnsupportedSyntax(
                    f"Typed constructor '{ref.name}' is missing from "
                    f"'{ref.origin}::{ref.adt_name}'.",
                    _artifact_position(artifact),
                )
            mapping[local] = bases[key] + ctor_index
        maps[artifact.module_id] = mapping
    return maps


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
            if import_.expected_abi_hash:
                if import_.kind == "module":
                    actual = module_abi_hash(dependency)
                else:
                    export = _find_export(dependency, import_.kind, import_.name)
                    assert export is not None
                    actual = export.abi_hash
                if import_.expected_abi_hash != actual:
                    raise UnsupportedSyntax(
                        f"Typed ABI hash mismatch for {import_.kind} "
                        f"'{dependency.module_id}::{import_.name}'.",
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
    merged_decls = _merged_decls(order)
    constructor_maps = _constructor_maps(order, merged_decls)

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


def _pin_imports(
    artifact: TypedArtifact,
    modules: Mapping[str, TypedArtifact],
) -> tuple[TypedArtifact, bool]:
    imports: list[TypedImport] = []
    stale = False
    for import_ in artifact.imports:
        dependency = modules.get(import_.module_id)
        if dependency is None:
            imports.append(import_)
            continue
        if import_.kind == "module":
            expected = module_abi_hash(dependency)
        else:
            export = _find_export(dependency, import_.kind, import_.name)
            if export is None:
                imports.append(import_)
                continue
            expected = export.abi_hash
        if import_.expected_abi_hash and import_.expected_abi_hash != expected:
            stale = True
        imports.append(dataclasses.replace(import_, expected_abi_hash=expected))
    return dataclasses.replace(artifact, imports=tuple(imports)), stale


def build_typed_artifacts(
    units: Sequence[TypedUnit],
    cache: TypedArtifactCache | None = None,
) -> tuple[TypedArtifact, dict[str, TypedArtifact]]:
    """Build all unit artifacts and pin import hashes; root artifact first."""

    origins = _origin_map(units)
    modules: dict[str, TypedArtifact] = {}
    for unit in units:
        dependencies = {
            ref.module_id: module_abi_hash(modules[ref.module_id])
            for ref in unit.imports
            if ref.module_id in modules
        }
        artifact: TypedArtifact | None = None
        if cache is not None:
            artifact = cache.load(unit, dependencies)
            if artifact is not None:
                artifact, stale = _pin_imports(artifact, modules)
                if stale:
                    artifact = None
        if artifact is None:
            if cache is None:
                artifact = build_typed_artifact(unit, origins)
                artifact, _ = _pin_imports(artifact, modules)
            else:
                with cache.entry_lock(unit, dependencies):
                    artifact = cache.load(unit, dependencies)
                    if artifact is not None:
                        artifact, stale = _pin_imports(artifact, modules)
                        if stale:
                            artifact = None
                    if artifact is None:
                        artifact = build_typed_artifact(unit, origins)
                        artifact, _ = _pin_imports(artifact, modules)
                        cache.store(unit, artifact, dependencies)

        if artifact.module_id in modules:
            raise UnsupportedSyntax(
                f"Duplicate typed module id '{artifact.module_id}'.",
                _artifact_position(artifact),
            )
        modules[artifact.module_id] = artifact
    return modules[units[-1].module_id], modules


def build_typed_program(
    units: Sequence[TypedUnit],
    cache: TypedArtifactCache | None = None,
) -> TypedProgram:
    """Compile typed units (dependencies first) and link their artifacts."""

    root, modules = build_typed_artifacts(units, cache)
    return link_typed_artifacts(root, modules)


def build_typed_program_exports(
    units: Sequence[TypedUnit],
    cache: TypedArtifactCache | None = None,
) -> tuple[TypedProgram, tuple[str, ...]]:
    """Link units and return the root module's exported function names."""

    root, modules = build_typed_artifacts(units, cache)
    program = link_typed_artifacts(root, modules)
    names = tuple(export.name for export in root.exports if export.kind == "function")
    return program, names


# ----------------------------------------------------------------------
# v9 serialization
# ----------------------------------------------------------------------


def write_typed_artifact(artifact: TypedArtifact, path: str | Path) -> None:
    """Serialize a typed module artifact as a kind=1 v9 file."""

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

    w.u32(len(artifact.constructors))
    for ref in artifact.constructors:
        w.string(ref.origin)
        w.string(ref.adt_name)
        w.string(ref.name)
        w.u16(ref.arity)

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
    """Read a kind=1 v9 typed module artifact."""

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

    constructors: list[ConstructorRef] = []
    for _ in range(r.u32()):
        constructors.append(ConstructorRef(r.string(), r.string(), r.string(), r.u16()))

    adt_decls: list[AdtDecl] = []
    for _ in range(r.u32()):
        origin = r.string()
        name = r.string()
        decl_constructors = []
        for _ in range(r.u16()):
            constructor_name = r.string()
            arity = r.u8()
            decl_constructors.append(AdtConstructor(constructor_name, arity=arity))
        adt_decls.append(AdtDecl(origin, name, tuple(decl_constructors)))
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
        tuple(constructors),
        TypedProgram(main=main, functions=functions, adt_decls=decls),
    )
    _validate_artifact(artifact)
    return artifact


# ----------------------------------------------------------------------
# Linked bundles (kind=2)
# ----------------------------------------------------------------------


def _flat_constructor_refs(program: TypedProgram) -> tuple[ConstructorRef, ...]:
    return tuple(
        ConstructorRef(decl.origin, decl.name, constructor.name, constructor.arity)
        for decl in program.adt_decls
        for constructor in decl.constructors
    )


def write_linked_bundle(program: TypedProgram, path: str | Path) -> None:
    """Serialize a linked typed program as a path-free kind=2 bundle."""

    refs = _flat_constructor_refs(program)
    w = _Writer()
    w._buf += MAGIC
    w.u8(LINKED_KIND)
    w.u8(LINKED_VERSION)
    w.u16(ABI_VERSION)

    decls = program.adt_decls
    w.u32(len(decls))
    for decl in decls:
        w.string(decl.origin)
        w.string(decl.name)
        w.u16(len(decl.constructors))
        for constructor in decl.constructors:
            w.string(constructor.name)
            w.u8(constructor.arity)

    w.u32(len(refs))
    for ref in refs:
        w.string(ref.origin)
        w.string(ref.adt_name)
        w.string(ref.name)
        w.u16(ref.arity)

    adt_index = {(decl.origin, decl.name): index for index, decl in enumerate(decls)}
    w.u32(len(program.functions))
    for proto in program.functions:
        _write_proto(w, proto, adt_index, filename=_LINKED_FILENAME)
    _write_proto(w, program.main, adt_index, filename=_LINKED_FILENAME)
    Path(path).write_bytes(w.bytes())


def read_linked_bundle(path: str | Path) -> TypedProgram:
    """Read a kind=2 linked bundle and validate its constructor table."""

    data = Path(path).read_bytes()
    if not data.startswith(MAGIC):
        raise ObcError("not an OBC file")
    if len(data) < 5:
        raise ObcError("truncated OBC header")
    kind = data[3]
    version = data[4]
    if kind != LINKED_KIND:
        raise ObcError(f"expected linked typed bundle (kind=2), got kind={kind}")
    if version != LINKED_VERSION:
        raise ObcError(f"unsupported linked bundle version {version}")

    r = _Reader(data[5:])
    abi_version = r.u16()
    if abi_version != ABI_VERSION:
        raise ObcError(f"unsupported linked bundle ABI version {abi_version}")

    adt_decls: list[AdtDecl] = []
    for _ in range(r.u32()):
        origin = r.string()
        name = r.string()
        constructors = []
        for _ in range(r.u16()):
            constructors.append(AdtConstructor(r.string(), arity=r.u8()))
        adt_decls.append(AdtDecl(origin, name, tuple(constructors)))
    decls = tuple(adt_decls)

    table = []
    for _ in range(r.u32()):
        table.append(ConstructorRef(r.string(), r.string(), r.string(), r.u16()))
    expected = tuple(
        ConstructorRef(decl.origin, decl.name, constructor.name, constructor.arity)
        for decl in decls
        for constructor in decl.constructors
    )
    if tuple(table) != expected:
        raise ObcError("linked bundle constructor table does not match its declarations")

    functions = tuple(_read_proto(r, decls) for _ in range(r.u32()))
    main = _read_proto(r, decls)
    if r._pos != len(r._data):
        raise ObcError("trailing bytes in linked bundle")
    return TypedProgram(main=main, functions=functions, adt_decls=decls)


__all__ = [
    "ABI_VERSION",
    "ARTIFACT_VERSION",
    "LINKED_KIND",
    "LINKED_VERSION",
    "TypedArtifact",
    "TypedExport",
    "TypedImport",
    "build_typed_artifact",
    "build_typed_artifacts",
    "build_typed_program",
    "build_typed_program_exports",
    "link_typed_artifacts",
    "read_linked_bundle",
    "read_typed_artifact",
    "write_linked_bundle",
    "write_typed_artifact",
]
