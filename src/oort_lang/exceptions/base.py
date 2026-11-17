#! /usr/bin/env python

from ..support.source_position import SourcePosition


class OortException(Exception):
    def __init__(self, msg: str, position: SourcePosition, recoverable: bool = True):
        self.msg = msg
        self.position = position
        self.recoverable: bool = recoverable
        self.traceback: list[tuple[str, SourcePosition]] = []

    def add_traceback(self, note: str, position: SourcePosition):
        self.traceback.append((note, position))


class OortSyntaxError(OortException):
    pass


class OortSyntaxWarning(OortException):
    pass
