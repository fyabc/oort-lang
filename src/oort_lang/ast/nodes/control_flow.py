#! /usr/bin/env python

from collections.abc import Iterable

from antlr4 import ParserRuleContext, Token

from ...support.source_position import SourcePosition
from ..ast_visitor import ASTVisitor
from .base import ASTNode
from .declarations import SingleDeclTarget
from .expressions import BlockExpr, StmtExpr


class IfExpr(StmtExpr):
    def __init__(
        self,
        context: ParserRuleContext,
        condition: ASTNode,
        if_block: BlockExpr,
        else_block: BlockExpr | None,
    ):
        super().__init__(context)
        self.condition = condition
        self.if_block = if_block
        self.else_block = else_block

    def named_children(self) -> Iterable[tuple[str, ASTNode | None]]:
        yield "condition", self.condition
        yield "if_block", self.if_block
        yield "else_block", self.else_block

    def _accept(self, visitor: ASTVisitor):
        return visitor.visit_if_expr(self)


class ForExpr(StmtExpr):
    def __init__(
        self,
        context: ParserRuleContext,
        vars_: Iterable[SingleDeclTarget],
        iterator: ASTNode,
        body: BlockExpr,
    ):
        super().__init__(context)
        self.vars = [var for var in vars_]
        self.iterator = iterator
        self.body = body

    def named_children(self) -> Iterable[tuple[str, ASTNode | None]]:
        for index, var in enumerate(self.vars):
            yield f"var {index}", var
        yield "iterator", self.iterator
        yield "body", self.body

    def _accept(self, visitor: ASTVisitor):
        return visitor.visit_for_expr(self)


class WhileExpr(StmtExpr):
    def __init__(
        self,
        context: ParserRuleContext,
        condition: ASTNode,
        body: BlockExpr,
    ):
        super().__init__(context)
        self.condition = condition
        self.body = body

    def named_children(self) -> Iterable[tuple[str, ASTNode | None]]:
        yield "condition", self.condition
        yield "body", self.body

    def _accept(self, visitor: ASTVisitor):
        return visitor.visit_while_expr(self)


class ReturnExpr(StmtExpr):
    def __init__(self, context: ParserRuleContext, value: ASTNode | None):
        super().__init__(context)
        self.value = value

    def named_children(self) -> Iterable[tuple[str, ASTNode | None]]:
        yield "value", self.value

    def _accept(self, visitor: ASTVisitor):
        return visitor.visit_return_expr(self)


class ContinueExpr(StmtExpr):
    def __init__(self, context: ParserRuleContext):
        super().__init__(context)

    def _accept(self, visitor: ASTVisitor):
        return visitor.visit_continue_expr(self)


class BreakExpr(StmtExpr):
    def __init__(self, context: ParserRuleContext, value: ASTNode | None = None):
        super().__init__(context)
        self.value = value

    def named_children(self) -> Iterable[tuple[str, ASTNode | None]]:
        yield "value", self.value

    def _accept(self, visitor: ASTVisitor):
        return visitor.visit_break_expr(self)


class YieldExpr(StmtExpr):
    def __init__(self, context: ParserRuleContext, value: ASTNode):
        super().__init__(context)
        self.value = value

    def named_children(self) -> Iterable[tuple[str, ASTNode | None]]:
        yield "value", self.value

    def _accept(self, visitor: ASTVisitor):
        return visitor.visit_yield_expr(self)


class AwaitExpr(StmtExpr):
    def __init__(self, context: SourcePosition | ParserRuleContext | Token, value: ASTNode):
        super().__init__(context)
        self.value = value

    def named_children(self) -> Iterable[tuple[str, ASTNode | None]]:
        yield "value", self.value

    def _accept(self, visitor: ASTVisitor):
        return visitor.visit_await_expr(self)
