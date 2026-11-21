#! /usr/bin/env python

"""Language dialects and the `#lang` module directive.

A module belongs to exactly one dialect. Shared frontend components (lexer,
parser, AST, diagnostics) stay dialect-agnostic; dialect-specific rules are
selected through :class:`DialectConfig` and enforced in semantic analysis.

See ``docs/proposals/0001-feature-layers-and-dialects.md``.
"""

import dataclasses
import re
from collections.abc import Callable

from .operator_defs import OperatorTable

LANG_DIRECTIVE = "#lang"
DEFAULT_DIALECT_NAME = "oort-object"

_BOM = chr(0xFEFF)
_LANG_LINE_RE = re.compile(r"^#lang(?:[ \t]+([A-Za-z][A-Za-z0-9_-]*))?[ \t]*$")


@dataclasses.dataclass(frozen=True)
class DialectFeatures:
    """Feature switches consumed by shared semantic analysis."""

    #: Whether `var` / `val` declarations are allowed directly in a class body.
    #: Dynamic `oort-object` keeps instances as open field bags, so class-body
    #: declarations are rejected (OP 0007); static dialects may use them for
    #: slots once those are implemented.
    class_body_vars: bool = False
    #: Whether semantic analysis runs the independent static checker.
    type_checking: bool = False
    #: Whether ADT declarations and `match` are enabled.
    adt: bool = False


@dataclasses.dataclass(frozen=True)
class DialectConfig:
    """Configuration of one language dialect."""

    name: str
    description: str
    implemented: bool
    features: DialectFeatures
    #: Factory for the Pratt operator table of this dialect. A fresh table is
    #: created per compilation so that dialect-specific extensions cannot leak
    #: between compilations.
    operator_table_factory: Callable[[], OperatorTable] = dataclasses.field(
        default=OperatorTable.default, repr=False, compare=False
    )

    def new_operator_table(self) -> OperatorTable:
        return self.operator_table_factory()


OORT_OBJECT = DialectConfig(
    name=DEFAULT_DIALECT_NAME,
    description="Dynamic objects, open field bags and dynamic dispatch.",
    implemented=True,
    features=DialectFeatures(class_body_vars=False),
)

OORT_CORE = DialectConfig(
    name="oort-core",
    description="Static core with type checking, ADTs, pattern matching and slots.",
    implemented=True,
    features=DialectFeatures(class_body_vars=True, type_checking=True, adt=True),
)

DIALECTS: dict[str, DialectConfig] = {config.name: config for config in (OORT_OBJECT, OORT_CORE)}

DEFAULT_DIALECT = OORT_OBJECT


def lookup_dialect(name: str) -> DialectConfig | None:
    """Look up a dialect by its exact, case-sensitive name."""
    return DIALECTS.get(name)


def known_dialect_names() -> list[str]:
    """Names accepted by `#lang`, including dialects that are not implemented."""
    return list(DIALECTS)


@dataclasses.dataclass(frozen=True)
class LangDirective:
    """Result of scanning a module for a `#lang` directive."""

    dialect_name: str | None = None
    error: str | None = None
    line: int = 1
    column: int = 0
    text: str = ""

    @property
    def has_directive(self) -> bool:
        return self.dialect_name is not None or self.error is not None


def _looks_like_lang_line(line: str) -> bool:
    """Whether a line is intended as a `#lang` directive.

    `#language` or `#langfoo` are ordinary comments; only `#lang` followed by
    whitespace or the end of the line counts.
    """
    return line == LANG_DIRECTIVE or line.startswith((LANG_DIRECTIVE + " ", LANG_DIRECTIVE + "\t"))


def parse_lang_directive(source: str) -> LangDirective:
    """Find the module dialect directive.

    The directive must start at column 0 of the first line (optionally after a
    UTF-8 BOM). A `#lang` line anywhere else is reported instead of being
    silently ignored as a comment. The directive itself remains a comment for
    the lexer, so line numbers are unaffected.
    """
    if source.startswith(_BOM):
        source = source[len(_BOM) :]

    lines = source.splitlines()
    if not lines:
        return LangDirective()

    first = lines[0]
    if _looks_like_lang_line(first):
        match = _LANG_LINE_RE.match(first)
        if match is not None and match.group(1) is not None:
            return LangDirective(
                dialect_name=match.group(1),
                line=1,
                column=0,
                text=first,
            )
        return LangDirective(
            error="Invalid `#lang` directive: expected `#lang <dialect>`.",
            line=1,
            column=0,
            text=first,
        )

    for line_number, line in enumerate(lines[1:], start=2):
        if _looks_like_lang_line(line):
            return LangDirective(
                error="The `#lang` directive must be the first line of the module.",
                line=line_number,
                column=0,
                text=line,
            )

    return LangDirective()
