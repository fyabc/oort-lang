#! /usr/bin/env python

"""Lexical scope layout shared by name resolution."""

import dataclasses
from collections import UserDict

from ..ast.binding import Binding


@dataclasses.dataclass
class ScopeEntry:
    """A name declared in one lexical scope."""

    index: int  # Slot index.
    is_ready: bool  # Whether the name is ready (distinguish declaration from definition).


class ScopeLayout(UserDict[str, ScopeEntry]):
    """Ordered slot layout for one lexical scope."""

    def __delitem__(self, key):
        raise TypeError("Cannot delete name from scope")

    def put(self, name: str) -> ScopeEntry:
        index = len(self.data)
        entry = ScopeEntry(index, False)
        self.data[name] = entry
        return entry

    def set_ready(self, name: str):
        self.data[name].is_ready = True

    def resolve(self, name: str, depth: int) -> Binding | None:
        """Resolve in this scope, or return None if it is not declared here."""
        entry = self.data.get(name)
        if entry is None:
            return None
        return Binding.local(name=name, depth=depth, index=entry.index)
