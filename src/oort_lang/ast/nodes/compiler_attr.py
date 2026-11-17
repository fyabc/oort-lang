#! /usr/bin/env python

from antlr4 import ParserRuleContext

from ..ast_visitor import ASTVisitor
from .base import ASTNode


class CompilerAttribute(ASTNode):
    def __init__(
        self,
        context: ParserRuleContext,
    ):
        super().__init__(context)

    def _accept(self, visitor: ASTVisitor):
        return visitor.visit_compiler_attribute(self)
