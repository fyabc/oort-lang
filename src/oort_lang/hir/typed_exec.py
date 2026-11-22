#! /usr/bin/env python

"""Typed HIR interpreter (M2 of design 15).

Executes the restricted scalar ``TypedModule`` directly in Python. It reuses
the existing runtime values and operator implementation so output matches the
tree-walking interpreter and bytecode VM for the accepted subset. This is a
research/validation interpreter, not a long-term backend: M3 moves to typed
bytecode and unboxed values.
"""

from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING, Any

from ..diagnostics.runtime_errors import OortNameError, OortTypeError
from ..runtime.environment import Environment
from ..runtime.functions import OortNativeFunction
from ..runtime.objects import OortBool, OortFloat, OortInt, OortObject
from .nodes import (
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

if TYPE_CHECKING:
    from ..runtime.interpreter import ASTInterpreter
    from ..source.source_position import SourcePosition
    from .typed import TypedFunction, TypedModule


@dataclasses.dataclass(frozen=True, slots=True)
class TypedFunctionValue:
    """A typed function bound in the typed interpreter's globals."""

    function: TypedFunction


class TypedInterpreter:
    def __init__(self, interpreter: ASTInterpreter):
        self.interpreter = interpreter
        self.runtime = interpreter.runtime
        self.globals: dict[str, TypedFunctionValue] = {}
        self.env = Environment(
            outer=interpreter.builtins_env,
            name="<typed>",
            allow_redefine=True,
            is_module_root=True,
        )

    def run(self, module: TypedModule) -> OortObject:
        for function in module.functions:
            self.globals[function.hir.name] = TypedFunctionValue(function)
        registers: list[Any] = [self.runtime.null] * module.main.hir.local_count
        with self.runtime.activate():
            return self._execute(module, module.main, registers)

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def _execute(
        self,
        module: TypedModule,
        function: TypedFunction,
        registers: list[Any],
    ) -> OortObject:
        code = function.hir.code
        labels = {
            instruction.name: index
            for index, instruction in enumerate(code)
            if isinstance(instruction, Label)
        }
        pc = 0
        while pc < len(code):
            instruction = code[pc]
            if isinstance(instruction, LoadConst):
                registers[instruction.dst] = self._wrap_constant(instruction.value)
                pc += 1
            elif isinstance(instruction, LoadLocal):
                registers[instruction.dst] = registers[instruction.slot]
                pc += 1
            elif isinstance(instruction, StoreLocal):
                registers[instruction.slot] = registers[instruction.src]
                pc += 1
            elif isinstance(instruction, LoadGlobal):
                registers[instruction.dst] = self._load_global(instruction, instruction.name)
                pc += 1
            elif isinstance(instruction, Move):
                registers[instruction.dst] = registers[instruction.src]
                pc += 1
            elif isinstance(instruction, BinOp):
                registers[instruction.dst] = self._binary(
                    instruction,
                    registers[instruction.lhs],
                    registers[instruction.rhs],
                )
                pc += 1
            elif isinstance(instruction, UnOp):
                registers[instruction.dst] = self._unary(
                    instruction,
                    registers[instruction.operand],
                )
                pc += 1
            elif isinstance(instruction, Label):
                pc += 1
            elif isinstance(instruction, Jump):
                pc = self._jump(labels, instruction.target, instruction)
            elif isinstance(instruction, JumpIfFalse):
                pc = (
                    self._jump(labels, instruction.target, instruction)
                    if not self._truth(registers[instruction.src], instruction)
                    else pc + 1
                )
            elif isinstance(instruction, JumpIfTrue):
                pc = (
                    self._jump(labels, instruction.target, instruction)
                    if self._truth(registers[instruction.src], instruction)
                    else pc + 1
                )
            elif isinstance(instruction, DefineFunction):
                pc += 1
            elif isinstance(instruction, FreshLocals):
                for slot in instruction.slots:
                    registers[slot] = self.runtime.null
                pc += 1
            elif isinstance(instruction, Call):
                arguments = [registers[register] for register in instruction.args]
                registers[instruction.dst] = self._call(
                    module,
                    registers[instruction.callee],
                    arguments,
                    instruction.position,
                )
                pc += 1
            elif isinstance(instruction, Return):
                return registers[instruction.src]
            elif isinstance(instruction, StoreGlobal):
                raise OortTypeError(
                    "Typed HIR does not support global stores.",
                    instruction.position,
                )
            else:
                raise OortTypeError(
                    f"Typed HIR cannot execute {type(instruction).__name__}.",
                    instruction.position,
                )
        raise OortTypeError(
            f"Typed function '{function.hir.name}' fell off the end.",
            function.hir.position,
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

    def _load_global(self, instruction: Instruction, name: str) -> Any:
        function = self.globals.get(name)
        if function is not None:
            return function
        entry = self.env.get(name)
        if entry is None:
            raise OortNameError(f"Unknown name '{name}'.", instruction.position)
        return entry.value

    def _call(
        self,
        module: TypedModule,
        callee: Any,
        arguments: list[Any],
        position: SourcePosition,
    ) -> OortObject:
        if isinstance(callee, TypedFunctionValue):
            function = callee.function
            if len(arguments) != len(function.hir.params):
                raise OortTypeError(
                    f"Typed function '{function.hir.name}' expects "
                    f"{len(function.hir.params)} arguments, got {len(arguments)}.",
                    position,
                )
            registers: list[Any] = [self.runtime.null] * function.hir.local_count
            for index, argument in enumerate(arguments):
                registers[index] = argument
            return self._execute(module, function, registers)
        if isinstance(callee, OortNativeFunction):
            return callee(self.interpreter, arguments, position)
        raise OortTypeError("Typed HIR call target is not callable.", position)

    def _binary(self, instruction: BinOp, lhs: Any, rhs: Any) -> OortObject:
        return self.interpreter.apply_binary(
            instruction.op,
            lhs,
            rhs,
            instruction.position,
            env=self.env,
        )

    def _unary(self, instruction: UnOp, operand: Any) -> OortObject:
        return self.interpreter.apply_unary(
            instruction.op,
            operand,
            instruction.position,
            env=self.env,
        )

    def _truth(self, value: Any, instruction: Instruction) -> bool:
        if isinstance(value, OortBool):
            return value.value
        raise OortTypeError("Typed HIR branch condition is not Bool.", instruction.position)

    @staticmethod
    def _jump(
        labels: dict[str, int],
        target: str,
        instruction: Instruction,
    ) -> int:
        index = labels.get(target)
        if index is None:
            raise OortTypeError(
                f"Typed HIR label '{target}' is missing.",
                instruction.position,
            )
        return index


__all__ = ["TypedFunctionValue", "TypedInterpreter"]
