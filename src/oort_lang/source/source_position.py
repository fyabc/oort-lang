#! /usr/bin/env python

from typing import Any

from antlr4 import ParserRuleContext, Token
from antlr4.FileStream import FileStream
from antlr4.Token import CommonToken


class AbstractSourcePosition:
    """Abstract source code position."""

    @property
    def sort_key(self) -> Any:
        """Sort key of position."""
        raise NotImplementedError()

    @property
    def filename(self) -> str:
        """Source file name."""
        raise NotImplementedError()

    @property
    def start_line(self) -> int:
        """Start line number."""
        raise NotImplementedError()

    @property
    def start_column(self) -> int | None:
        """Start column number (if available)."""
        raise NotImplementedError()

    @property
    def stop_line(self) -> int:
        """Stop line number."""
        raise NotImplementedError()

    @property
    def stop_column(self) -> int | None:
        """Stop column number (if available)."""
        raise NotImplementedError()

    def __str__(self):
        if self.start_column is None:
            return f"{self.filename}:{self.start_line}"
        else:
            return f"{self.filename}:{self.start_line}:{self.start_column + 1}"


class SourcePosition(AbstractSourcePosition):
    """Source code position."""

    def __init__(self, start: Token | None, stop: Token | None, filename: str | None = None):
        self.start = start
        self.stop = stop
        self._filename = filename

    @classmethod
    def from_context(cls, context: ParserRuleContext):
        if context is None:
            return cls(None, None)
        return cls(context.start, context.stop)

    @classmethod
    def from_token(cls, token: Token):
        return cls(token, token)

    @classmethod
    def from_location(cls, line: int, column: int, text: str, filename: str | None = None):
        """Build a position for diagnostics that have no lexer token.

        Used for errors detected before lexing, such as an invalid `#lang`
        directive.
        """
        token = CommonToken()
        token.line = line
        token.column = column
        token.text = text
        return cls(token, token, filename=filename)

    @property
    def sort_key(self) -> Any:
        assert self.start is not None
        return self.start.tokenIndex

    @property
    def filename(self) -> str:
        if self._filename is None:
            if self.start is None and self.stop is None:
                self._filename = "<unknown>"
                return self._filename
            token = self.start or self.stop
            assert token is not None
            token_stream = token.getInputStream()
            if isinstance(token_stream, FileStream):
                self._filename = token_stream.fileName
            else:
                self._filename = "<string>"
        return self._filename

    @property
    def start_line(self) -> int:
        assert self.start is not None
        return self.start.line

    @property
    def start_column(self) -> int:
        assert self.start is not None
        return self.start.column

    @property
    def stop_line(self) -> int:
        assert self.stop is not None
        return self.stop.line

    @property
    def stop_column(self) -> int:
        assert self.stop is not None
        return self.stop.column + len(self.stop.text) - 1
