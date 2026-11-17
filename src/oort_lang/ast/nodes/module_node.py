#! /usr/bin/env python

from collections.abc import Iterable

from antlr4 import ParserRuleContext

from ..ast_visitor import ASTVisitor
from .base import ASTNode
from .expressions import BlockExpr


class ModuleNode(ASTNode):
    def __init__(self, context: ParserRuleContext, body: BlockExpr):
        super().__init__(context)
        self.body = body

    @property
    def node_type(self):
        return "Module"

    def named_children(self) -> Iterable[tuple[str, ASTNode | None]]:
        yield "body", self.body

    def _accept(self, visitor: ASTVisitor):
        return visitor.visit_module(self)
