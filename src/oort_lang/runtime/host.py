#! /usr/bin/env python

"""Host boundary for native functions and the Python implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol

from .objects import wrap_value

if TYPE_CHECKING:
    from .objects import OortObject


class HostBridge(Protocol):
    """Conversions between Oort values and one host representation.

    The Python implementation lives here. A future Rust host implements the
    same operations over its own value types; the language-facing Runtime must
    only depend on this protocol, not on Python's `py_value`.
    """

    def to_host(self, value: OortObject) -> Any: ...

    def from_host(self, value: Any) -> OortObject: ...


class PythonHost:
    """Host projection used by the tree-walking Python interpreter."""

    def to_host(self, value: OortObject) -> Any:
        return value.host_value

    def from_host(self, value: Any) -> OortObject:
        return wrap_value(value)
