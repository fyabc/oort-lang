#! /usr/bin/env python

"""Resolved-name bindings attached to AST nodes."""

import dataclasses


@dataclasses.dataclass(frozen=True, slots=True)
class Binding:
    """Where a name is resolved.

    `depth` is the number of lexical scopes between the use site and the
    defining scope; `None` means the global scope. `index` is the name's slot
    in that scope layout and is `None` for globals.

    The slot index is not used by the tree-walking interpreter yet. It is
    carried here so a later slot/upvalue backend can consume the same binding
    without re-resolving names.
    """

    name: str
    depth: int | None = None
    index: int | None = None

    def __post_init__(self):
        if self.depth is None:
            if self.index is not None:
                raise ValueError("A global binding cannot have a slot index")
        elif self.index is None:
            raise ValueError("A local binding requires a slot index")
        elif self.depth < 0 or self.index < 0:
            raise ValueError("Binding depth and index must be non-negative")

    @property
    def is_global(self) -> bool:
        return self.depth is None

    @classmethod
    def global_binding(cls, name: str) -> "Binding":
        return cls(name=name)

    @classmethod
    def local(cls, name: str, depth: int, index: int) -> "Binding":
        return cls(name=name, depth=depth, index=index)
