#! /usr/bin/env python

from antlr4 import Token
from antlr4.error.ErrorListener import ErrorListener

from ..source.input_info import InputInfo
from ..source.source_position import SourcePosition
from . import OortSyntaxError
from .error_handler import CompilerErrorHandler

# ANTLR wraps the text a failed lexer rule tried to match in this prefix.
_LEXER_ERROR_PREFIX = "token recognition error at: '"


class OortErrorListener(ErrorListener):
    """ErrorListener class integrated into ANTLR lexer and parser."""

    def __init__(self, error_handler: CompilerErrorHandler, input_info: InputInfo):
        self.error_handler = error_handler
        self.input_info = input_info

    def syntaxError(
        self,
        _recognizer,
        offendingSymbol: Token | None,
        line: int,
        column: int,
        msg: str,
        e,
    ):
        if offendingSymbol is not None:
            position = SourcePosition.from_token(offendingSymbol)
            if msg.startswith("no viable alternative at input"):
                # Replace useless error message.
                msg = "Invalid syntax"
        else:
            # Lexer notifications carry no token; classify them so the
            # message names the failure instead of a generic "invalid token".
            text = self._attempted_text(msg, line, column)
            position = SourcePosition.from_location(line, column, text[:1])
            msg = self._lexer_message(text, line, column)
        self.error_handler.add(OortSyntaxError(msg, position), self.input_info)

    def _lexer_message(self, text: str, line: int, column: int) -> str:
        """Classify a lexer failure by the text the failing rule tried to match.

        Follows the mainstream convention of naming the category (Python's
        "unterminated string literal", javac's "unclosed string literal",
        Python's "invalid character '…' (U+…)") rather than a generic
        "invalid token" (the V8 style).
        """
        if text.startswith(("'", '"')):
            quote = text[0]
            prefix = self._line_prefix(line, column, 2)
            # A failing triple quote is reported at its third quote: the
            # first two already matched as an empty short string.
            if prefix == quote * 2:
                return "Unterminated triple-quoted string literal"
            return "Unterminated string literal"
        if text:
            return f"Invalid character {text[0]!r} (U+{ord(text[0]):04X})"
        return "Invalid token"

    def _attempted_text(self, msg: str, line: int, column: int) -> str:
        """Extract the text the failing lexer rule tried to match."""
        if (
            msg.startswith(_LEXER_ERROR_PREFIX)
            and msg.endswith("'")
            and len(msg) > len(_LEXER_ERROR_PREFIX)
        ):
            return msg[len(_LEXER_ERROR_PREFIX) : -1]
        # Older ANTLR wording or unexpected shapes: fall back to the source
        # character at the reported position.
        lines = self.input_info.get_lines()
        if 0 < line <= len(lines):
            line_text = lines[line - 1]
            if column < len(line_text):
                return line_text[column]
        return ""

    def _line_prefix(self, line: int, column: int, length: int) -> str:
        """Return up to `length` characters before (line, column)."""
        lines = self.input_info.get_lines()
        if 0 < line <= len(lines):
            return lines[line - 1][max(0, column - length) : column]
        return ""
