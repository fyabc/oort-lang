#! /usr/bin/env python

from collections.abc import Iterable
from typing import Optional

from antlr4 import ParserRuleContext, Token

from ...support.source_position import SourcePosition
from ..ast_visitor import ASTVisitor, T


class ASTNode:
    def __init__(self, context: SourcePosition | ParserRuleContext | Token):
        if isinstance(context, ParserRuleContext):
            position = SourcePosition.from_context(context)
        elif isinstance(context, Token):
            position = SourcePosition.from_token(context)
        else:
            position = context
        assert isinstance(position, SourcePosition)
        self.position = position

        self.metadata = {
            # How many scopes between current scope and the scope of definition of the name.
            # - Only used in name nodes
            # - `Optional[int]`
            # - `None` means the name is defined in global.
            # "name_depth": None
            # Slot index of the name.
            # - Only used in name nodes
            # - int
            # "name_index": 1
            # Captured implicit class depth of `super`.
            # - Only used in implicit super nodes
            # - int
            # "super_depth": 1
        }

    @property
    def node_type(self):
        return type(self).__name__

    def children(self) -> Iterable["ASTNode"]:
        for _, child in self.named_children():
            if child is not None:
                yield child

    def named_children(self) -> Iterable[tuple[str, Optional["ASTNode"]]]:
        return []

    def __iter__(self):
        return iter(self.children())

    def _accept(self, visitor: ASTVisitor[T]) -> T:
        raise NotImplementedError()

    def accept(self, visitor: ASTVisitor[T]) -> T:
        visitor.pre_process(self)
        result = self._accept(visitor)
        return visitor.post_process(self, result)

    def str_attrs(self) -> str | None:
        return None
