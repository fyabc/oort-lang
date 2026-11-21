#! /usr/bin/env python

"""Operator definitions."""

from dataclasses import dataclass
from enum import Enum

# Characters allowed in user-defined operators. Keep in sync with `USER_OP`
# in `grammars/Oort.g4`.
USER_OPERATOR_CHARS = frozenset("!%&*+-/<=>?^|~")

# Built-in operators that may be overloaded. `and`, `or`, `not`, `is` and
# `!is` are deliberately excluded: they are short-circuit, truthiness or
# identity operations and cannot be dispatched to user code.
BUILTIN_UNARY_OPERATORS = frozenset({"+", "-", "~"})
BUILTIN_BINARY_OPERATORS = frozenset(
    {
        "+",
        "-",
        "*",
        "/",
        "//",
        "%",
        "**",
        "<<",
        ">>",
        "&",
        "|",
        "^",
        "==",
        "!=",
        "<",
        "<=",
        ">",
        ">=",
        "in",
        "!in",
    }
)
RESERVED_OPERATOR_SYMBOLS = frozenset({"and", "or", "not", "is", "!is", "await", "=", "=>"})

# Square brackets are not Pratt operators, but reuse the operator-method
# machinery for subscript get/set. The value is the parameter count in
# addition to the receiver: "[]" takes an index, "[]=" takes index + value.
SPECIAL_OPERATOR_ARITY = {"[]": 1, "[]=": 2}


def validate_operator_definition(symbol: str, operand_count: int) -> str | None:
    """Validate an operator method definition.

    Returns an error message, or None if the definition is valid.
    """
    if not symbol:
        return "Operator symbol cannot be empty."

    special_arity = SPECIAL_OPERATOR_ARITY.get(symbol)
    if special_arity is not None:
        if operand_count != special_arity + 1:
            return f"Operator {symbol!r} takes exactly {special_arity} parameter(s)."
        return None

    if symbol in RESERVED_OPERATOR_SYMBOLS:
        return f"Operator {symbol!r} cannot be overloaded."

    is_builtin = symbol in BUILTIN_UNARY_OPERATORS or symbol in BUILTIN_BINARY_OPERATORS
    if not is_builtin and not all(char in USER_OPERATOR_CHARS for char in symbol):
        return f"Invalid operator symbol {symbol!r}."

    if operand_count not in (1, 2):
        return "An operator method takes at most one parameter."

    if is_builtin:
        allowed = set()
        if symbol in BUILTIN_UNARY_OPERATORS:
            allowed.add(1)
        if symbol in BUILTIN_BINARY_OPERATORS:
            allowed.add(2)
        if operand_count not in allowed:
            arity = "unary" if operand_count == 1 else "binary"
            return f"Operator {symbol!r} cannot be defined as a {arity} operator."

    return None


class Arity(Enum):
    PREFIX = 1
    INFIX = 2


class Associativity(Enum):
    LEFT = 1
    RIGHT = 2
    NONE = 3  # Non-associative: chaining at the same precedence is an error.


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

    def __init__(self, parent: "OperatorTable | None" = None):
        self.parent = parent
        self.operators: dict[tuple[str, Arity], OperatorDef] = {}

    def get(self, symbol: str, arity: Arity, default: bool = False) -> OperatorDef | None:
        table: OperatorTable | None = self
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
            (">", Arity.INFIX): OperatorDef(">", Arity.INFIX, 300, Associativity.NONE),
            ("<", Arity.INFIX): OperatorDef("<", Arity.INFIX, 300, Associativity.NONE),
            (">=", Arity.INFIX): OperatorDef(">=", Arity.INFIX, 300, Associativity.NONE),
            ("<=", Arity.INFIX): OperatorDef("<=", Arity.INFIX, 300, Associativity.NONE),
            ("in", Arity.INFIX): OperatorDef("in", Arity.INFIX, 300, Associativity.NONE),
            ("!in", Arity.INFIX): OperatorDef("!in", Arity.INFIX, 300, Associativity.NONE),
            ("is", Arity.INFIX): OperatorDef("is", Arity.INFIX, 300, Associativity.NONE),
            ("!is", Arity.INFIX): OperatorDef("!is", Arity.INFIX, 300, Associativity.NONE),
            ("==", Arity.INFIX): OperatorDef("==", Arity.INFIX, 300, Associativity.NONE),
            ("!=", Arity.INFIX): OperatorDef("!=", Arity.INFIX, 300, Associativity.NONE),
            ("&", Arity.INFIX): OperatorDef("&", Arity.INFIX, 340, Associativity.LEFT),
            ("^", Arity.INFIX): OperatorDef("^", Arity.INFIX, 330, Associativity.LEFT),
            ("|", Arity.INFIX): OperatorDef("|", Arity.INFIX, 320, Associativity.LEFT),
            ("and", Arity.INFIX): OperatorDef("and", Arity.INFIX, 90, Associativity.LEFT),
            ("or", Arity.INFIX): OperatorDef("or", Arity.INFIX, 80, Associativity.LEFT),
            # Function-type arrow: `Int -> Int -> Int` groups to the right.
            ("->", Arity.INFIX): OperatorDef("->", Arity.INFIX, 50, Associativity.RIGHT),
        }
        return table
