#! /usr/bin/env python

"""Serialization of typed bytecode (``.obc`` kind=1, design 15).

Version 6 stores a module-level ADT declaration table plus a per-proto type
table: register/param/return types are type-table indices, composite types
reference earlier entries, and ADT types reference module declarations. The
table only describes static types; values remain runtime values.
"""

from __future__ import annotations

from pathlib import Path

from ..hir.typed import (
    AdtConstructor,
    AdtDecl,
    AdtType,
    ContainerType,
    IrType,
    IrTypeLike,
    ir_type_tag,
    list_type,
    tuple_type,
)
from ..source.source_position import SourcePosition
from .serialize import MAGIC, ObcError, _read_constant, _Reader, _write_constant, _Writer
from .typed_compile import TypedProgram, TypedProto

KIND_TYPED = 1
VERSION = 6

_SCALAR_BY_TAG = {
    1: IrType.INT,
    2: IrType.FLOAT,
    3: IrType.BOOL,
    4: IrType.UNIT,
    5: IrType.FUNCTION,
    6: IrType.STRING,
    11: IrType.ITERATOR,
}


def _write_type_table(
    w: _Writer,
    types: tuple[IrTypeLike, ...],
    adt_index: dict[tuple[str, str], int],
) -> None:
    w.u16(len(types))
    index = {ir_type: position for position, ir_type in enumerate(types)}
    for ir_type in types:
        w.u8(ir_type_tag(ir_type))
        if isinstance(ir_type, ContainerType):
            if ir_type.kind in ("List", "Set"):
                w.u16(index[ir_type.args[0]])
            elif ir_type.kind == "Dict":
                w.u16(index[ir_type.args[0]])
                w.u16(index[ir_type.args[1]])
            elif ir_type.kind == "Tuple":
                w.u16(len(ir_type.args))
                for arg in ir_type.args:
                    w.u16(index[arg])
            else:
                raise ObcError(f"unsupported container type {ir_type.kind}")
        elif isinstance(ir_type, AdtType):
            try:
                w.u16(adt_index[(ir_type.origin, ir_type.name)])
            except KeyError as exc:
                raise ObcError(f"unknown ADT type {ir_type}") from exc
            w.u16(len(ir_type.args))
            for argument in ir_type.args:
                w.u16(index[argument])


def _write_type_id(w: _Writer, type_id: int | None) -> None:
    w.u16(0 if type_id is None else type_id + 1)


def _write_proto(
    w: _Writer,
    proto: TypedProto,
    adt_index: dict[tuple[str, str], int],
    filename: str | None = None,
) -> None:
    w.string(proto.name)
    w.boolean(proto.is_main)
    _write_type_table(w, proto.types, adt_index)
    w.u16(proto.register_count)
    for type_id in proto.register_types:
        _write_type_id(w, type_id)
    w.u8(len(proto.param_types))
    for type_id in proto.param_types:
        _write_type_id(w, type_id)
    _write_type_id(w, proto.ret_type)
    w.u32(len(proto.code))
    for word in proto.code:
        w.u32(word)
    w.u32(len(proto.constants))
    for constant in proto.constants:
        _write_constant(w, constant)
    w.boolean(bool(proto.positions))
    if proto.positions:
        w.string(filename if filename is not None else proto.positions[0].filename)
        w.u32(len(proto.positions))
        for position in proto.positions:
            w.u32(position.start_line)
            column = position.start_column
            w.i32(-1 if column is None else column)


def _read_type_table(
    r: _Reader,
    proto_name: str,
    adt_decls: tuple[AdtDecl, ...],
) -> tuple[IrTypeLike, ...]:
    count = r.u16()
    types: list[IrTypeLike] = []
    for position in range(count):
        tag = r.u8()
        if tag in _SCALAR_BY_TAG:
            types.append(_SCALAR_BY_TAG[tag])
            continue
        if tag in (7, 8):
            child = r.u16()
            if child >= len(types):
                raise ObcError(f"typed proto {proto_name!r} has a forward type reference")
            factory = list_type if tag == 7 else (lambda element: ContainerType("Set", (element,)))
            types.append(factory(types[child]))
            continue
        if tag == 9:
            key = r.u16()
            value = r.u16()
            if key >= len(types) or value >= len(types):
                raise ObcError(f"typed proto {proto_name!r} has a forward type reference")
            types.append(ContainerType("Dict", (types[key], types[value])))
            continue
        if tag == 12:
            decl_id = r.u16()
            if decl_id >= len(adt_decls):
                raise ObcError(f"typed proto {proto_name!r} has an unknown ADT declaration")
            arguments = []
            for _ in range(r.u16()):
                child = r.u16()
                if child >= len(types):
                    raise ObcError(f"typed proto {proto_name!r} has a forward type reference")
                arguments.append(types[child])
            decl = adt_decls[decl_id]
            types.append(AdtType(decl.origin, decl.name, tuple(arguments)))
            continue
        if tag == 10:
            elements = []
            for _ in range(r.u16()):
                child = r.u16()
                if child >= len(types):
                    raise ObcError(f"typed proto {proto_name!r} has a forward type reference")
                elements.append(types[child])
            types.append(tuple_type(*elements))
            continue
        raise ObcError(f"invalid typed type tag {tag} at position {position}")
    return tuple(types)


def _read_type_id(r: _Reader, types: tuple[IrTypeLike, ...], proto_name: str) -> int:
    raw = r.u16()
    if raw == 0:
        raise ObcError(f"typed proto {proto_name!r} references an untyped register")
    type_id = raw - 1
    if type_id >= len(types):
        raise ObcError(f"typed proto {proto_name!r} has an out-of-range type id")
    return type_id


def _read_proto(r: _Reader, adt_decls: tuple[AdtDecl, ...]) -> TypedProto:
    name = r.string()
    is_main = r.boolean()
    types = _read_type_table(r, name, adt_decls)
    register_count = r.u16()
    register_types = tuple(0 if (raw := r.u16()) == 0 else raw - 1 for _ in range(register_count))
    for type_id in register_types:
        if type_id >= len(types):
            raise ObcError(f"typed proto {name!r} has an out-of-range register type")
    params = []
    for _ in range(r.u8()):
        params.append(_read_type_id(r, types, name))
    ret_type = _read_type_id(r, types, name)
    code = tuple(r.u32() for _ in range(r.u32()))
    constants = tuple(_read_constant(r) for _ in range(r.u32()))
    positions: tuple[SourcePosition, ...] = ()
    if r.boolean():
        filename = r.string()
        count = r.u32()
        if count != len(code):
            raise ObcError(f"typed proto {name!r} position table size mismatch")
        rebuilt = []
        for _ in range(count):
            line = r.u32()
            column = r.i32()
            rebuilt.append(
                SourcePosition.from_location(line, max(column, 0), "", filename=filename)
            )
        positions = tuple(rebuilt)
    if not positions:
        positions = tuple(
            SourcePosition.from_location(1, 0, "", filename="<typed-bytecode>") for _ in code
        )
    return TypedProto(
        name=name,
        code=code,
        constants=constants,
        positions=positions,
        register_count=register_count,
        types=types,
        register_types=register_types,
        param_types=tuple(params),
        ret_type=ret_type,
        is_main=is_main,
    )


def write_typed_obc(program: TypedProgram, path: str | Path) -> None:
    """Serialize a typed bytecode program to a kind=1 ``.obc`` file."""

    w = _Writer()
    w._buf += MAGIC
    w.u8(KIND_TYPED)
    w.u8(VERSION)
    w.u32(len(program.adt_decls))
    for decl in program.adt_decls:
        w.string(decl.origin)
        w.string(decl.name)
        w.u16(len(decl.constructors))
        for constructor in decl.constructors:
            w.string(constructor.name)
            w.u8(constructor.arity)
    w.u32(len(program.functions))
    adt_index = {(decl.origin, decl.name): index for index, decl in enumerate(program.adt_decls)}
    for proto in program.functions:
        _write_proto(w, proto, adt_index)
    _write_proto(w, program.main, adt_index)
    Path(path).write_bytes(w.bytes())


def read_typed_obc(path: str | Path) -> TypedProgram:
    """Read a kind=1 ``.obc`` file; reject other kinds and versions."""

    data = Path(path).read_bytes()
    if not data.startswith(MAGIC):
        raise ObcError("not an OBC file")
    if len(data) < 5:
        raise ObcError("truncated OBC header")
    kind = data[3]
    version = data[4]
    if kind != KIND_TYPED:
        raise ObcError(f"expected typed bytecode (kind=1), got kind={kind}")
    if version != VERSION:
        raise ObcError(f"unsupported typed bytecode version {version}")
    r = _Reader(data[5:])
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
    functions = tuple(_read_proto(r, tuple(adt_decls)) for _ in range(r.u32()))
    main = _read_proto(r, tuple(adt_decls))
    if r._pos != len(r._data):
        raise ObcError("trailing bytes in typed bytecode file")
    return TypedProgram(main=main, functions=functions, adt_decls=tuple(adt_decls))


__all__ = ["KIND_TYPED", "read_typed_obc", "write_typed_obc"]
