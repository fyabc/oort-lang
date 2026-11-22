#! /usr/bin/env python

from collections.abc import Iterable
from typing import TYPE_CHECKING, Any, Optional, TypeAlias

from antlr4 import ParserRuleContext, Token

from ...source.source_position import SourcePosition
from ..ast_visitor import ASTVisitor, T

if TYPE_CHECKING:
    from ..binding import Binding

NodeContext: TypeAlias = SourcePosition | ParserRuleContext | Token


class ASTNode:
    def __init__(self, context: NodeContext):
        if isinstance(context, ParserRuleContext):
            position = SourcePosition.from_context(context)
        elif isinstance(context, Token):
            position = SourcePosition.from_token(context)
        else:
            position = context
        assert isinstance(position, SourcePosition)
        self.position = position

        # Filled in by pass 1 for name-like nodes (`Name`, `ImplicitSuperExpr`).
        self.binding: Binding | None = None

        self.metadata: dict[str, Any] = {}

        # True for compiler-injected nodes (for example the core prelude);
        # AST dumps skip them and they are not module exports.
        self.synthetic = False

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
