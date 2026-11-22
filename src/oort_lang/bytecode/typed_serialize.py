#! /usr/bin/env python

"""Serialization of typed bytecode (``.obc`` kind=1, design 15 M3).

The container reuses the dynamic ``.obc`` primitives (magic, little-endian
writer/reader, tagged simple constants) but has its own kind and payload:
typed protos carry register types, parameter/return types and typed words.
Kind 0 readers and kind 1 readers must reject each other explicitly.
"""

from __future__ import annotations

from pathlib import Path

from ..hir.typed import IrType
from ..source.source_position import SourcePosition
from .serialize import MAGIC, ObcError, _read_constant, _Reader, _write_constant, _Writer
from .typed_compile import TypedProgram, TypedProto

KIND_TYPED = 1
VERSION = 3

_IR_TO_INDEX = {
    None: 0,
    IrType.INT: 1,
    IrType.FLOAT: 2,
    IrType.BOOL: 3,
    IrType.UNIT: 4,
    IrType.FUNCTION: 5,
    IrType.STRING: 6,
}
_INDEX_TO_IR = {index: ir_type for ir_type, index in _IR_TO_INDEX.items()}


def _write_ir_type(w: _Writer, ir_type: IrType | None) -> None:
    w.u8(_IR_TO_INDEX[ir_type])


def _read_ir_type(r: _Reader) -> IrType | None:
    index = r.u8()
    try:
        return _INDEX_TO_IR[index]
    except KeyError as exc:
        raise ObcError(f"invalid typed register type tag {index}") from exc


def _write_proto(w: _Writer, proto: TypedProto) -> None:
    w.string(proto.name)
    w.boolean(proto.is_main)
    w.u16(proto.register_count)
    for ir_type in proto.register_types:
        _write_ir_type(w, ir_type)
    w.u8(len(proto.param_types))
    for ir_type in proto.param_types:
        _write_ir_type(w, ir_type)
    _write_ir_type(w, proto.ret_type)
    w.u32(len(proto.code))
    for word in proto.code:
        w.u32(word)
    w.u32(len(proto.constants))
    for constant in proto.constants:
        _write_constant(w, constant)
    w.boolean(bool(proto.positions))
    if proto.positions:
        w.string(proto.positions[0].filename)
        w.u32(len(proto.positions))
        for position in proto.positions:
            w.u32(position.start_line)
            column = position.start_column
            w.i32(-1 if column is None else column)


def _read_proto(r: _Reader) -> TypedProto:
    name = r.string()
    is_main = r.boolean()
    register_count = r.u16()
    register_types = tuple(_read_ir_type(r) for _ in range(register_count))
    params: list[IrType] = []
    for _ in range(r.u8()):
        param_type = _read_ir_type(r)
        if param_type is None:
            raise ObcError(f"typed proto {name!r} has an untyped parameter")
        params.append(param_type)
    param_types = tuple(params)
    ret_type = _read_ir_type(r)
    if ret_type is None:
        raise ObcError(f"typed proto {name!r} has no return type")
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
        register_types=register_types,
        param_types=param_types,
        ret_type=ret_type,
        is_main=is_main,
    )


def write_typed_obc(program: TypedProgram, path: str | Path) -> None:
    """Serialize a typed bytecode program to a kind=1 ``.obc`` file."""

    w = _Writer()
    w._buf += MAGIC
    w.u8(KIND_TYPED)
    w.u8(VERSION)
    w.u32(len(program.functions))
    for proto in program.functions:
        _write_proto(w, proto)
    _write_proto(w, program.main)
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
    functions = tuple(_read_proto(r) for _ in range(r.u32()))
    main = _read_proto(r)
    if r._pos != len(r._data):
        raise ObcError("trailing bytes in typed bytecode file")
    return TypedProgram(main=main, functions=functions)


__all__ = ["KIND_TYPED", "read_typed_obc", "write_typed_obc"]
