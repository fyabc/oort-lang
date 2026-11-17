#! /usr/bin/env python

from collections.abc import Iterable

from antlr4 import ParserRuleContext, Token

from ...support.source_position import SourcePosition
from ..ast_visitor import ASTVisitor
from .argument import Argument
from .base import ASTNode
from .expressions import Expression


class Call(Expression):
    def __init__(
        self,
        context: SourcePosition | ParserRuleContext | Token,
        func: ASTNode,
        args: Iterable[Argument],
        infix: bool = False,
    ):
        super().__init__(context)
        self.func = func
        # todo: normalize all type of args (and trailing block) here?
        self.args = [arg for arg in args]
        self.infix = infix

    def named_children(self) -> Iterable[tuple[str, ASTNode | None]]:
        yield "func", self.func
        for index, arg in enumerate(self.args):
            yield f"arg {index}", arg

    def _accept(self, visitor: ASTVisitor):
        return visitor.visit_call(self)
