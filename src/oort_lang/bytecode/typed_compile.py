#! /usr/bin/env python

"""Compile typed HIR to typed bytecode (design 15, M3).

The first typed-bytecode slice keeps boxed runtime values but makes the static
types explicit: register types travel in the proto, arithmetic/comparison use
typed opcodes, and mixed Int/Float operations insert ``TO_FLOAT``. This is the
ABI foundation for unboxed registers and the Rust VM.
"""

from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING

from ..diagnostics.syntax_errors import UnsupportedSyntax
from ..hir.nodes import (
    BinOp,
    Call,
    DefineFunction,
    FreshLocals,
    Instruction,
    Jump,
    JumpIfFalse,
    JumpIfTrue,
    Label,
    LoadConst,
    LoadGlobal,
    LoadLocal,
    Move,
    Return,
    StoreGlobal,
    StoreLocal,
    UnOp,
)
from ..hir.typed import IrType, TypedFunction, TypedModule
from .typed_opcodes import TypedOp, encode_abc, encode_abx

if TYPE_CHECKING:
    from ..source.source_position import SourcePosition

_MAX_REGISTERS = 256
_MAX_CONSTANTS = 65536

_ARITHMETIC = {
    "+": (TypedOp.ADD_I, TypedOp.ADD_F),
    "-": (TypedOp.SUB_I, TypedOp.SUB_F),
    "*": (TypedOp.MUL_I, TypedOp.MUL_F),
    "//": (TypedOp.FLOORDIV_I, TypedOp.FLOORDIV_F),
    "%": (TypedOp.MOD_I, TypedOp.MOD_F),
}
_COMPARISONS = {
    "<": (TypedOp.LT_I, TypedOp.LT_F),
    "<=": (TypedOp.LE_I, TypedOp.LE_F),
    ">": (TypedOp.GT_I, TypedOp.GT_F),
    ">=": (TypedOp.GE_I, TypedOp.GE_F),
}
_EQUALITY = {
    "==": (TypedOp.EQ_I, TypedOp.EQ_F, TypedOp.EQ_B),
    "!=": (TypedOp.NE_I, TypedOp.NE_F, TypedOp.NE_B),
}
_MIXED_COMPARISONS = {
    "<": TypedOp.LT_MIXED,
    "<=": TypedOp.LE_MIXED,
    ">": TypedOp.GT_MIXED,
    ">=": TypedOp.GE_MIXED,
}
_MIXED_EQUALITY = {"==": TypedOp.EQ_MIXED, "!=": TypedOp.NE_MIXED}


@dataclasses.dataclass(frozen=True, slots=True)
class TypedProto:
    name: str
    code: tuple[int, ...]
    constants: tuple[object, ...]
    positions: tuple[SourcePosition, ...]
    register_count: int
    register_types: tuple[IrType | None, ...]
    param_types: tuple[IrType, ...]
    ret_type: IrType
    is_main: bool = False


@dataclasses.dataclass(frozen=True, slots=True)
class TypedProgram:
    main: TypedProto
    functions: tuple[TypedProto, ...]


class _ConstantPool:
    def __init__(self) -> None:
        self.values: list[object] = []
        self.index: dict[tuple[type, object], int] = {}

    def add(self, value: object, position: SourcePosition) -> int:
        key = (type(value), value)
        existing = self.index.get(key)
        if existing is not None:
            return existing
        if len(self.values) >= _MAX_CONSTANTS:
            raise UnsupportedSyntax("Typed bytecode constant pool overflow.", position)
        index = len(self.values)
        self.values.append(value)
        self.index[key] = index
        return index


class _ProtoBuilder:
    def __init__(self, function: TypedFunction):
        self.function = function
        self.code: list[int] = []
        self.positions: list[SourcePosition] = []
        self.constants = _ConstantPool()
        self.register_types: list[IrType | None] = list(function.register_types)
        self.next_register = len(self.register_types)
        self.labels: dict[str, int] = {}
        self.fixups: list[tuple[int, TypedOp, int, str]] = []

    def build(self) -> TypedProto:
        for instruction in self.function.hir.code:
            self._emit_instruction(instruction)
        self._resolve_jumps()
        return TypedProto(
            name=self.function.hir.name,
            code=tuple(self.code),
            constants=tuple(self.constants.values),
            positions=tuple(self.positions),
            register_count=len(self.register_types),
            register_types=tuple(self.register_types),
            param_types=self.function.param_types,
            ret_type=self.function.ret_type,
            is_main=self.function.hir.is_main,
        )

    # ------------------------------------------------------------------
    # Emission helpers
    # ------------------------------------------------------------------

    def _emit(self, word: int, position: SourcePosition) -> None:
        self.code.append(word)
        self.positions.append(position)

    def _alloc(self, ir_type: IrType, position: SourcePosition) -> int:
        if self.next_register >= _MAX_REGISTERS:
            raise UnsupportedSyntax(
                f"Typed bytecode register limit ({_MAX_REGISTERS}) exceeded.",
                position,
            )
        register = self.next_register
        self.next_register += 1
        self.register_types.append(ir_type)
        return register

    def _constant(self, value: object, position: SourcePosition) -> int:
        return self.constants.add(value, position)

    def _register_type(self, register: int, position: SourcePosition) -> IrType:
        ir_type = self.function.register_types[register]
        if ir_type is None:
            raise UnsupportedSyntax(
                f"Typed bytecode register R{register} has no static type.",
                position,
            )
        return ir_type

    def _ensure_float(self, register: int, ir_type: IrType, position: SourcePosition) -> int:
        if ir_type is IrType.FLOAT:
            return register
        converted = self._alloc(IrType.FLOAT, position)
        self._emit(encode_abc(TypedOp.TO_FLOAT, converted, register, 0), position)
        return converted

    # ------------------------------------------------------------------
    # Instructions
    # ------------------------------------------------------------------

    def _emit_instruction(self, instruction: Instruction) -> None:
        position = instruction.position
        if isinstance(instruction, LoadConst):
            index = self._constant(instruction.value, position)
            self._emit(encode_abx(TypedOp.LOAD_K, instruction.dst, index), position)
        elif isinstance(instruction, LoadLocal):
            self._emit(
                encode_abc(TypedOp.LOAD_L, instruction.dst, instruction.slot, 0),
                position,
            )
        elif isinstance(instruction, StoreLocal):
            self._emit(
                encode_abc(TypedOp.STORE_L, instruction.slot, instruction.src, 0),
                position,
            )
        elif isinstance(instruction, LoadGlobal):
            index = self._constant(instruction.name, position)
            self._emit(encode_abx(TypedOp.LOAD_G, instruction.dst, index), position)
        elif isinstance(instruction, DefineFunction):
            name_index = self._constant(instruction.name, position)
            if name_index >= 256:
                raise UnsupportedSyntax(
                    "Typed bytecode function name constant index exceeds 255.",
                    position,
                )
            self._emit(
                encode_abx(TypedOp.DEF_FUN, name_index, instruction.function_index),
                position,
            )
        elif isinstance(instruction, Move):
            self._emit(
                encode_abc(TypedOp.MOVE, instruction.dst, instruction.src, 0),
                position,
            )
        elif isinstance(instruction, BinOp):
            self._emit_binop(instruction)
        elif isinstance(instruction, UnOp):
            self._emit_unop(instruction)
        elif isinstance(instruction, Label):
            self.labels[instruction.name] = len(self.code)
        elif isinstance(instruction, Jump):
            self._emit_fixup(TypedOp.JMP, 0, instruction.target, position)
        elif isinstance(instruction, JumpIfFalse):
            self._emit_fixup(TypedOp.JMP_FALSE, instruction.src, instruction.target, position)
        elif isinstance(instruction, JumpIfTrue):
            self._emit_fixup(TypedOp.JMP_TRUE, instruction.src, instruction.target, position)
        elif isinstance(instruction, FreshLocals):
            # The scalar subset has no closures, so per-iteration cells are
            # not observable; skip the erased-path cell refresh.
            return
        elif isinstance(instruction, Return):
            self._emit(encode_abc(TypedOp.RET, instruction.src, 0, 0), position)
        elif isinstance(instruction, Call):
            self._emit_call(instruction)
        elif isinstance(instruction, StoreGlobal):
            raise UnsupportedSyntax("Typed bytecode does not support global stores.", position)
        else:
            raise UnsupportedSyntax(
                f"Typed bytecode does not support {type(instruction).__name__}.",
                position,
            )

    def _emit_binop(self, instruction: BinOp) -> None:
        position = instruction.position
        lhs_type = self._register_type(instruction.lhs, position)
        rhs_type = self._register_type(instruction.rhs, position)
        op = instruction.op
        lhs = instruction.lhs
        rhs = instruction.rhs

        if op == "/":
            lhs = self._ensure_float(lhs, lhs_type, position)
            rhs = self._ensure_float(rhs, rhs_type, position)
            self._emit(encode_abc(TypedOp.DIV_F, instruction.dst, lhs, rhs), position)
            return

        if op in _ARITHMETIC:
            int_op, float_op = _ARITHMETIC[op]
            if lhs_type is IrType.INT and rhs_type is IrType.INT:
                self._emit(encode_abc(int_op, instruction.dst, lhs, rhs), position)
            else:
                lhs = self._ensure_float(lhs, lhs_type, position)
                rhs = self._ensure_float(rhs, rhs_type, position)
                self._emit(encode_abc(float_op, instruction.dst, lhs, rhs), position)
            return

        if op in _COMPARISONS:
            int_op, float_op = _COMPARISONS[op]
            if lhs_type is IrType.INT and rhs_type is IrType.INT:
                self._emit(encode_abc(int_op, instruction.dst, lhs, rhs), position)
            elif lhs_type is IrType.FLOAT and rhs_type is IrType.FLOAT:
                self._emit(encode_abc(float_op, instruction.dst, lhs, rhs), position)
            else:
                self._emit(
                    encode_abc(_MIXED_COMPARISONS[op], instruction.dst, lhs, rhs),
                    position,
                )
            return

        if op in _EQUALITY:
            int_op, float_op, bool_op = _EQUALITY[op]
            if lhs_type is IrType.BOOL and rhs_type is IrType.BOOL:
                self._emit(encode_abc(bool_op, instruction.dst, lhs, rhs), position)
            elif lhs_type is IrType.INT and rhs_type is IrType.INT:
                self._emit(encode_abc(int_op, instruction.dst, lhs, rhs), position)
            elif lhs_type is IrType.FLOAT and rhs_type is IrType.FLOAT:
                self._emit(encode_abc(float_op, instruction.dst, lhs, rhs), position)
            else:
                self._emit(
                    encode_abc(_MIXED_EQUALITY[op], instruction.dst, lhs, rhs),
                    position,
                )
            return

        raise UnsupportedSyntax(
            f"Typed bytecode does not support binary operator {op!r}.",
            position,
        )

    def _emit_unop(self, instruction: UnOp) -> None:
        position = instruction.position
        operand_type = self._register_type(instruction.operand, position)
        if instruction.op == "not":
            self._emit(
                encode_abc(TypedOp.NOT_B, instruction.dst, instruction.operand, 0),
                position,
            )
            return
        if instruction.op in {"+", "-"}:
            if operand_type is IrType.INT:
                op = TypedOp.POS_I if instruction.op == "+" else TypedOp.NEG_I
            elif operand_type is IrType.FLOAT:
                op = TypedOp.POS_F if instruction.op == "+" else TypedOp.NEG_F
            else:
                raise UnsupportedSyntax(
                    f"Typed bytecode unary operator {instruction.op!r} requires a number.",
                    position,
                )
            self._emit(encode_abc(op, instruction.dst, instruction.operand, 0), position)
            return
        raise UnsupportedSyntax(
            f"Typed bytecode does not support unary operator {instruction.op!r}.",
            position,
        )

    def _emit_fixup(
        self,
        op: TypedOp,
        a: int,
        label: str,
        position: SourcePosition,
    ) -> None:
        index = len(self.code)
        self._emit(encode_abx(op, a, 0), position)
        self.fixups.append((index, op, a, label))

    def _resolve_jumps(self) -> None:
        for index, op, a, label in self.fixups:
            target = self.labels.get(label)
            if target is None:
                raise UnsupportedSyntax(
                    f"Typed bytecode jump target '{label}' is missing.",
                    self.positions[index],
                )
            self.code[index] = encode_abx(op, a, target)

    def _emit_call(self, instruction: Call) -> None:
        position = instruction.position
        if instruction.keywords or instruction.block is not None:
            raise UnsupportedSyntax(
                "Typed bytecode does not support keyword or block arguments.",
                position,
            )
        argc = len(instruction.args)
        if argc > 255:
            raise UnsupportedSyntax("Typed bytecode call has too many arguments.", position)
        base = self._alloc(IrType.FUNCTION, position)
        self._emit(encode_abc(TypedOp.MOVE, base, instruction.callee, 0), position)
        for index, argument in enumerate(instruction.args):
            argument_type = self._register_type(argument, position)
            slot = self._alloc(argument_type, position)
            if slot != base + 1 + index:
                raise UnsupportedSyntax(
                    "Typed bytecode call window is not contiguous.",
                    position,
                )
            self._emit(encode_abc(TypedOp.MOVE, slot, argument, 0), position)
        self._emit(encode_abc(TypedOp.CALL, base, argc, instruction.dst), position)


def compile_typed_module(module: TypedModule) -> TypedProgram:
    """Compile a typed HIR module to typed bytecode."""

    functions = tuple(_ProtoBuilder(function).build() for function in module.functions)
    main = _ProtoBuilder(module.main).build()
    return TypedProgram(main=main, functions=functions)
