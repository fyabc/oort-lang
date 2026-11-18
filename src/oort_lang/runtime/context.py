#! /usr/bin/env python

"""Active-runtime context shared by the object model."""

import contextlib
import contextvars
from collections.abc import Iterator
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .type_system import Runtime

_CURRENT_RUNTIME: "contextvars.ContextVar[Runtime | None]" = contextvars.ContextVar(
    "oort_runtime", default=None
)


def get_runtime() -> "Runtime":
    """Get the active runtime, or fail loudly outside an evaluation."""
    runtime = _CURRENT_RUNTIME.get()
    if runtime is None:
        raise RuntimeError("No active Oort runtime")
    return runtime


@contextlib.contextmanager
def activate_runtime(runtime: "Runtime") -> Iterator["Runtime"]:
    """Make `runtime` current for object construction and dispatch."""
    token = _CURRENT_RUNTIME.set(runtime)
    try:
        yield runtime
    finally:
        _CURRENT_RUNTIME.reset(token)
