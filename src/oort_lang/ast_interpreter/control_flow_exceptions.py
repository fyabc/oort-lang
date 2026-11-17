#! /usr/bin/env python

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .objects import OortObject


# Control flow exceptions.
class OortReturn(Exception):
    """Control flow exception for `return` statement."""

    def __init__(self, value: "OortObject"):
        self.value = value


class OortBreak(Exception):
    """Control flow exception for `break` statement."""


class OortContinue(Exception):
    """Control flow exception for `continue` statement."""
