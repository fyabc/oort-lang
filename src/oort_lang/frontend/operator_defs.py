#! /usr/bin/env python

"""Operator definitions."""

from dataclasses import dataclass
from enum import Enum


class Arity(Enum):
    PREFIX = 1
    INFIX = 2


class Associativity(Enum):
    LEFT = 1
    RIGHT = 2


@dataclass
class OperatorDef:
    symbol: str
    arity: Arity
    precedence: int
    associativity: Associativity


class OperatorTable:
    """Scoped operator table."""

    DEFAULT_OP_DEF = {
        Arity.PREFIX: OperatorDef("<DEFAULT>", Arity.PREFIX, 800, Associativity.RIGHT),
        Arity.INFIX: OperatorDef("<DEFAULT>", Arity.INFIX, 500, Associativity.LEFT),
    }

    def __init__(self, parent: "OperatorTable" = None):
        self.parent = parent
        self.operators: dict[tuple[str, Arity], OperatorDef] = {}

    def get(self, symbol: str, arity: Arity, default: bool = False) -> OperatorDef | None:
        table = self
        while table:
            op_def = table.operators.get((symbol, arity), None)
            if op_def:
                return op_def
            table = table.parent
        if default:
            return self.DEFAULT_OP_DEF[arity]
        else:
            return None

    @classmethod
    def default(cls) -> "OperatorTable":
        """Get the default operator table."""
        table = cls(None)
        table.operators = {
            ("await", Arity.PREFIX): OperatorDef("await", Arity.PREFIX, 1000, Associativity.RIGHT),
            ("not", Arity.PREFIX): OperatorDef("not", Arity.PREFIX, 100, Associativity.RIGHT),
            ("**", Arity.INFIX): OperatorDef("**", Arity.INFIX, 900, Associativity.RIGHT),
            ("+", Arity.PREFIX): OperatorDef("+", Arity.PREFIX, 800, Associativity.RIGHT),
            ("-", Arity.PREFIX): OperatorDef("-", Arity.PREFIX, 800, Associativity.RIGHT),
            ("~", Arity.PREFIX): OperatorDef("~", Arity.PREFIX, 800, Associativity.RIGHT),
            ("*", Arity.INFIX): OperatorDef("*", Arity.INFIX, 700, Associativity.LEFT),
            ("/", Arity.INFIX): OperatorDef("/", Arity.INFIX, 700, Associativity.LEFT),
            ("//", Arity.INFIX): OperatorDef("//", Arity.INFIX, 700, Associativity.LEFT),
            ("%", Arity.INFIX): OperatorDef("%", Arity.INFIX, 700, Associativity.LEFT),
            ("+", Arity.INFIX): OperatorDef("+", Arity.INFIX, 600, Associativity.LEFT),
            ("-", Arity.INFIX): OperatorDef("-", Arity.INFIX, 600, Associativity.LEFT),
            ("<<", Arity.INFIX): OperatorDef("<<", Arity.INFIX, 400, Associativity.LEFT),
            (">>", Arity.INFIX): OperatorDef(">>", Arity.INFIX, 400, Associativity.LEFT),
            (">", Arity.INFIX): OperatorDef(">", Arity.INFIX, 300, Associativity.LEFT),
            ("<", Arity.INFIX): OperatorDef("<", Arity.INFIX, 300, Associativity.LEFT),
            (">=", Arity.INFIX): OperatorDef(">=", Arity.INFIX, 300, Associativity.LEFT),
            ("<=", Arity.INFIX): OperatorDef("<=", Arity.INFIX, 300, Associativity.LEFT),
            ("in", Arity.INFIX): OperatorDef("in", Arity.INFIX, 300, Associativity.LEFT),
            ("!in", Arity.INFIX): OperatorDef("!in", Arity.INFIX, 300, Associativity.LEFT),
            ("is", Arity.INFIX): OperatorDef("is", Arity.INFIX, 300, Associativity.LEFT),
            ("!is", Arity.INFIX): OperatorDef("!is", Arity.INFIX, 300, Associativity.LEFT),
            ("==", Arity.INFIX): OperatorDef("==", Arity.INFIX, 200, Associativity.LEFT),
            ("!=", Arity.INFIX): OperatorDef("!=", Arity.INFIX, 200, Associativity.LEFT),
            ("&", Arity.INFIX): OperatorDef("&", Arity.INFIX, 180, Associativity.LEFT),
            ("^", Arity.INFIX): OperatorDef("^", Arity.INFIX, 160, Associativity.LEFT),
            ("|", Arity.INFIX): OperatorDef("|", Arity.INFIX, 140, Associativity.LEFT),
            ("and", Arity.INFIX): OperatorDef("and", Arity.INFIX, 90, Associativity.LEFT),
            ("or", Arity.INFIX): OperatorDef("or", Arity.INFIX, 80, Associativity.LEFT),
        }
        return table
