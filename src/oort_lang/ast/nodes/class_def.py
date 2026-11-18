#! /usr/bin/env python

from collections.abc import Iterable

from antlr4 import ParserRuleContext

from ...source.source_position import SourcePosition
from ..ast_visitor import ASTVisitor
from .base import ASTNode
from .declarations import TypeParameter
from .expressions import BlockExpr, Expression, StmtExpr


class ClassDef(StmtExpr):
    def __init__(
        self,
        context: ParserRuleContext,
        names: Iterable[str],
        type_params: Iterable[TypeParameter],
        bases: Iterable[Expression],
        meta: Expression | None,
        body: BlockExpr,
        name_position: SourcePosition,
    ):
        super().__init__(context)
        self.names = [name for name in names]
        self.type_params = [type_param for type_param in type_params]
        self.bases = [base for base in bases]
        self.meta = meta
        self.body = body
        self.name_position = name_position

    def named_children(self) -> Iterable[tuple[str, ASTNode | None]]:
        for index, type_param in enumerate(self.type_params):
            yield f"type_param {index}", type_param
        for index, base in enumerate(self.bases):
            yield f"base {index}", base
        if self.meta:
            yield "meta", self.meta
        yield "body", self.body

    def _accept(self, visitor: ASTVisitor):
        return visitor.visit_class_def(self)

    def str_attrs(self) -> str | None:
        return f"name={self.full_name!r}"

    @property
    def name(self) -> str:
        if not self.names:
            return "<lambda>"
        return self.names[-1]

    @property
    def full_name(self) -> str:
        if not self.names:
            return "<lambda>"
        return ".".join(self.names)

    @property
    def is_lambda(self) -> bool:
        return not self.names


class ImplicitSuperExpr(Expression):
    def _accept(self, visitor: ASTVisitor):
        return visitor.visit_implicit_super_expr(self)
