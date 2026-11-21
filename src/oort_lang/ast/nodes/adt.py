#! /usr/bin/env python

from collections.abc import Iterable

from antlr4 import ParserRuleContext

from ...source.source_position import SourcePosition
from ..ast_visitor import ASTVisitor
from .base import ASTNode
from .declarations import TypeParameter
from .expressions import StmtExpr


class EnumDef(StmtExpr):
    """A monomorphic tagged-union declaration."""

    def __init__(
        self,
        context: ParserRuleContext,
        name: str,
        type_params: Iterable[TypeParameter],
        constructors: Iterable["EnumConstructor"],
        name_position: SourcePosition,
    ):
        super().__init__(context)
        self.name = name
        self.type_params = list(type_params)
        self.constructors = list(constructors)
        self.name_position = name_position

    def named_children(self) -> Iterable[tuple[str, ASTNode | None]]:
        for index, type_param in enumerate(self.type_params):
            yield f"type_param {index}", type_param
        for index, constructor in enumerate(self.constructors):
            yield f"constructor {index}", constructor

    def _accept(self, visitor: ASTVisitor):
        return visitor.visit_enum_def(self)

    def str_attrs(self) -> str | None:
        return f"name={self.name!r}"


class EnumConstructor(ASTNode):
    """One enum variant, optionally with named payload fields."""

    def __init__(
        self,
        context: ParserRuleContext,
        name: str,
        fields: Iterable["EnumField"],
    ):
        super().__init__(context)
        self.name = name
        self.fields = list(fields)

    def named_children(self) -> Iterable[tuple[str, ASTNode | None]]:
        for index, field in enumerate(self.fields):
            yield f"field {index}", field

    def _accept(self, visitor: ASTVisitor):
        return visitor.visit_enum_constructor(self)

    def str_attrs(self) -> str | None:
        return f"name={self.name!r}"


class EnumField(ASTNode):
    def __init__(self, context: ParserRuleContext, name: str, type_expr: ASTNode | None):
        super().__init__(context)
        self.name = name
        self.type_expr = type_expr

    def named_children(self) -> Iterable[tuple[str, ASTNode | None]]:
        yield "type_expr", self.type_expr

    def _accept(self, visitor: ASTVisitor):
        return visitor.visit_enum_field(self)

    def str_attrs(self) -> str | None:
        return f"name={self.name!r}"


class MatchExpr(StmtExpr):
    def __init__(
        self,
        context: ParserRuleContext,
        scrutinee: ASTNode,
        arms: Iterable["MatchArm"],
    ):
        super().__init__(context)
        self.scrutinee = scrutinee
        self.arms = list(arms)

    def named_children(self) -> Iterable[tuple[str, ASTNode | None]]:
        yield "scrutinee", self.scrutinee
        for index, arm in enumerate(self.arms):
            yield f"arm {index}", arm

    def _accept(self, visitor: ASTVisitor):
        return visitor.visit_match_expr(self)


class MatchArm(ASTNode):
    def __init__(self, context: ParserRuleContext, pattern: "Pattern", body: ASTNode):
        super().__init__(context)
        self.pattern = pattern
        self.body = body

    def named_children(self) -> Iterable[tuple[str, ASTNode | None]]:
        yield "pattern", self.pattern
        yield "body", self.body

    def _accept(self, visitor: ASTVisitor):
        return visitor.visit_match_arm(self)


class Pattern(ASTNode):
    def _accept(self, visitor: ASTVisitor):
        raise RuntimeError("Should not be called")


class WildcardPattern(Pattern):
    def _accept(self, visitor: ASTVisitor):
        return visitor.visit_wildcard_pattern(self)


class NamePattern(Pattern):
    """A binding name, or a nullary constructor when resolved by the checker."""

    def __init__(self, context: ParserRuleContext, name: str):
        super().__init__(context)
        self.name = name

    def _accept(self, visitor: ASTVisitor):
        return visitor.visit_name_pattern(self)

    def str_attrs(self) -> str | None:
        return f"name={self.name!r}"


class ConstructorPattern(Pattern):
    def __init__(self, context: ParserRuleContext, name: str, args: Iterable[Pattern]):
        super().__init__(context)
        self.name = name
        self.args = list(args)

    def named_children(self) -> Iterable[tuple[str, ASTNode | None]]:
        for index, arg in enumerate(self.args):
            yield f"arg {index}", arg

    def _accept(self, visitor: ASTVisitor):
        return visitor.visit_constructor_pattern(self)

    def str_attrs(self) -> str | None:
        return f"name={self.name!r}"
