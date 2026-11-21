#! /usr/bin/env python

from antlr4 import Token
from antlr4.error.ErrorListener import ErrorListener

from ..source.input_info import InputInfo
from ..source.source_position import SourcePosition
from . import OortSyntaxError
from .error_handler import CompilerErrorHandler


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
        else:
            # Lexer errors carry no token; point at the offending character.
            position = SourcePosition.from_location(
                line,
                column,
                self._offending_text(line, column),
            )
        if msg.startswith("no viable alternative at input"):
            # Replace useless error message.
            msg = "Invalid syntax"
        elif msg.startswith("token recognition error"):
            msg = "Invalid token"
        self.error_handler.add(OortSyntaxError(msg, position), self.input_info)

    def _offending_text(self, line: int, column: int) -> str:
        """Return the source character a lexer error points at, if any."""
        lines = self.input_info.get_lines()
        if 0 < line <= len(lines):
            text = lines[line - 1]
            if column < len(text):
                return text[column]
        return ""
