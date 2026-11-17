#! /usr/bin/env python

from collections.abc import Iterable
from enum import Enum

from antlr4 import ParserRuleContext

from ..ast_visitor import ASTVisitor
from .base import ASTNode


class ArgumentKind(Enum):
    """Function call argument kinds."""

    INVALID = 0
    DEFAULT = 1  # arg1
    KEYWORD = 2  # name=arg2
    VAR_POS = 3  # *args
    VAR_KW = 4  # **kwargs
    BLOCK = 5  # f() do {}


class Argument(ASTNode):
    def __init__(
        self,
        context: ParserRuleContext,
        value: ASTNode,
        kind: ArgumentKind = ArgumentKind.DEFAULT,
        keyword: str | None = None,
    ):
        super().__init__(context)
        self.value = value
        self.kind = kind
        self.keyword = keyword

    def named_children(self) -> Iterable[tuple[str, ASTNode | None]]:
        yield "value", self.value

    def _accept(self, visitor: ASTVisitor):
        return visitor.visit_argument(self)
