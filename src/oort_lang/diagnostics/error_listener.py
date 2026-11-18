#! /usr/bin/env python

from antlr4 import Token
from antlr4.error.ErrorListener import ErrorListener

from ..source.input_info import InputInfo
from ..source.source_position import SourcePosition
from . import OortSyntaxError
from .error_handler import CompilerErrorHandler


class OortErrorListener(ErrorListener):
    """ErrorListener class integrated into ANTLR parser."""

    def __init__(self, error_handler: CompilerErrorHandler, input_info: InputInfo):
        self.error_handler = error_handler
        self.input_info = input_info

    def syntaxError(self, _recognizer, offendingSymbol: Token, line: int, column: int, msg: str, e):
        if msg.startswith("no viable alternative at input"):
            # Replace useless error message.
            msg = "Invalid syntax"
        self.error_handler.add(
            OortSyntaxError(msg, SourcePosition.from_token(offendingSymbol)),
            self.input_info,
        )
