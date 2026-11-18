#! /usr/bin/env python

from collections.abc import Iterable
from enum import Enum

from antlr4 import ParserRuleContext, Token

from ...source.source_position import SourcePosition
from ..ast_visitor import ASTVisitor
from .base import ASTNode


class LValueContext(Enum):
    """Context of lvalues."""

    INVALID = 0
    LOAD = 1
    STORE = 2
    DELETE = 3


class LValue(ASTNode):
    def __init__(
        self,
        context: SourcePosition | ParserRuleContext | Token,
        ctx: LValueContext = LValueContext.LOAD,
    ):
        super().__init__(context)
        self.ctx = ctx


class Name(LValue):
    def __init__(
        self,
        context: SourcePosition | ParserRuleContext | Token,
        id_: str,
        ctx: LValueContext = LValueContext.LOAD,
    ):
        super().__init__(context, ctx)
        self.id = id_

    def _accept(self, visitor: ASTVisitor):
        return visitor.visit_name(self)

    def str_attrs(self) -> str | None:
        return f"{self.id!r}, ctx={self.ctx.name}"


class Attribute(LValue):
    def __init__(
        self,
        context: SourcePosition | ParserRuleContext | Token,
        value: ASTNode,
        attribute: str,
        ctx: LValueContext = LValueContext.LOAD,
    ):
        super().__init__(context, ctx)
        self.value = value
        self.attribute = attribute

    def named_children(self) -> Iterable[tuple[str, ASTNode | None]]:
        yield "value", self.value

    def _accept(self, visitor: ASTVisitor):
        return visitor.visit_attribute(self)

    def str_attrs(self) -> str | None:
        return f"{self.attribute!r}, ctx={self.ctx.name}"


class Subscript(LValue):
    def __init__(
        self,
        context: ParserRuleContext,
        value: ASTNode,
        index: ASTNode,
        ctx: LValueContext = LValueContext.LOAD,
    ):
        super().__init__(context, ctx)
        self.value = value
        self.index = index

    def named_children(self) -> Iterable[tuple[str, ASTNode | None]]:
        yield "value", self.value
        yield "index", self.index

    def _accept(self, visitor: ASTVisitor):
        return visitor.visit_subscript(self)
