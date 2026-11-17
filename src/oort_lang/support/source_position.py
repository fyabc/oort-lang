#! /usr/bin/env python

from typing import Any

from antlr4 import ParserRuleContext, Token
from antlr4.FileStream import FileStream


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

    def __init__(self, start: Token | None, stop: Token | None):
        self.start = start
        self.stop = stop
        self._filename = None

    @classmethod
    def from_context(cls, context: ParserRuleContext):
        if context is None:
            return cls(None, None)
        return cls(context.start, context.stop)

    @classmethod
    def from_token(cls, token: Token):
        return cls(token, token)

    @property
    def sort_key(self) -> Any:
        return self.start.tokenIndex

    @property
    def filename(self) -> str:
        if self._filename is None:
            if self.start is None and self.stop is None:
                self._filename = "<unknown>"
            token = self.start or self.stop
            token_stream = token.getInputStream()
            if isinstance(token_stream, FileStream):
                self._filename = token_stream.fileName
            else:
                self._filename = "<string>"
        return self._filename

    @property
    def start_line(self):
        return self.start.line

    @property
    def start_column(self):
        return self.start.column

    @property
    def stop_line(self):
        return self.stop.line

    @property
    def stop_column(self):
        return self.stop.column + len(self.stop.text) - 1
