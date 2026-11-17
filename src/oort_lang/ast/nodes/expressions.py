#! /usr/bin/env python

from collections.abc import Iterable

from antlr4 import ParserRuleContext, Token

from ...support.source_position import SourcePosition
from ..ast_visitor import ASTVisitor
from .base import ASTNode


class Expression(ASTNode):
    def _accept(self, visitor: ASTVisitor):
        raise RuntimeError("Should not be called")


class StmtExpr(Expression):
    def _accept(self, visitor: ASTVisitor):
        raise RuntimeError("Should not be called")


class BlockExpr(Expression):
    def __init__(self, context: ParserRuleContext, statements: Iterable[ASTNode] = ()):
        super().__init__(context)
        self.statements = [stmt for stmt in statements]

    @property
    def node_type(self):
        return "Block"

    def named_children(self) -> Iterable[tuple[str, ASTNode | None]]:
        for index, stmt in enumerate(self.statements):
            yield str(index), stmt

    def _accept(self, visitor: ASTVisitor):
        return visitor.visit_block_expr(self)


class UnaryExpr(Expression):
    def __init__(
        self, context: SourcePosition | ParserRuleContext | Token, op: Token, operand: ASTNode
    ):
        super().__init__(context)
        self.op = op
        self.operand = operand

    def named_children(self) -> Iterable[tuple[str, ASTNode | None]]:
        yield "operand", self.operand

    def _accept(self, visitor: ASTVisitor):
        return visitor.visit_unary_expr(self)

    def str_attrs(self) -> str | None:
        return f"op={self.op.text!r}"


class BinaryExpr(Expression):
    def __init__(
        self,
        context: SourcePosition | ParserRuleContext | Token,
        op: Token,
        lhs: ASTNode,
        rhs: ASTNode,
    ):
        super().__init__(context)
        self.op = op
        self.lhs = lhs
        self.rhs = rhs

    def named_children(self) -> Iterable[tuple[str, ASTNode | None]]:
        yield "lhs", self.lhs
        yield "rhs", self.rhs

    def _accept(self, visitor: ASTVisitor):
        return visitor.visit_binary_expr(self)

    def str_attrs(self) -> str | None:
        return f"op={self.op.text!r}"


class BooleanExpr(BinaryExpr):
    def _accept(self, visitor: ASTVisitor):
        raise RuntimeError("Should not be called")


class AndExpr(BooleanExpr):
    def _accept(self, visitor: ASTVisitor):
        return visitor.visit_and_expr(self)


class OrExpr(BooleanExpr):
    def _accept(self, visitor: ASTVisitor):
        return visitor.visit_or_expr(self)
