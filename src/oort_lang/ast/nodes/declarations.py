#! /usr/bin/env python

from collections.abc import Iterable
from enum import Enum

from antlr4 import ParserRuleContext

from ..ast_visitor import ASTVisitor
from .base import ASTNode


class Declaration(ASTNode):
    def __init__(self, context: ParserRuleContext, name: str, type_expr: ASTNode):
        super().__init__(context)
        self.name = name
        self.type_expr = type_expr

    def _accept(self, visitor: ASTVisitor):
        raise RuntimeError("Should not be called")


class SingleDeclTarget(Declaration):
    def named_children(self) -> Iterable[tuple[str, ASTNode | None]]:
        yield "type_expr", self.type_expr

    def _accept(self, visitor: ASTVisitor):
        return visitor.visit_single_decl_target(self)


class VarDecl(ASTNode):
    def __init__(
        self,
        context: ParserRuleContext,
        decl_targets: Iterable[SingleDeclTarget],
        init_value: ASTNode | None,
        mutable: bool,
    ):
        super().__init__(context)
        self.decl_targets = [decl_target for decl_target in decl_targets]
        self.init_value = init_value
        self.mutable = mutable

    def named_children(self) -> Iterable[tuple[str, ASTNode | None]]:
        for index, decl_target in enumerate(self.decl_targets):
            yield f"target {index}", decl_target
        yield "init_value", self.init_value

    def _accept(self, visitor: ASTVisitor):
        return visitor.visit_var_decl(self)

    def str_attrs(self) -> str | None:
        if self.mutable:
            return "var"
        else:
            return "val"


class ParameterKind(Enum):
    INVALID = 0
    DEFAULT = 1  # param1
    KW_ONLY = 2  # *, kw_only
    VAR_POS = 3  # *params
    VAR_KW = 4  # **kw_params
    POS_ONLY = 5  # param_pos_only, /
    BLOCK = 6  # $trailing_block


class Parameter(Declaration):
    def __init__(
        self,
        context: ParserRuleContext,
        name: str,
        type_expr: ASTNode,
        kind: ParameterKind = ParameterKind.DEFAULT,
        default_value: ASTNode | None = None,
    ):
        super().__init__(context, name, type_expr)
        self.kind = kind
        self.default_value = default_value

    def named_children(self) -> Iterable[tuple[str, ASTNode | None]]:
        yield "type_expr", self.type_expr
        yield "default", self.default_value

    def _accept(self, visitor: ASTVisitor):
        return visitor.visit_parameter(self)

    def str_attrs(self) -> str | None:
        if self.kind == ParameterKind.DEFAULT:
            return self.name
        return f"{self.name}, {self.kind.name}"


class TypeQualifierKind(Enum):
    INVALID = 0
    DEFAULT = 1
    UPPER_BOUND = 2
    LOWER_BOUND = 3
    META_TYPE = 4


class TypeParameter(Declaration):
    def __init__(
        self,
        context: ParserRuleContext,
        name: str,
        type_expr: ASTNode,
        qualifier: TypeQualifierKind = TypeQualifierKind.DEFAULT,
        default_value: ASTNode | None = None,
    ):
        super().__init__(context, name, type_expr)
        self.qualifier = qualifier
        self.default_value = default_value

    def _accept(self, visitor: ASTVisitor):
        return visitor.visit_type_parameter(self)

    def str_attrs(self) -> str | None:
        return f"{self.name}, {self.qualifier.name}"
