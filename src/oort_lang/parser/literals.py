#! /usr/bin/env python

"""String literal parsing shared by declarations and expressions."""

import ast
import re

from antlr4 import ParserRuleContext, Token

from ..diagnostics.syntax_errors import UnsupportedSyntax
from ..source.source_position import SourcePosition

_STRING_PREFIX_RE = re.compile(r"^([A-Za-z]*)")


def parse_string_literal(ctx: ParserRuleContext | Token) -> str:
    """Parse a string literal.

    Only plain and raw string literals are supported for now. Formatted
    string literals are rejected explicitly instead of being evaluated by
    Python (which would execute arbitrary code at parse time).
    """
    text = ctx.getText()
    prefix_match = _STRING_PREFIX_RE.match(text)
    assert prefix_match is not None
    prefix = prefix_match.group(1).lower()
    position = (
        SourcePosition.from_context(ctx)
        if isinstance(ctx, ParserRuleContext)
        else SourcePosition.from_token(ctx)
    )
    if "f" in prefix:
        raise UnsupportedSyntax("Formatted string literals are not implemented yet.", position)
    # `ast.literal_eval` is safe: it only accepts Python literals.
    try:
        return ast.literal_eval(text)
    except (ValueError, SyntaxError) as e:
        raise UnsupportedSyntax(f"Invalid string literal: {e}", position) from e
