#! /usr/bin/env python

"""Typed bytecode opcodes (`.obc` kind=1, design 15 M3).

The encoding reuses the 32-bit ABC/ABx layout, but opcodes live in a separate
namespace: a kind=1 reader must never interpret them as erased bytecode.
"""

from __future__ import annotations

from enum import IntEnum


class TypedOp(IntEnum):
    LOAD_K = 1
    LOAD_L = 2
    STORE_L = 3
    LOAD_G = 4
    DEF_FUN = 5
    MOVE = 6

    ADD_I = 10
    ADD_F = 11
    SUB_I = 12
    SUB_F = 13
    MUL_I = 14
    MUL_F = 15
    DIV_F = 16
    FLOORDIV_I = 17
    FLOORDIV_F = 18
    MOD_I = 19
    MOD_F = 20

    EQ_I = 21
    EQ_F = 22
    EQ_B = 23
    NE_I = 24
    NE_F = 25
    NE_B = 26
    LT_I = 27
    LT_F = 28
    LE_I = 29
    LE_F = 30
    GT_I = 31
    GT_F = 32
    GE_I = 33
    GE_F = 34

    POS_I = 35
    POS_F = 36
    NEG_I = 37
    NEG_F = 38
    NOT_B = 39
    TO_FLOAT = 40

    JMP = 41
    JMP_FALSE = 42
    JMP_TRUE = 43
    CALL = 44
    RET = 45

    EQ_MIXED = 46
    NE_MIXED = 47
    LT_MIXED = 48
    LE_MIXED = 49
    GT_MIXED = 50
    GE_MIXED = 51

    ADD_S = 52
    EQ_S = 53
    NE_S = 54
    LT_S = 55
    LE_S = 56
    GT_S = 57
    GE_S = 58


# ABC: [op:8][A:8][B:8][C:8]
ABC_OPS = frozenset(
    {
        TypedOp.LOAD_L,
        TypedOp.STORE_L,
        TypedOp.MOVE,
        TypedOp.ADD_I,
        TypedOp.ADD_F,
        TypedOp.SUB_I,
        TypedOp.SUB_F,
        TypedOp.MUL_I,
        TypedOp.MUL_F,
        TypedOp.DIV_F,
        TypedOp.FLOORDIV_I,
        TypedOp.FLOORDIV_F,
        TypedOp.MOD_I,
        TypedOp.MOD_F,
        TypedOp.EQ_I,
        TypedOp.EQ_F,
        TypedOp.EQ_B,
        TypedOp.NE_I,
        TypedOp.NE_F,
        TypedOp.NE_B,
        TypedOp.LT_I,
        TypedOp.LT_F,
        TypedOp.LE_I,
        TypedOp.LE_F,
        TypedOp.GT_I,
        TypedOp.GT_F,
        TypedOp.GE_I,
        TypedOp.GE_F,
        TypedOp.POS_I,
        TypedOp.POS_F,
        TypedOp.NEG_I,
        TypedOp.NEG_F,
        TypedOp.NOT_B,
        TypedOp.TO_FLOAT,
        TypedOp.CALL,
        TypedOp.RET,
        TypedOp.EQ_MIXED,
        TypedOp.NE_MIXED,
        TypedOp.LT_MIXED,
        TypedOp.LE_MIXED,
        TypedOp.GT_MIXED,
        TypedOp.GE_MIXED,
        TypedOp.ADD_S,
        TypedOp.EQ_S,
        TypedOp.NE_S,
        TypedOp.LT_S,
        TypedOp.LE_S,
        TypedOp.GT_S,
        TypedOp.GE_S,
    }
)

# ABx: [op:8][A:8][Bx:16]
ABX_OPS = frozenset(
    {
        TypedOp.LOAD_K,
        TypedOp.LOAD_G,
        TypedOp.DEF_FUN,
        TypedOp.JMP,
        TypedOp.JMP_FALSE,
        TypedOp.JMP_TRUE,
    }
)


def encode_abc(op: TypedOp, a: int, b: int, c: int) -> int:
    return (int(op) << 24) | (a << 16) | (b << 8) | c


def encode_abx(op: TypedOp, a: int, bx: int) -> int:
    return (int(op) << 24) | (a << 16) | bx


def decode_op(word: int) -> TypedOp:
    return TypedOp(word >> 24)


def decode_a(word: int) -> int:
    return (word >> 16) & 0xFF


def decode_bx(word: int) -> int:
    return word & 0xFFFF


def decode_b(word: int) -> int:
    return (word >> 8) & 0xFF


def decode_c(word: int) -> int:
    return word & 0xFF
