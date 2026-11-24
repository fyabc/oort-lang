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
    AdtField,
    AdtTag,
    BinOp,
    BuildAdt,
    BuildDict,
    BuildList,
    BuildSet,
    BuildTuple,
    Call,
    DefineFunction,
    FreshLocals,
    GetItem,
    ImportFrom,
    ImportModule,
    Instruction,
    IteratorNext,
    Jump,
    JumpIfFalse,
    JumpIfTrue,
    Label,
    LoadConst,
    LoadGlobal,
    LoadLocal,
    LoadOuter,
    MakeClosure,
    Move,
    OpenIterator,
    Return,
    SetItem,
    Slice,
    StoreGlobal,
    StoreLocal,
    StoreOuter,
    TupleItem,
    UnOp,
)
from ..hir.typed import (
    AdtDecl,
    AdtType,
    ContainerType,
    IrType,
    IrTypeLike,
    TypedFunction,
    TypedModule,
)
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
_STRING_COMPARISONS = {
    "<": TypedOp.LT_S,
    "<=": TypedOp.LE_S,
    ">": TypedOp.GT_S,
    ">=": TypedOp.GE_S,
}
_STRING_EQUALITY = {"==": TypedOp.EQ_S, "!=": TypedOp.NE_S}


@dataclasses.dataclass(frozen=True, slots=True)
class TypedProto:
    name: str
    code: tuple[int, ...]
    constants: tuple[object, ...]
    positions: tuple[SourcePosition, ...]
    register_count: int
    types: tuple[IrTypeLike, ...]
    register_types: tuple[int | None, ...]  # type-table indices
    param_types: tuple[int, ...]  # type-table indices
    ret_type: int  # type-table index
    is_main: bool = False
    cells: tuple[int, ...] = ()


@dataclasses.dataclass(frozen=True, slots=True)
class TypedProgram:
    main: TypedProto
    functions: tuple[TypedProto, ...]
    adt_decls: tuple[AdtDecl, ...] = ()


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
    def __init__(
        self,
        function: TypedFunction,
        capturing: set[int] | None = None,
        cells: tuple[int, ...] = (),
    ):
        self.function = function
        self.capturing = capturing if capturing is not None else set()
        self.cells = cells
        self.code: list[int] = []
        self.positions: list[SourcePosition] = []
        self.constants = _ConstantPool()
        self.register_types: list[IrTypeLike | None] = list(function.register_types)
        self.next_register = len(self.register_types)
        self.labels: dict[str, int] = {}
        self.fixups: list[tuple[int, TypedOp, int, str]] = []
        self.types: list[IrTypeLike] = []
        self.type_index: dict[IrTypeLike, int] = {}

    def _intern_type(self, ir_type: IrTypeLike) -> int:
        existing = self.type_index.get(ir_type)
        if existing is not None:
            return existing
        if isinstance(ir_type, (AdtType, ContainerType)):
            for arg in ir_type.args:
                self._intern_type(arg)
        index = len(self.types)
        self.types.append(ir_type)
        self.type_index[ir_type] = index
        return index

    def build(self) -> TypedProto:
        for instruction in self.function.hir.code:
            self._emit_instruction(instruction)
        self._resolve_jumps()
        register_type_ids: list[int | None] = []
        for ir_type in self.register_types:
            register_type_ids.append(None if ir_type is None else self._intern_type(ir_type))
        param_type_ids = tuple(self._intern_type(t) for t in self.function.param_types)
        ret_type_id = self._intern_type(self.function.ret_type)
        return TypedProto(
            name=self.function.hir.name,
            code=tuple(self.code),
            constants=tuple(self.constants.values),
            positions=tuple(self.positions),
            register_count=len(self.register_types),
            types=tuple(self.types),
            register_types=tuple(register_type_ids),
            param_types=param_type_ids,
            ret_type=ret_type_id,
            is_main=self.function.hir.is_main,
            cells=self.cells,
        )

    # ------------------------------------------------------------------
    # Emission helpers
    # ------------------------------------------------------------------

    def _emit(self, word: int, position: SourcePosition) -> None:
        self.code.append(word)
        self.positions.append(position)

    def _alloc(self, ir_type: IrTypeLike, position: SourcePosition) -> int:
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

    def _register_type(self, register: int, position: SourcePosition) -> IrTypeLike:
        ir_type = self.function.register_types[register]
        if ir_type is None:
            raise UnsupportedSyntax(
                f"Typed bytecode register R{register} has no static type.",
                position,
            )
        return ir_type

    def _ensure_float(self, register: int, ir_type: IrTypeLike, position: SourcePosition) -> int:
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
        if isinstance(instruction, (ImportFrom, ImportModule)):
            return
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
        elif isinstance(instruction, MakeClosure):
            # A capturing lambda snapshots the creating frame; a leaf lambda
            # is just a function reference.
            opcode = (
                TypedOp.MK_CLOSURE
                if instruction.function_index in self.capturing
                else TypedOp.MK_FUN
            )
            self._emit(encode_abx(opcode, instruction.dst, instruction.function_index), position)
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
        elif isinstance(instruction, BuildAdt):
            self._emit_adt(instruction)
        elif isinstance(instruction, AdtTag):
            self._emit(
                encode_abc(TypedOp.ADT_TAG, instruction.dst, instruction.value, 0),
                position,
            )
        elif isinstance(instruction, AdtField):
            self._emit(
                encode_abc(
                    TypedOp.ADT_FIELD, instruction.dst, instruction.value, instruction.index
                ),
                position,
            )
        elif isinstance(instruction, LoadOuter):
            self._emit(
                encode_abc(
                    TypedOp.LOAD_OUTER, instruction.dst, instruction.depth, instruction.slot
                ),
                position,
            )
        elif isinstance(instruction, StoreOuter):
            self._emit(
                encode_abc(
                    TypedOp.STORE_OUTER, instruction.depth, instruction.slot, instruction.src
                ),
                position,
            )
        elif isinstance(instruction, Slice):
            self._emit_slice(instruction)
        elif isinstance(instruction, TupleItem):
            self._emit(
                encode_abc(
                    TypedOp.TUPLE_ITEM, instruction.dst, instruction.value, instruction.index
                ),
                position,
            )
        elif isinstance(instruction, BuildList):
            self._emit_sequence(instruction, TypedOp.NEW_LIST)
        elif isinstance(instruction, BuildSet):
            self._emit_sequence(instruction, TypedOp.NEW_SET)
        elif isinstance(instruction, BuildTuple):
            self._emit_sequence(instruction, TypedOp.NEW_TUPLE)
        elif isinstance(instruction, BuildDict):
            self._emit_dict(instruction)
        elif isinstance(instruction, GetItem):
            self._emit(
                encode_abc(
                    TypedOp.GET_ITEM,
                    instruction.dst,
                    instruction.container,
                    instruction.index,
                ),
                position,
            )
        elif isinstance(instruction, SetItem):
            self._emit(
                encode_abc(
                    TypedOp.SET_ITEM,
                    instruction.container,
                    instruction.index,
                    instruction.src,
                ),
                position,
            )
        elif isinstance(instruction, OpenIterator):
            self._emit(
                encode_abc(TypedOp.OPEN_ITER, instruction.dst, instruction.iterable, 0),
                position,
            )
        elif isinstance(instruction, IteratorNext):
            ok = self._alloc(IrType.BOOL, position)
            self._emit(
                encode_abc(TypedOp.ITER_NEXT, instruction.value_dst, instruction.iterator, ok),
                position,
            )
            self._emit_fixup(TypedOp.JMP_FALSE, ok, instruction.done, position)
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
            # Each loop iteration gets fresh cells so closures created in
            # earlier iterations keep their own bindings.
            for slot in instruction.slots:
                self._emit(encode_abc(TypedOp.FRESH_CELL, slot, 0, 0), position)
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

    def _emit_slice(self, instruction: Slice) -> None:
        position = instruction.position
        container_type = self._register_type(instruction.container, position)
        base = self._alloc(container_type, position)
        self._emit(encode_abc(TypedOp.MOVE, base, instruction.container, 0), position)
        flags = 0
        for offset, bound in ((1, instruction.start), (2, instruction.stop)):
            if bound is None:
                slot = self._alloc(IrType.UNIT, position)
                self._emit(
                    encode_abx(TypedOp.LOAD_K, slot, self._constant(None, position)), position
                )
            else:
                bound_type = self._register_type(bound, position)
                slot = self._alloc(bound_type, position)
                self._emit(encode_abc(TypedOp.MOVE, slot, bound, 0), position)
                flags |= 1 << (offset - 1)
            if slot != base + offset:
                raise UnsupportedSyntax("Typed slice window is not contiguous.", position)
        self._emit(
            encode_abc(TypedOp.SLICE, base, flags, instruction.dst),
            position,
        )

    def _emit_sequence(
        self, instruction: BuildList | BuildSet | BuildTuple, opcode: TypedOp
    ) -> None:
        position = instruction.position
        count = len(instruction.elements)
        if count > 255:
            raise UnsupportedSyntax("Typed collection literal has too many elements.", position)
        base = 0
        for index, element in enumerate(instruction.elements):
            element_type = self._register_type(element, position)
            slot = self._alloc(element_type, position)
            if index == 0:
                base = slot
            elif slot != base + index:
                raise UnsupportedSyntax(
                    "Typed collection window is not contiguous.",
                    position,
                )
            self._emit(encode_abc(TypedOp.MOVE, slot, element, 0), position)
        self._emit(encode_abc(opcode, base, count, instruction.dst), position)

    def _emit_adt(self, instruction: BuildAdt) -> None:
        position = instruction.position
        count = len(instruction.args)
        if count > 255 or instruction.constructor_id > 255:
            raise UnsupportedSyntax("Typed ADT constructor exceeds the bytecode limit.", position)
        base = 0
        for index, argument in enumerate(instruction.args):
            argument_type = self._register_type(argument, position)
            slot = self._alloc(argument_type, position)
            if index == 0:
                base = slot
            elif slot != base + index:
                raise UnsupportedSyntax("Typed ADT payload window is not contiguous.", position)
            self._emit(encode_abc(TypedOp.MOVE, slot, argument, 0), position)
        self._emit(
            encode_abc(TypedOp.NEW_ADT, base, instruction.constructor_id, instruction.dst),
            position,
        )

    def _emit_dict(self, instruction: BuildDict) -> None:
        position = instruction.position
        count = len(instruction.items)
        if 2 * count > 255:
            raise UnsupportedSyntax("Typed Dict literal has too many entries.", position)
        base = 0
        for index, (key, value) in enumerate(instruction.items):
            key_type = self._register_type(key, position)
            value_type = self._register_type(value, position)
            key_slot = self._alloc(key_type, position)
            if index == 0:
                base = key_slot
            elif key_slot != base + 2 * index:
                raise UnsupportedSyntax(
                    "Typed Dict window is not contiguous.",
                    position,
                )
            value_slot = self._alloc(value_type, position)
            if value_slot != key_slot + 1:
                raise UnsupportedSyntax(
                    "Typed Dict window is not contiguous.",
                    position,
                )
            self._emit(encode_abc(TypedOp.MOVE, key_slot, key, 0), position)
            self._emit(encode_abc(TypedOp.MOVE, value_slot, value, 0), position)
        self._emit(encode_abc(TypedOp.NEW_DICT, base, count, instruction.dst), position)

    def _emit_binop(self, instruction: BinOp) -> None:
        position = instruction.position
        lhs_type = self._register_type(instruction.lhs, position)
        rhs_type = self._register_type(instruction.rhs, position)
        op = instruction.op
        lhs = instruction.lhs
        rhs = instruction.rhs

        if op in ("in", "!in"):
            self._emit(encode_abc(TypedOp.CONTAINS, instruction.dst, rhs, lhs), position)
            if op == "!in":
                self._emit(encode_abc(TypedOp.NOT_B, instruction.dst, instruction.dst, 0), position)
            return

        set_ops = {
            "|": TypedOp.SET_UNION,
            "&": TypedOp.SET_INTERSECT,
            "-": TypedOp.SET_DIFFERENCE,
            "^": TypedOp.SET_SYMMETRIC,
        }
        lhs_set = isinstance(lhs_type, ContainerType) and lhs_type.kind == "Set"
        rhs_set = isinstance(rhs_type, ContainerType) and rhs_type.kind == "Set"
        if op in set_ops and (lhs_set or rhs_set):
            if not (lhs_set and rhs_set):
                raise UnsupportedSyntax(
                    f"Typed bytecode set operator {op!r} requires two Sets.", position
                )
            self._emit(encode_abc(set_ops[op], instruction.dst, lhs, rhs), position)
            return

        if (
            isinstance(lhs_type, ContainerType)
            and isinstance(rhs_type, ContainerType)
            and lhs_type == rhs_type
            and lhs_type.kind in ("List", "Tuple", "Set", "Dict")
        ):
            if op not in ("==", "!="):
                raise UnsupportedSyntax(
                    f"Typed bytecode does not support {lhs_type.kind} operator {op!r}.",
                    position,
                )
            equality_ops = {
                "List": (TypedOp.EQ_LIST, TypedOp.NE_LIST),
                "Tuple": (TypedOp.EQ_TUPLE, TypedOp.NE_TUPLE),
                "Set": (TypedOp.EQ_SET, TypedOp.NE_SET),
                "Dict": (TypedOp.EQ_DICT, TypedOp.NE_DICT),
            }
            eq_op, ne_op = equality_ops[lhs_type.kind]
            opcode = eq_op if op == "==" else ne_op
            self._emit(encode_abc(opcode, instruction.dst, lhs, rhs), position)
            return

        if isinstance(lhs_type, AdtType) and isinstance(rhs_type, AdtType) and lhs_type == rhs_type:
            if op not in ("==", "!="):
                raise UnsupportedSyntax(
                    f"Typed bytecode does not support ADT operator {op!r}.",
                    position,
                )
            opcode = TypedOp.EQ_ADT if op == "==" else TypedOp.NE_ADT
            self._emit(encode_abc(opcode, instruction.dst, lhs, rhs), position)
            return

        if lhs_type is IrType.STRING and rhs_type is IrType.STRING:
            if op == "+":
                self._emit(encode_abc(TypedOp.ADD_S, instruction.dst, lhs, rhs), position)
                return
            if op in _STRING_COMPARISONS:
                self._emit(
                    encode_abc(_STRING_COMPARISONS[op], instruction.dst, lhs, rhs),
                    position,
                )
                return
            if op in _STRING_EQUALITY:
                self._emit(
                    encode_abc(_STRING_EQUALITY[op], instruction.dst, lhs, rhs),
                    position,
                )
                return
            raise UnsupportedSyntax(
                f"Typed bytecode does not support string operator {op!r}.",
                position,
            )

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

    # Main is the root frame; key it -1 so top-level lambdas resolve their
    # creator chain the same way functions do.
    bodies = {-1: module.main.hir.code}
    bodies.update((index, function.hir.code) for index, function in enumerate(module.functions))

    capturing = {
        index
        for index, function in enumerate(module.functions)
        if any(
            isinstance(instruction, (LoadOuter, StoreOuter)) for instruction in function.hir.code
        )
    }
    # A lambda whose subtree captures must itself be a closure: its snapshot
    # carries the parent chain nested reads walk through, even when the
    # lambda reads no outer slot directly. Named functions and main execute
    # without a closure context and need no marking.
    enclosing: dict[int, int] = {}
    for owner, code in bodies.items():
        for instruction in code:
            if isinstance(instruction, MakeClosure):
                enclosing[instruction.function_index] = owner
    changed = True
    while changed:
        changed = False
        for index, function in enumerate(module.functions):
            if index in capturing or index not in enclosing:
                continue
            if any(
                isinstance(instruction, MakeClosure) and instruction.function_index in capturing
                for instruction in function.hir.code
            ):
                capturing.add(index)
                changed = True

    # Cell slots: locals of this function that any lambda subtree reads or
    # writes, resolved through the creator chain (LoadOuter/StoreOuter depth
    # is 1-based from the referencing function). Parameters keep their entry
    # value; the VM wraps cell slots at frame setup.
    def cell_slots(owner: int) -> tuple[int, ...]:
        slots: set[int] = set()

        def walk(lambda_index: int) -> None:
            inner = module.functions[lambda_index]
            for instruction in inner.hir.code:
                if isinstance(instruction, (LoadOuter, StoreOuter)):
                    target = lambda_index
                    for _ in range(instruction.depth):
                        target = enclosing.get(target, -1)
                    if target == owner:
                        slots.add(instruction.slot)
                elif isinstance(instruction, MakeClosure):
                    walk(instruction.function_index)

        for instruction in bodies[owner]:
            if isinstance(instruction, MakeClosure):
                walk(instruction.function_index)
        return tuple(sorted(slots))

    functions = tuple(
        _ProtoBuilder(function, capturing, cell_slots(index)).build()
        for index, function in enumerate(module.functions)
    )
    main = _ProtoBuilder(module.main, capturing, cell_slots(-1)).build()
    return TypedProgram(main=main, functions=functions, adt_decls=module.adt_decls)
