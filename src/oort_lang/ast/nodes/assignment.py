#! /usr/bin/env python

from collections.abc import Iterable

from antlr4 import ParserRuleContext, Token

from ..ast_visitor import ASTVisitor
from .base import ASTNode


class Assignment(ASTNode):
    def __init__(self, context: ParserRuleContext, op: Token, lhs: ASTNode, rhs: ASTNode):
        super().__init__(context)
        self.op = op
        self.lhs = lhs
        self.rhs = rhs

    def named_children(self) -> Iterable[tuple[str, ASTNode | None]]:
        yield "lhs", self.lhs
        yield "rhs", self.rhs

    def _accept(self, visitor: ASTVisitor):
        return visitor.visit_assignment(self)
