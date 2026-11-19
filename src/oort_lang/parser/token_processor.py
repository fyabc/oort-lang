#! /usr/bin/env python

"""Host-independent token post-processing between the lexer and parser.

The grammar no longer tracks brackets or filters newlines. This module does
both on a plain token list, so the grammar stays portable and the REPL can ask
whether the current input is complete without touching lexer internals.

Rules, matching the historical lexer behavior:

- a newline inside any bracket is ignored, except when the innermost bracket
  is a code block ``{`` (statements inside a block still separate by newline);
- line escapes (``\\`` + newline) are removed for the parser and mark a
  trailing escape as incomplete input;
- unmatched closing brackets are passed through unchanged so the parser
  reports a normal syntax error instead of the lexer crashing.
"""

from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING

from antlr4 import Lexer, Token

from .grammar.OortLexer import OortLexer

if TYPE_CHECKING:
    from collections.abc import Iterable

_OPEN_TO_CLOSE = {
    OortLexer.LPA: OortLexer.RPA,
    OortLexer.LBK: OortLexer.RBK,
    OortLexer.AT_LBK: OortLexer.RBK,
    OortLexer.LDICT_LITERAL: OortLexer.RDICT_LITERAL,
    OortLexer.LSET_LITERAL: OortLexer.RSET_LITERAL,
    OortLexer.LBC: OortLexer.RBC,
}
_CLOSERS = frozenset(_OPEN_TO_CLOSE.values())


@dataclasses.dataclass(frozen=True)
class TokenizedInput:
    """Filtered tokens plus the completeness information the REPL needs."""

    tokens: list[Token]
    bracket_depth: int
    incomplete: bool


def process_tokens(tokens: Iterable[Token]) -> TokenizedInput:
    """Filter newlines/line escapes according to bracket nesting."""
    stack: list[int] = []
    kept: list[Token] = []
    last_significant: Token | None = None

    for token in tokens:
        token_type = token.type

        if token_type == Token.EOF:
            kept.append(token)
            continue

        if token_type == OortLexer.LINE_ESCAPE:
            # The parser never sees line escapes; remember whether the input
            # ends with one for the REPL's completeness check.
            last_significant = token
            continue

        if token_type == OortLexer.NEWLINE and stack and stack[-1] != OortLexer.LBC:
            continue

        kept.append(token)

        if token_type in _OPEN_TO_CLOSE:
            stack.append(token_type)
        elif token_type in _CLOSERS:
            if stack and _OPEN_TO_CLOSE[stack[-1]] == token_type:
                stack.pop()

        last_significant = token

    incomplete = bool(stack) or (
        last_significant is not None and last_significant.type == OortLexer.LINE_ESCAPE
    )
    return TokenizedInput(tokens=kept, bracket_depth=len(stack), incomplete=incomplete)


def tokenize(lexer: Lexer) -> TokenizedInput:
    """Run a lexer to EOF and post-process its tokens."""
    tokens: list[Token] = []
    while True:
        token = lexer.nextToken()
        tokens.append(token)
        if token.type == Token.EOF:
            break
    return process_tokens(tokens)
