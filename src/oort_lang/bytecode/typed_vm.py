#! /usr/bin/env python

"""Typed bytecode VM (design 15, M3).

Executes ``TypedProgram`` words with typed opcodes. Values are still boxed
Oort objects in this slice; the point is to validate the typed ABI (register
types, typed arithmetic, TO_FLOAT, entry guards) before M4 moves to unboxed
registers and the Rust VM.
"""

from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING, Any

from ..diagnostics.runtime_errors import OortNameError, OortRuntimeError, OortTypeError
from ..hir.typed import AdtType, ContainerType, IrType, IrTypeLike, adt_runtime_name
from ..runtime.environment import Environment
from ..runtime.functions import OortNativeFunction
from ..runtime.objects import (
    OortADT,
    OortBool,
    OortDict,
    OortFloat,
    OortInt,
    OortList,
    OortNull,
    OortObject,
    OortSet,
    OortString,
    OortTuple,
)
from ..runtime.type_system import OortType
from .typed_opcodes import TypedOp, decode_a, decode_b, decode_bx, decode_c, decode_op

if TYPE_CHECKING:
    from ..runtime.interpreter import ASTInterpreter
    from ..source.source_position import SourcePosition
    from .typed_compile import TypedProgram, TypedProto


@dataclasses.dataclass(frozen=True, slots=True)
class TypedCodeFunction:
    """A typed bytecode function bound in globals."""

    proto: TypedProto


class TypedCodeVM:
    def __init__(self, interpreter: ASTInterpreter):
        self.interpreter = interpreter
        self.runtime = interpreter.runtime
        self.globals: dict[str, TypedCodeFunction] = {}
        self._program: TypedProgram | None = None
        self._adt_types: dict[str, OortType] = {}
        self._adt_by_name: dict[str, int] = {}
        self._constructors: dict[int, tuple[int, int]] = {}
        self.env = Environment(
            outer=interpreter.builtins_env,
            name="<typed-bytecode>",
            allow_redefine=True,
            is_module_root=True,
        )

    def run(self, program: TypedProgram) -> OortObject:
        self._program = program
        for proto in program.functions:
            self.globals.setdefault(proto.name, TypedCodeFunction(proto))
        registers: list[Any] = [self.runtime.null] * program.main.register_count
        with self.runtime.activate():
            self._prepare_adts(program)
            return self._execute(program, program.main, registers)

    def _prepare_adts(self, program: TypedProgram) -> None:
        self._adt_types = {}
        self._adt_by_name = {}
        self._constructors = {}
        decl_index = {
            (decl.origin, decl.name): index for index, decl in enumerate(program.adt_decls)
        }
        for proto in (program.main, *program.functions):
            for ir_type in proto.types:
                if not isinstance(ir_type, AdtType):
                    continue
                key = (ir_type.origin, ir_type.name)
                index = decl_index.get(key)
                if index is None:
                    raise OortTypeError(f"Unknown ADT type {ir_type}.", proto.positions[0])
                runtime_name = adt_runtime_name(ir_type)
                self._adt_types[runtime_name] = OortType(runtime_name)
                self._adt_by_name[runtime_name] = index
        constructor_id = 0
        for decl_index_value, decl in enumerate(program.adt_decls):
            for ctor_index, _constructor in enumerate(decl.constructors):
                self._constructors[constructor_id] = (decl_index_value, ctor_index)
                constructor_id += 1

    def invoke(
        self,
        proto: TypedProto,
        arguments: list[Any],
        position: SourcePosition,
    ) -> OortObject:
        """Invoke a typed function after ``run`` has initialized the module."""
        if self._program is None:
            raise OortRuntimeError("Typed VM has not run a module yet.", position)
        with self.runtime.activate():
            return self._invoke(self._program, proto, arguments, position)

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def _execute(
        self,
        program: TypedProgram,
        proto: TypedProto,
        registers: list[Any],
    ) -> OortObject:
        code = proto.code
        pc = 0
        while pc < len(code):
            word = code[pc]
            op = decode_op(word)
            a = decode_a(word)
            b = decode_b(word)
            c = decode_c(word)
            bx = decode_bx(word)
            position = proto.positions[pc]

            if op is TypedOp.LOAD_K:
                registers[a] = self._wrap_constant(proto.constants[bx])
            elif op is TypedOp.LOAD_L or op is TypedOp.STORE_L:
                registers[a] = registers[b]
            elif op is TypedOp.LOAD_G:
                registers[a] = self._load_global(proto, bx, position)
            elif op is TypedOp.DEF_FUN:
                name = proto.constants[a]
                if not isinstance(name, str):
                    raise OortTypeError("Invalid function name constant.", position)
                if not 0 <= bx < len(program.functions):
                    raise OortTypeError("Invalid typed function index.", position)
                self.globals[name] = TypedCodeFunction(program.functions[bx])
            elif op is TypedOp.MOVE:
                registers[a] = registers[b]
            elif op in (
                TypedOp.ADD_I,
                TypedOp.SUB_I,
                TypedOp.MUL_I,
                TypedOp.FLOORDIV_I,
                TypedOp.MOD_I,
            ):
                registers[a] = self._int_binary(op, registers[b], registers[c], position)
            elif op in (
                TypedOp.ADD_F,
                TypedOp.SUB_F,
                TypedOp.MUL_F,
                TypedOp.FLOORDIV_F,
                TypedOp.MOD_F,
                TypedOp.DIV_F,
            ):
                registers[a] = self._float_binary(op, registers[b], registers[c], position)
            elif op in (
                TypedOp.EQ_I,
                TypedOp.NE_I,
                TypedOp.LT_I,
                TypedOp.LE_I,
                TypedOp.GT_I,
                TypedOp.GE_I,
            ):
                registers[a] = self._int_compare(op, registers[b], registers[c], position)
            elif op in (
                TypedOp.EQ_F,
                TypedOp.NE_F,
                TypedOp.LT_F,
                TypedOp.LE_F,
                TypedOp.GT_F,
                TypedOp.GE_F,
            ):
                registers[a] = self._float_compare(op, registers[b], registers[c], position)
            elif op in (TypedOp.EQ_B, TypedOp.NE_B):
                registers[a] = self._bool_compare(op, registers[b], registers[c], position)
            elif op in (
                TypedOp.EQ_MIXED,
                TypedOp.NE_MIXED,
                TypedOp.LT_MIXED,
                TypedOp.LE_MIXED,
                TypedOp.GT_MIXED,
                TypedOp.GE_MIXED,
            ):
                registers[a] = self._mixed_compare(op, registers[b], registers[c], position)
            elif op in (TypedOp.POS_I, TypedOp.NEG_I):
                registers[a] = self._int_unary(op, registers[b], position)
            elif op in (TypedOp.POS_F, TypedOp.NEG_F):
                registers[a] = self._float_unary(op, registers[b], position)
            elif op is TypedOp.NOT_B:
                operand = self._bool(registers[b], position)
                registers[a] = OortBool.get_bool_value(not operand.value)
            elif op is TypedOp.TO_FLOAT:
                registers[a] = self._to_float(registers[b], position)
            elif op is TypedOp.ADD_S:
                registers[a] = OortString(
                    self._string(registers[b], position).value
                    + self._string(registers[c], position).value
                )
            elif op in (
                TypedOp.EQ_S,
                TypedOp.NE_S,
                TypedOp.LT_S,
                TypedOp.LE_S,
                TypedOp.GT_S,
                TypedOp.GE_S,
            ):
                registers[a] = self._string_compare(op, registers[b], registers[c], position)
            elif op is TypedOp.NEW_LIST:
                registers[c] = OortList(registers[a : a + b])
            elif op is TypedOp.NEW_SET:
                registers[c] = OortSet(set(registers[a : a + b]))
            elif op is TypedOp.NEW_TUPLE:
                registers[c] = OortTuple(tuple(registers[a : a + b]))
            elif op is TypedOp.NEW_DICT:
                mapping = {
                    registers[a + 2 * index]: registers[a + 2 * index + 1] for index in range(b)
                }
                registers[c] = OortDict(mapping)
            elif op is TypedOp.NEW_ADT:
                try:
                    decl_index, ctor_index = self._constructors[b]
                except KeyError as exc:
                    raise OortTypeError("Invalid typed ADT constructor id.", position) from exc
                type_id = proto.register_types[c] if c < len(proto.register_types) else None
                if type_id is None:
                    raise OortTypeError("Typed ADT target has no static type.", position)
                adt_type = proto.types[type_id]
                if not isinstance(adt_type, AdtType):
                    raise OortTypeError("Typed ADT target is not an ADT type.", position)
                type_obj = self._adt_types.get(adt_runtime_name(adt_type))
                if type_obj is None:
                    raise OortTypeError(f"Unknown ADT type {adt_type}.", position)
                decl = program.adt_decls[decl_index]
                constructor = decl.constructors[ctor_index]
                registers[c] = OortADT(
                    type_obj,
                    constructor.name,
                    registers[a : a + constructor.arity],
                )
            elif op is TypedOp.ADT_TAG:
                value = registers[b]
                if type(value) is not OortADT:
                    raise OortTypeError("Typed ADT_TAG expects an ADT.", position)
                tag_decl_index = self._adt_by_name.get(value.type.name)
                if tag_decl_index is None:
                    raise OortTypeError("Unknown typed ADT value.", position)
                decl = program.adt_decls[tag_decl_index]
                registers[a] = OortInt(
                    next(
                        (
                            index
                            for index, constructor in enumerate(decl.constructors)
                            if constructor.name == value.variant
                        ),
                        -1,
                    )
                )
            elif op is TypedOp.ADT_FIELD:
                value = registers[b]
                if type(value) is not OortADT or not 0 <= c < len(value.values):
                    raise OortTypeError("Typed ADT_FIELD is out of range.", position)
                registers[a] = value.values[c]
            elif op is TypedOp.TUPLE_ITEM:
                value = registers[b]
                if type(value) is not OortTuple or not 0 <= c < len(value.value):
                    raise OortTypeError("Typed TUPLE_ITEM is out of range.", position)
                registers[a] = value.value[c]
            elif op in (TypedOp.EQ_ADT, TypedOp.NE_ADT):
                equal = self.interpreter.values_equal(registers[b], registers[c], position)
                if op is TypedOp.NE_ADT:
                    equal = not equal
                registers[a] = OortBool.get_bool_value(equal)
            elif op is TypedOp.GET_ITEM:
                registers[a] = self._get_item(registers[b], registers[c], position)
            elif op in (
                TypedOp.EQ_LIST,
                TypedOp.NE_LIST,
                TypedOp.EQ_TUPLE,
                TypedOp.NE_TUPLE,
                TypedOp.EQ_SET,
                TypedOp.NE_SET,
                TypedOp.EQ_DICT,
                TypedOp.NE_DICT,
            ):
                equal = self.interpreter.values_equal(registers[b], registers[c], position)
                if op in (
                    TypedOp.NE_LIST,
                    TypedOp.NE_TUPLE,
                    TypedOp.NE_SET,
                    TypedOp.NE_DICT,
                ):
                    equal = not equal
                registers[a] = OortBool.get_bool_value(equal)
            elif op is TypedOp.OPEN_ITER:
                registers[a] = self.interpreter.open_iterator(registers[b], position)
            elif op is TypedOp.ITER_NEXT:
                value, valid = self.interpreter.iterator_next(registers[b], position)
                registers[a] = self.runtime.null if value is None else value
                registers[c] = OortBool.get_bool_value(valid)
            elif op is TypedOp.SET_ITEM:
                container = registers[a]
                if type(container) is OortList:
                    if type(registers[b]) is not OortInt:
                        raise OortTypeError("Typed SetItem index must be Int.", position)
                    container[registers[b]] = registers[c]
                elif type(container) is OortDict:
                    container[registers[b]] = registers[c]
                else:
                    raise OortTypeError("Typed SetItem expects a List or Dict.", position)
            elif op is TypedOp.CONTAINS:
                registers[a] = OortBool.get_bool_value(
                    self._contains(registers[b], registers[c], position)
                )
            elif op is TypedOp.SLICE:
                start = registers[a + 1] if b & 1 else None
                stop = registers[a + 2] if b & 2 else None
                registers[c] = self._slice(registers[a], start, stop, position)
            elif op in (
                TypedOp.SET_UNION,
                TypedOp.SET_INTERSECT,
                TypedOp.SET_DIFFERENCE,
                TypedOp.SET_SYMMETRIC,
            ):
                registers[a] = self._set_operation(op, registers[b], registers[c], position)
            elif op is TypedOp.JMP:
                pc = bx
                continue
            elif op is TypedOp.JMP_FALSE:
                if not self._bool(registers[a], position).value:
                    pc = bx
                    continue
            elif op is TypedOp.JMP_TRUE:
                if self._bool(registers[a], position).value:
                    pc = bx
                    continue
            elif op is TypedOp.CALL:
                arguments = registers[a + 1 : a + 1 + b]
                registers[c] = self._call(program, registers[a], arguments, position)
            elif op is TypedOp.RET:
                return registers[a]
            else:  # pragma: no cover - exhaustive TypedOp set
                raise OortTypeError(f"Unknown typed opcode {op}.", position)
            pc += 1

        raise OortTypeError(
            f"Typed bytecode function '{proto.name}' fell off the end.", proto.positions[0]
        )

    # ------------------------------------------------------------------
    # Values and calls
    # ------------------------------------------------------------------

    def _wrap_constant(self, value: object) -> OortObject:
        if value is None:
            return self.runtime.null
        if type(value) is int:
            return OortInt(value)
        if isinstance(value, bool):
            return self.runtime.true if value else self.runtime.false
        if isinstance(value, float):
            return OortFloat(value)
        return self.runtime.host.from_host(value)

    def _load_global(self, proto: TypedProto, index: int, position: SourcePosition) -> Any:
        name = proto.constants[index]
        if not isinstance(name, str):
            raise OortTypeError("Invalid global name constant.", position)
        function = self.globals.get(name)
        if function is not None:
            return function
        entry = self.env.get(name)
        if entry is None:
            raise OortNameError(f"Unknown name '{name}'.", position)
        return entry.value

    def _call(
        self,
        program: TypedProgram,
        callee: Any,
        arguments: list[Any],
        position: SourcePosition,
    ) -> OortObject:
        if isinstance(callee, TypedCodeFunction):
            return self._invoke(program, callee.proto, arguments, position)
        if isinstance(callee, OortNativeFunction):
            return callee(self.interpreter, arguments, position)
        raise OortTypeError("Typed bytecode call target is not callable.", position)

    def _invoke(
        self,
        program: TypedProgram,
        proto: TypedProto,
        arguments: list[Any],
        position: SourcePosition,
    ) -> OortObject:
        if len(arguments) != len(proto.param_types):
            raise OortTypeError(
                f"Typed function '{proto.name}' expects {len(proto.param_types)} "
                f"arguments, got {len(arguments)}.",
                position,
            )
        registers: list[Any] = [self.runtime.null] * proto.register_count
        for index, (type_id, value) in enumerate(zip(proto.param_types, arguments)):
            expected = proto.types[type_id]
            self._guard(expected, value, proto.name, index, position)
            registers[index] = value
        return self._execute(program, proto, registers)

    @staticmethod
    def _guard(
        expected: IrTypeLike,
        value: Any,
        name: str,
        index: int,
        position: SourcePosition,
    ) -> None:
        if isinstance(expected, ContainerType):
            ok = (
                (expected.kind == "List" and type(value) is OortList)
                or (expected.kind == "Tuple" and type(value) is OortTuple)
                or (expected.kind == "Set" and type(value) is OortSet)
                or (expected.kind == "Dict" and type(value) is OortDict)
            )
        elif isinstance(expected, AdtType):
            ok = type(value) is OortADT and value.type.name == adt_runtime_name(expected)
        else:
            ok = (
                (expected is IrType.INT and type(value) is OortInt)
                or (expected is IrType.FLOAT and type(value) is OortFloat)
                or (expected is IrType.BOOL and type(value) is OortBool)
                or (expected is IrType.STRING and type(value) is OortString)
                or (expected is IrType.UNIT and type(value) is OortNull)
            )
        if not ok:
            raise OortTypeError(
                f"Typed bytecode guard failed for '{name}' argument {index}: expected {expected}.",
                position,
            )

    # ------------------------------------------------------------------
    # Typed operations (boxed values, exact static types)
    # ------------------------------------------------------------------

    @staticmethod
    def _int(value: Any, position: SourcePosition) -> OortInt:
        if type(value) is not OortInt:
            raise OortTypeError("Typed opcode expected Int.", position)
        return value

    @staticmethod
    def _float(value: Any, position: SourcePosition) -> OortFloat:
        if type(value) is not OortFloat:
            raise OortTypeError("Typed opcode expected Float.", position)
        return value

    @staticmethod
    def _bool(value: Any, position: SourcePosition) -> OortBool:
        if type(value) is not OortBool:
            raise OortTypeError("Typed opcode expected Bool.", position)
        return value

    def _int_binary(
        self,
        op: TypedOp,
        lhs: Any,
        rhs: Any,
        position: SourcePosition,
    ) -> OortObject:
        left = self._int(lhs, position).value
        right = self._int(rhs, position).value
        try:
            if op is TypedOp.ADD_I:
                return OortInt(left + right)
            if op is TypedOp.SUB_I:
                return OortInt(left - right)
            if op is TypedOp.MUL_I:
                return OortInt(left * right)
            if op is TypedOp.FLOORDIV_I:
                return OortInt(left // right)
            return OortInt(left % right)
        except ZeroDivisionError as exc:
            raise OortRuntimeError(str(exc), position) from exc

    def _float_binary(
        self,
        op: TypedOp,
        lhs: Any,
        rhs: Any,
        position: SourcePosition,
    ) -> OortObject:
        left = self._float(lhs, position).value
        right = self._float(rhs, position).value
        try:
            if op is TypedOp.ADD_F:
                return OortFloat(left + right)
            if op is TypedOp.SUB_F:
                return OortFloat(left - right)
            if op is TypedOp.MUL_F:
                return OortFloat(left * right)
            if op is TypedOp.DIV_F:
                return OortFloat(left / right)
            if op is TypedOp.FLOORDIV_F:
                return OortFloat(left // right)
            return OortFloat(left % right)
        except ZeroDivisionError as exc:
            raise OortRuntimeError(str(exc), position) from exc

    def _int_compare(
        self,
        op: TypedOp,
        lhs: Any,
        rhs: Any,
        position: SourcePosition,
    ) -> OortBool:
        left = self._int(lhs, position).value
        right = self._int(rhs, position).value
        result = {
            TypedOp.EQ_I: left == right,
            TypedOp.NE_I: left != right,
            TypedOp.LT_I: left < right,
            TypedOp.LE_I: left <= right,
            TypedOp.GT_I: left > right,
            TypedOp.GE_I: left >= right,
        }[op]
        return OortBool.get_bool_value(result)

    def _float_compare(
        self,
        op: TypedOp,
        lhs: Any,
        rhs: Any,
        position: SourcePosition,
    ) -> OortBool:
        left = self._float(lhs, position).value
        right = self._float(rhs, position).value
        result = {
            TypedOp.EQ_F: left == right,
            TypedOp.NE_F: left != right,
            TypedOp.LT_F: left < right,
            TypedOp.LE_F: left <= right,
            TypedOp.GT_F: left > right,
            TypedOp.GE_F: left >= right,
        }[op]
        return OortBool.get_bool_value(result)

    def _bool_compare(
        self,
        op: TypedOp,
        lhs: Any,
        rhs: Any,
        position: SourcePosition,
    ) -> OortBool:
        left = self._bool(lhs, position).value
        right = self._bool(rhs, position).value
        result = left == right if op is TypedOp.EQ_B else left != right
        return OortBool.get_bool_value(result)

    def _mixed_compare(
        self,
        op: TypedOp,
        lhs: Any,
        rhs: Any,
        position: SourcePosition,
    ) -> OortBool:
        left = self._number(lhs, position)
        right = self._number(rhs, position)
        if op is TypedOp.EQ_MIXED:
            result = left == right
        elif op is TypedOp.NE_MIXED:
            result = left != right
        elif op is TypedOp.LT_MIXED:
            result = left < right
        elif op is TypedOp.LE_MIXED:
            result = left <= right
        elif op is TypedOp.GT_MIXED:
            result = left > right
        else:
            result = left >= right
        return OortBool.get_bool_value(result)

    @staticmethod
    def _number(value: Any, position: SourcePosition) -> int | float:
        if type(value) is OortInt:
            return value.value
        if type(value) is OortFloat:
            return value.value
        raise OortTypeError("Typed mixed comparison expects Int or Float.", position)

    def _contains(self, container: Any, value: Any, position: SourcePosition) -> bool:
        if type(container) is OortList:
            return any(
                self.interpreter.values_equal(item, value, position) for item in container.value
            )
        if type(container) is OortTuple:
            return any(
                self.interpreter.values_equal(item, value, position) for item in container.value
            )
        if type(container) is OortSet:
            return value in container.value
        if type(container) is OortDict:
            return value in container.value
        if type(container) is OortString and type(value) is OortString:
            return value.value in container.value
        raise OortTypeError(
            f"Typed membership is not supported for {getattr(container, 'type', None)}.",
            position,
        )

    def _slice(
        self,
        container: Any,
        start: Any,
        stop: Any,
        position: SourcePosition,
    ) -> OortObject:
        def bound(value: Any) -> int | None:
            if value is None:
                return None
            if type(value) is not OortInt:
                raise OortTypeError("Typed slice bound must be Int.", position)
            return value.value

        begin = bound(start)
        end = bound(stop)
        if type(container) is OortList:
            return OortList(container.value[begin:end])
        if type(container) is OortTuple:
            return OortTuple(container.value[begin:end])
        if type(container) is OortString:
            return OortString(container.value[begin:end])
        raise OortTypeError("Typed slice source must be List, Tuple or String.", position)

    def _set_operation(
        self,
        op: TypedOp,
        lhs: Any,
        rhs: Any,
        position: SourcePosition,
    ) -> OortSet:
        if type(lhs) is not OortSet or type(rhs) is not OortSet:
            raise OortTypeError("Typed set operators require two Sets.", position)
        if op is TypedOp.SET_UNION:
            values = lhs.value | rhs.value
        elif op is TypedOp.SET_INTERSECT:
            values = lhs.value & rhs.value
        elif op is TypedOp.SET_DIFFERENCE:
            values = lhs.value - rhs.value
        else:
            values = lhs.value ^ rhs.value
        return OortSet(values)

    def _get_item(self, container: Any, index: Any, position: SourcePosition) -> OortObject:
        if type(container) is OortDict:
            try:
                return container[index]
            except (KeyError, TypeError) as exc:
                raise OortRuntimeError(str(exc), position) from exc
        if type(container) not in (OortList, OortTuple, OortString):
            raise OortTypeError("Typed indexing expects a List, Tuple, String or Dict.", position)
        if type(index) is not OortInt:
            raise OortTypeError("Typed index must be Int.", position)
        try:
            return container[index]
        except (IndexError, TypeError) as exc:
            raise OortRuntimeError(str(exc), position) from exc

    @staticmethod
    def _string(value: Any, position: SourcePosition) -> OortString:
        if type(value) is not OortString:
            raise OortTypeError("Typed opcode expected String.", position)
        return value

    def _string_compare(
        self,
        op: TypedOp,
        lhs: Any,
        rhs: Any,
        position: SourcePosition,
    ) -> OortBool:
        left = self._string(lhs, position).value
        right = self._string(rhs, position).value
        if op is TypedOp.EQ_S:
            result = left == right
        elif op is TypedOp.NE_S:
            result = left != right
        elif op is TypedOp.LT_S:
            result = left < right
        elif op is TypedOp.LE_S:
            result = left <= right
        elif op is TypedOp.GT_S:
            result = left > right
        else:
            result = left >= right
        return OortBool.get_bool_value(result)

    def _int_unary(self, op: TypedOp, operand: Any, position: SourcePosition) -> OortInt:
        value = self._int(operand, position).value
        return OortInt(-value if op is TypedOp.NEG_I else value)

    def _float_unary(self, op: TypedOp, operand: Any, position: SourcePosition) -> OortFloat:
        value = self._float(operand, position).value
        return OortFloat(-value if op is TypedOp.NEG_F else value)

    def _to_float(self, operand: Any, position: SourcePosition) -> OortFloat:
        if type(operand) is OortFloat:
            return operand
        return OortFloat(float(self._int(operand, position).value))


__all__ = ["TypedCodeFunction", "TypedCodeVM"]
