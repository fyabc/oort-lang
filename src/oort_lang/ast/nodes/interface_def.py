#! /usr/bin/env python

from collections.abc import Iterable

from ...source.source_position import SourcePosition
from ..ast_visitor import ASTVisitor
from .base import ASTNode, NodeContext
from .declarations import Parameter, TypeParameter
from .expressions import Expression, StmtExpr


class InterfaceDef(StmtExpr):
    """A static interface: method signatures only, no state or constructors."""

    def __init__(
        self,
        context: NodeContext,
        name: str,
        type_params: Iterable[TypeParameter],
        bases: Iterable[Expression],
        methods: Iterable["InterfaceMethod"],
        name_position: SourcePosition,
    ):
        super().__init__(context)
        self.name = name
        self.type_params = list(type_params)
        self.bases = list(bases)
        self.methods = list(methods)
        self.name_position = name_position

    def named_children(self) -> Iterable[tuple[str, ASTNode | None]]:
        for index, type_param in enumerate(self.type_params):
            yield f"type_param {index}", type_param
        for index, base in enumerate(self.bases):
            yield f"base {index}", base
        for index, method in enumerate(self.methods):
            yield f"method {index}", method

    def _accept(self, visitor: ASTVisitor):
        return visitor.visit_interface_def(self)

    def str_attrs(self) -> str | None:
        return f"name={self.name!r}"


class InterfaceMethod(ASTNode):
    """One method requirement in an interface declaration."""

    def __init__(
        self,
        context: NodeContext,
        name: str,
        type_params: Iterable[TypeParameter],
        params: Iterable[Parameter],
        ret_type: ASTNode | None,
        name_position: SourcePosition,
    ):
        super().__init__(context)
        self.name = name
        self.type_params = list(type_params)
        self.params = list(params)
        self.ret_type = ret_type
        self.name_position = name_position

    def named_children(self) -> Iterable[tuple[str, ASTNode | None]]:
        for index, type_param in enumerate(self.type_params):
            yield f"type_param {index}", type_param
        for index, param in enumerate(self.params):
            yield f"param {index}", param
        yield "ret_type", self.ret_type

    def _accept(self, visitor: ASTVisitor):
        return visitor.visit_interface_method(self)

    def str_attrs(self) -> str | None:
        return f"name={self.name!r}"
