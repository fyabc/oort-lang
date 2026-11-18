#! /usr/bin/env python

"""Declaration context used by semantic checks."""

from enum import Enum


class OutsideDeclType(Enum):
    """Current outside declaration type."""

    NONE = 0  # global
    FUNCTION = 1  # free function
    CLASS = 2  # class
    METHOD = 3  # method
    METHOD_INIT = 4  # initializer
    CLASS_METHOD = 5  # static method

    @property
    def is_function(self) -> bool:
        return self in [
            OutsideDeclType.FUNCTION,
            OutsideDeclType.METHOD,
            OutsideDeclType.METHOD_INIT,
            OutsideDeclType.CLASS_METHOD,
        ]

    @property
    def is_method(self) -> bool:
        return self in [
            OutsideDeclType.METHOD,
            OutsideDeclType.METHOD_INIT,
            OutsideDeclType.CLASS_METHOD,
        ]
