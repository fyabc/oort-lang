#! /usr/bin/env python

"""Binary serialization of type-erased bytecode (the ``.obc`` format, spec 13).

The format is a little-endian binary container for a :class:`BytecodeModule`:
a magic header (``OBC`` + kind + version), the flat function table, then the
main proto. Each proto carries its code words, tagged constant pool, signature
and (optional) source positions. Opcode numbers and descriptor semantics are
defined by spec 12 / ``opcodes.py``; this module only adds the file layer.

``kind`` distinguishes bytecode families (0 = dynamic/type-erased; 1+ reserved
for future typed bytecode) and ``version`` the format revision of that kind, so
future bytecode variants can share the ``.obc`` extension.
"""

from __future__ import annotations

import struct
from pathlib import Path

from ..runtime.call_protocol import ParamKind, ParamSpec, SignatureSpec
from ..source.source_position import SourcePosition
from .code import (
    BytecodeModule,
    CallSpec,
    ClassSpec,
    EnumSpec,
    ExtensionSpec,
    ImportSpec,
    MatchArmSpec,
    MatchSpec,
    PatternSpec,
    Proto,
)

MAGIC = b"OBC"
KIND_DYNAMIC = 0
VERSION = 2
_SUPPORTED_VERSIONS = (1, 2)

# Constant-pool tags. PatternSpec/MatchArmSpec are nested, not top-level entries.
_TAG_NULL = 0
_TAG_BOOL = 1
_TAG_INT = 2
_TAG_FLOAT = 3
_TAG_STR = 4
_TAG_SLOTS = 5
_TAG_CLASS = 10
_TAG_CALL = 11
_TAG_ENUM = 12
_TAG_MATCH = 13
_TAG_IMPORT = 15
_TAG_EXTENSION = 16

_PARAM_KIND_ORDER = (
    ParamKind.POS_ONLY,
    ParamKind.POS_OR_KW,
    ParamKind.VAR_POS,
    ParamKind.KW_ONLY,
    ParamKind.VAR_KW,
    ParamKind.BLOCK,
)
_PARAM_KIND_INDEX = {kind: i for i, kind in enumerate(_PARAM_KIND_ORDER)}

_PATTERN_KIND_INDEX = {
    "wildcard": 0,
    "name": 1,
    "constructor": 2,
    "literal_int": 3,
    "literal_float": 4,
    "literal_string": 5,
    "literal_bool": 6,
    "tuple": 7,
    "or": 8,
}
_PATTERN_KIND_NAME = {i: name for name, i in _PATTERN_KIND_INDEX.items()}
_LITERAL_PATTERN_KINDS = frozenset(
    {"literal_int", "literal_float", "literal_string", "literal_bool"}
)

_I64_MIN = -(1 << 63)
_I64_MAX = (1 << 63) - 1


class ObcError(ValueError):
    """Raised when a bytecode module cannot be serialized/deserialized."""


class _Writer:
    def __init__(self) -> None:
        self._buf = bytearray()

    def u8(self, value: int) -> None:
        self._buf += struct.pack("<B", value)

    def u16(self, value: int) -> None:
        self._buf += struct.pack("<H", value)

    def u32(self, value: int) -> None:
        self._buf += struct.pack("<I", value)

    def i32(self, value: int) -> None:
        self._buf += struct.pack("<i", value)

    def i64(self, value: int) -> None:
        self._buf += struct.pack("<q", value)

    def f64(self, value: float) -> None:
        self._buf += struct.pack("<d", value)

    def boolean(self, value: bool) -> None:
        self.u8(1 if value else 0)

    def string(self, value: str) -> None:
        encoded = value.encode("utf-8")
        self.u32(len(encoded))
        self._buf += encoded

    def opt_string(self, value: str | None) -> None:
        self.boolean(value is not None)
        if value is not None:
            self.string(value)

    def opt_u32(self, value: int | None) -> None:
        self.boolean(value is not None)
        if value is not None:
            self.u32(value)

    def bytes(self) -> bytes:
        return bytes(self._buf)


class _Reader:
    def __init__(self, data: bytes) -> None:
        self._data = data
        self._pos = 0
        self.version = 1

    def _take(self, n: int) -> bytes:
        if self._pos + n > len(self._data):
            raise ObcError("unexpected end of bytecode file")
        chunk = self._data[self._pos : self._pos + n]
        self._pos += n
        return chunk

    def u8(self) -> int:
        return struct.unpack("<B", self._take(1))[0]

    def u16(self) -> int:
        return struct.unpack("<H", self._take(2))[0]

    def u32(self) -> int:
        return struct.unpack("<I", self._take(4))[0]

    def i32(self) -> int:
        return struct.unpack("<i", self._take(4))[0]

    def i64(self) -> int:
        return struct.unpack("<q", self._take(8))[0]

    def f64(self) -> float:
        return struct.unpack("<d", self._take(8))[0]

    def boolean(self) -> bool:
        return self.u8() != 0

    def string(self) -> str:
        length = self.u32()
        return self._take(length).decode("utf-8")

    def opt_string(self) -> str | None:
        return self.string() if self.boolean() else None

    def opt_u32(self) -> int | None:
        return self.u32() if self.boolean() else None


def _write_pattern(w: _Writer, pattern: PatternSpec) -> None:
    w.u8(_PATTERN_KIND_INDEX[pattern.kind])
    w.string(pattern.name)
    w.u32(len(pattern.args))
    for arg in pattern.args:
        _write_pattern(w, arg)
    if pattern.kind in _LITERAL_PATTERN_KINDS:
        _write_constant(w, pattern.value)


def _write_constant(w: _Writer, value: object) -> None:
    # bool is a subclass of int: check it first to keep the tags distinct.
    if value is None:
        w.u8(_TAG_NULL)
    elif isinstance(value, bool):
        w.u8(_TAG_BOOL)
        w.boolean(value)
    elif isinstance(value, int):
        if not _I64_MIN <= value <= _I64_MAX:
            raise ObcError(f"integer constant out of i64 range: {value}")
        w.u8(_TAG_INT)
        w.i64(value)
    elif isinstance(value, float):
        w.u8(_TAG_FLOAT)
        w.f64(value)
    elif isinstance(value, str):
        w.u8(_TAG_STR)
        w.string(value)
    elif isinstance(value, tuple):
        w.u8(_TAG_SLOTS)
        w.u32(len(value))
        for slot in value:
            w.u16(slot)
    elif isinstance(value, ClassSpec):
        w.u8(_TAG_CLASS)
        w.string(value.name)
        w.u16(value.base_count)
        w.u32(len(value.methods))
        for name, index in value.methods:
            w.string(name)
            w.u32(index)
        w.u32(len(value.slots))
        for name, mutable, init_index in value.slots:
            w.string(name)
            w.boolean(mutable)
            w.opt_u32(init_index)
        w.u32(len(value.class_methods))
        for name, index in value.class_methods:
            w.string(name)
            w.u32(index)
        w.u32(len(value.operators))
        for symbol, operand_count, index in value.operators:
            w.string(symbol)
            w.u16(operand_count)
            w.u32(index)
        w.boolean(value.has_metaclass)
    elif isinstance(value, CallSpec):
        w.u8(_TAG_CALL)
        w.u16(value.positional_count)
        w.u32(len(value.keywords))
        for keyword in value.keywords:
            w.string(keyword)
        w.boolean(value.has_block)
    elif isinstance(value, EnumSpec):
        w.u8(_TAG_ENUM)
        w.string(value.name)
        w.u32(len(value.constructors))
        for name, arity in value.constructors:
            w.string(name)
            w.u16(arity)
    elif isinstance(value, MatchSpec):
        w.u8(_TAG_MATCH)
        w.u32(len(value.arms))
        for arm in value.arms:
            _write_pattern(w, arm.pattern)
            w.u32(arm.function_index)
            w.opt_u32(arm.guard_index)
    elif isinstance(value, ImportSpec):
        w.u8(_TAG_IMPORT)
        w.string(value.module_path)
        w.opt_string(value.alias)
        w.u32(len(value.names))
        for source, alias in value.names:
            w.string(source)
            w.opt_string(alias)
        w.boolean(value.is_from)
    elif isinstance(value, ExtensionSpec):
        w.u8(_TAG_EXTENSION)
        w.string(value.name)
        w.u32(value.function_index)
        w.opt_string(value.symbol)
        w.u16(value.operand_count)
        w.string(value.receiver_name)
    else:
        raise ObcError(f"unsupported constant pool entry: {type(value).__name__}")


def _write_signature(w: _Writer, signature: SignatureSpec) -> None:
    w.boolean(signature.has_this)
    w.u32(len(signature.params))
    for param in signature.params:
        w.string(param.name)
        w.u8(_PARAM_KIND_INDEX[param.kind])
        w.u16(param.slot)
        w.boolean(param.has_default)
        w.opt_u32(param.default_index)


def _write_proto(w: _Writer, proto: Proto) -> None:
    w.string(proto.name)
    w.u32(len(proto.params))
    for name in proto.params:
        w.string(name)
    w.u16(proto.register_count)
    w.u16(proto.local_count)
    w.u16(proto.scratch_base)
    flags = (
        (1 if proto.has_this else 0)
        | (2 if proto.uses_cells else 0)
        | (4 if proto.defines_extensions else 0)
    )
    w.u8(flags)
    _write_signature(w, proto.signature)
    w.u32(len(proto.code))
    for word in proto.code:
        w.u32(word)
    w.u32(len(proto.constants))
    for constant in proto.constants:
        _write_constant(w, constant)
    # Positions are optional (the VM has a fallback); store filename + per-word
    # (line, column) when present. line_table is derived from these on read.
    w.boolean(bool(proto.positions))
    if proto.positions:
        w.string(proto.positions[0].filename)
        w.u32(len(proto.positions))
        for position in proto.positions:
            w.u32(position.start_line)
            column = position.start_column
            w.i32(-1 if column is None else column)


def write_obc(module: BytecodeModule, path: str | Path) -> None:
    """Serialize a bytecode module to a ``.obc`` file."""
    w = _Writer()
    w._buf += MAGIC
    w.u8(KIND_DYNAMIC)
    w.u8(VERSION)
    w.u32(len(module.functions))
    for proto in module.functions:
        _write_proto(w, proto)
    _write_proto(w, module.main)
    Path(path).write_bytes(w.bytes())


def _read_pattern(r: _Reader) -> PatternSpec:
    kind = _PATTERN_KIND_NAME[r.u8()]
    name = r.string()
    args = tuple(_read_pattern(r) for _ in range(r.u32()))
    value = None
    if r.version >= 2 and kind in _LITERAL_PATTERN_KINDS:
        value = _read_constant(r)
    return PatternSpec(kind, name, args, value)


def _read_constant(r: _Reader) -> object:
    tag = r.u8()
    if tag == _TAG_NULL:
        return None
    if tag == _TAG_BOOL:
        return r.boolean()
    if tag == _TAG_INT:
        return r.i64()
    if tag == _TAG_FLOAT:
        return r.f64()
    if tag == _TAG_STR:
        return r.string()
    if tag == _TAG_SLOTS:
        return tuple(r.u16() for _ in range(r.u32()))
    if tag == _TAG_CLASS:
        name = r.string()
        base_count = r.u16()
        methods = tuple((r.string(), r.u32()) for _ in range(r.u32()))
        slots = tuple((r.string(), r.boolean(), r.opt_u32()) for _ in range(r.u32()))
        class_methods = tuple((r.string(), r.u32()) for _ in range(r.u32()))
        operators = tuple((r.string(), r.u16(), r.u32()) for _ in range(r.u32()))
        has_metaclass = r.boolean()
        return ClassSpec(name, base_count, methods, slots, class_methods, operators, has_metaclass)
    if tag == _TAG_CALL:
        positional_count = r.u16()
        keywords = tuple(r.string() for _ in range(r.u32()))
        has_block = r.boolean()
        return CallSpec(positional_count, keywords, has_block)
    if tag == _TAG_ENUM:
        name = r.string()
        constructors = tuple((r.string(), r.u16()) for _ in range(r.u32()))
        return EnumSpec(name, constructors)
    if tag == _TAG_MATCH:
        count = r.u32()
        arms = []
        for _ in range(count):
            pattern = _read_pattern(r)
            function_index = r.u32()
            guard_index = r.opt_u32() if r.version >= 2 else None
            arms.append(MatchArmSpec(pattern, function_index, guard_index))
        return MatchSpec(tuple(arms))
    if tag == _TAG_IMPORT:
        module_path = r.string()
        alias = r.opt_string()
        names = tuple((r.string(), r.opt_string()) for _ in range(r.u32()))
        is_from = r.boolean()
        return ImportSpec(module_path, alias, names, is_from)
    if tag == _TAG_EXTENSION:
        name = r.string()
        function_index = r.u32()
        symbol = r.opt_string()
        operand_count = r.u16()
        receiver_name = r.string()
        return ExtensionSpec(name, function_index, symbol, operand_count, receiver_name)
    raise ObcError(f"unknown constant pool tag: {tag}")


def _read_signature(r: _Reader) -> SignatureSpec:
    has_this = r.boolean()
    params = tuple(
        ParamSpec(r.string(), _PARAM_KIND_ORDER[r.u8()], r.u16(), r.boolean(), r.opt_u32())
        for _ in range(r.u32())
    )
    return SignatureSpec(params, has_this)


def _read_proto(r: _Reader) -> Proto:
    name = r.string()
    params = tuple(r.string() for _ in range(r.u32()))
    register_count = r.u16()
    local_count = r.u16()
    scratch_base = r.u16()
    flags = r.u8()
    signature = _read_signature(r)
    code = tuple(r.u32() for _ in range(r.u32()))
    constants = tuple(_read_constant(r) for _ in range(r.u32()))
    positions: tuple[SourcePosition, ...] = ()
    line_table: tuple[int, ...] = ()
    if r.boolean():
        filename = r.string()
        count = r.u32()
        lines = []
        rebuilt = []
        for _ in range(count):
            line = r.u32()
            column = r.i32()
            lines.append(line)
            rebuilt.append(
                SourcePosition.from_location(line, max(column, 0), "", filename=filename)
            )
        line_table = tuple(lines)
        positions = tuple(rebuilt)
    return Proto(
        name,
        params,
        register_count,
        code,
        constants,
        line_table,
        positions,
        scratch_base,
        bool(flags & 1),
        signature,
        local_count,
        bool(flags & 2),
        bool(flags & 4),
    )


def read_obc(path: str | Path) -> BytecodeModule:
    """Deserialize a ``.obc`` file back into a bytecode module."""
    data = Path(path).read_bytes()
    r = _Reader(data)
    if r._take(3) != MAGIC:
        raise ObcError("not an Oort bytecode file (bad magic)")
    kind = r.u8()
    if kind != KIND_DYNAMIC:
        raise ObcError(f"unsupported bytecode kind: {kind}")
    version = r.u8()
    if version not in _SUPPORTED_VERSIONS:
        raise ObcError(f"unsupported bytecode version: {version}")
    r.version = version
    functions = tuple(_read_proto(r) for _ in range(r.u32()))
    main = _read_proto(r)
    return BytecodeModule(main, functions)
