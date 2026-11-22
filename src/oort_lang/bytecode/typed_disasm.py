#! /usr/bin/env python

"""Text disassembly for typed bytecode (design 15, M3)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .typed_opcodes import TypedOp, decode_a, decode_b, decode_bx, decode_c, decode_op

if TYPE_CHECKING:
    from .typed_compile import TypedProgram, TypedProto


def _format_instruction(proto: TypedProto, word: int) -> str:
    op = decode_op(word)
    a = decode_a(word)
    b = decode_b(word)
    c = decode_c(word)
    bx = decode_bx(word)

    if op is TypedOp.LOAD_K:
        return f"LOAD_K R{a} k{bx}({proto.constants[bx]!r})"
    if op is TypedOp.LOAD_L:
        return f"LOAD_L R{a} slot{b}"
    if op is TypedOp.STORE_L:
        return f"STORE_L slot{a} R{b}"
    if op is TypedOp.LOAD_G:
        return f"LOAD_G R{a} {proto.constants[bx]!r}"
    if op is TypedOp.DEF_FUN:
        return f"DEF_FUN {proto.constants[a]!r} proto[{bx}]"
    if op is TypedOp.MOVE:
        return f"MOVE R{a} R{b}"
    if op is TypedOp.TO_FLOAT:
        return f"TO_FLOAT R{a} R{b}"
    if op is TypedOp.JMP:
        return f"JMP {bx}"
    if op is TypedOp.JMP_FALSE:
        return f"JMP_FALSE R{a} {bx}"
    if op is TypedOp.JMP_TRUE:
        return f"JMP_TRUE R{a} {bx}"
    if op is TypedOp.CALL:
        return f"CALL R{a} argc={b} -> R{c}"
    if op is TypedOp.RET:
        return f"RET R{a}"
    if op in {
        TypedOp.POS_I,
        TypedOp.POS_F,
        TypedOp.NEG_I,
        TypedOp.NEG_F,
        TypedOp.NOT_B,
    }:
        return f"{op.name} R{a} R{b}"
    return f"{op.name} R{a} R{b} R{c}"


def format_typed_proto(proto: TypedProto) -> str:
    params = ", ".join(str(proto.types[type_id]) for type_id in proto.param_types)
    lines = [
        f"{proto.name}({params}) -> {proto.types[proto.ret_type]} "
        f"registers={proto.register_count} words={len(proto.code)}"
    ]
    lines.append(
        "  register types: "
        + " ".join(
            f"R{index}:{proto.types[type_id] if type_id is not None else '?'}"
            for index, type_id in enumerate(proto.register_types)
        )
    )
    for pc, word in enumerate(proto.code):
        lines.append(f"  {pc:4d}  {_format_instruction(proto, word)}")
    return "\n".join(lines)


def disassemble_typed_program(program: TypedProgram) -> str:
    lines = [format_typed_proto(program.main)]
    for proto in program.functions:
        lines.append("")
        lines.append(format_typed_proto(proto))
    return "\n".join(lines)
