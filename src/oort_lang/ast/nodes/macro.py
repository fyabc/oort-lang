#! /usr/bin/env python

from collections.abc import Iterable

from antlr4 import ParserRuleContext

from ..ast_visitor import ASTVisitor
from .argument import Argument
from .base import ASTNode
from .declarations import Parameter
from .expressions import BlockExpr, Expression, StmtExpr


class MacroDef(StmtExpr):
    def __init__(
        self,
        context: ParserRuleContext,
        name: str,
        params: Iterable[Parameter],
        body: BlockExpr,
    ):
        super().__init__(context)
        self.name = name
        self.params = [param for param in params]
        self.body = body

    def named_children(self) -> Iterable[tuple[str, ASTNode | None]]:
        for index, param in enumerate(self.params):
            yield f"param {index}", param
        yield "body", self.body

    def _accept(self, visitor: ASTVisitor):
        return visitor.visit_macro_def(self)

    def str_attrs(self) -> str | None:
        return f"name={self.name!r}"


class MacroCall(Expression):
    def __init__(
        self,
        context: ParserRuleContext,
        name: str,
        args: Iterable[Argument],
    ):
        super().__init__(context)
        self.name = name
        self.args = [arg for arg in args]

    def named_children(self) -> Iterable[tuple[str, ASTNode | None]]:
        for index, arg in enumerate(self.args):
            yield f"arg {index}", arg

    def _accept(self, visitor: ASTVisitor):
        return visitor.visit_macro_call(self)

    def str_attrs(self) -> str | None:
        return f"name={self.name!r}"
