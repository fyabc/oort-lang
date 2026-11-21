#! /usr/bin/env python

"""Oort's minimal standard library: collection helpers and native modules."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .io_module import build_io_module
from .math_module import build_math_module
from .os_module import build_os_module
from .string_module import build_string_module

if TYPE_CHECKING:
    from collections.abc import Callable

    from ..interpreter import ASTInterpreter
    from ..objects import OortModule

    NativeModuleFactory = Callable[[], OortModule]


NATIVE_MODULE_NAMES = frozenset({"io", "math", "os", "string"})


def native_module_factories(
    interpreter: ASTInterpreter,
) -> dict[str, NativeModuleFactory]:
    """Return lazy factories for the trusted built-in standard modules."""
    return {
        "io": lambda: build_io_module(interpreter),
        "math": lambda: build_math_module(interpreter),
        "os": lambda: build_os_module(interpreter),
        "string": lambda: build_string_module(interpreter),
    }
