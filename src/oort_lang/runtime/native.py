#! /usr/bin/env python

"""Native call modes and the context handed to higher-order native functions."""

from __future__ import annotations

import dataclasses
from enum import Enum, auto
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable

    from ..source.source_position import SourcePosition
    from .interpreter import ASTInterpreter
    from .objects import OortObject


class NativeMode(Enum):
    """How `OortNativeFunction` marshals arguments and results.

    HOST is for host-specific functions (operators, math, string); VALUE works
    on Oort values and lets the host bridge wrap the result; CONTEXT also gets
    a `NativeContext` to call Oort callables and apply Oort operators.
    """

    HOST = auto()
    VALUE = auto()
    CONTEXT = auto()


@dataclasses.dataclass(frozen=True)
class NativeContext:
    """Language operations available to a CONTEXT-mode native function."""

    interpreter: ASTInterpreter
    position: SourcePosition | None = None

    def call(self, func: OortObject, args: Iterable[OortObject]) -> OortObject:
        return self.interpreter.call_value(func, list(args), self.position)

    def truthy(self, value: OortObject) -> bool:
        return self.interpreter.is_truthy(value)

    def iterate(self, value: OortObject) -> list[OortObject]:
        return self.interpreter.iter_values(value, self.position)

    def binary(self, symbol: str, lhs: OortObject, rhs: OortObject) -> OortObject:
        return self.interpreter.apply_operator(symbol, lhs, rhs, self.position)

    def equal(self, lhs: OortObject, rhs: OortObject) -> bool:
        """Oort value equality, recursive through builtin containers."""
        return self.interpreter.values_equal(lhs, rhs, self.position)

    def contains(self, container: OortObject, item: OortObject) -> bool:
        """Sequence membership using Oort value equality."""
        return self.interpreter.sequence_contains(container, item, self.position)
