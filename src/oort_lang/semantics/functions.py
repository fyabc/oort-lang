#! /usr/bin/env python

"""Function and method declaration checks."""

from collections.abc import Callable

from ..ast import nodes
from ..ast.ast_visitor import ASTVisitor
from ..ast.nodes.declarations import ParameterKind
from ..diagnostics import OortSyntaxError
from ..diagnostics.error_handler import CompilerErrorHandler
from ..parser.operator_defs import validate_operator_definition
from ..source.input_info import InputInfo
from ..source.source_position import SourcePosition
from .decl import OutsideDeclType
from .scope import ScopeLayout


class FunctionResolverMixin(ASTVisitor):
    error_handler: CompilerErrorHandler
    input_info: InputInfo
    scopes: list[ScopeLayout]
    _current_func: nodes.FunctionDef | None
    _current_decl: OutsideDeclType
    _current_class: nodes.ClassDef | None
    _current_loop: nodes.ASTNode | None
    _unsupported: Callable[[str, nodes.ASTNode], None]

    # Implemented by ScopeResolverMixin, which comes first in the analyzer MRO.
    def begin_scope(self):
        raise NotImplementedError

    def end_scope(self):
        raise NotImplementedError

    def declare(self, name: str, position: SourcePosition):
        raise NotImplementedError

    def _declare_anonymous(self, name: str):
        raise NotImplementedError

    def define(self, name: str):
        raise NotImplementedError

    def visit_function_def(self, node: nodes.FunctionDef) -> None:
        if node.type_params:
            self._unsupported("Generic functions are not implemented yet.", node)
        if node.is_class_method and self._current_decl != OutsideDeclType.CLASS:
            self._unsupported("Class methods must be defined inside a class.", node)
            return None
        if (
            len(node.names) > 1
            and not node.is_class_method
            and self._current_decl != OutsideDeclType.CLASS
        ):
            self._unsupported("Extension methods are not implemented yet.", node)
            return None
        if node.is_operator:
            self._check_operator_definition(node)

        if not node.is_lambda:
            # TODO: Allow function redefinition in local scopes to support overloading.
            self.declare(self._declaration_name(node), node.name_position)
            self.define(self._declaration_name(node))  # Define eagerly for recursion.
        self.resolve_function(node)

    @staticmethod
    def _declaration_name(node: nodes.FunctionDef) -> str:
        """Name used for duplicate checks; operator arities may coexist."""
        if node.is_operator:
            return f"{node.name}#{node.operator_operand_count}"
        return node.name

    def _check_operator_definition(self, node: nodes.FunctionDef):
        if self._current_decl != OutsideDeclType.CLASS:
            self._unsupported("Operator methods must be defined inside a class.", node)
            return
        if node.is_class_method:
            self._unsupported("Class operator methods are not supported yet.", node)
            return

        assert node.operator_symbol is not None
        assert node.operator_operand_count is not None
        message = validate_operator_definition(node.operator_symbol, node.operator_operand_count)
        if message is not None:
            self.error_handler.add(
                OortSyntaxError(message, node.name_position),
                self.input_info,
            )

        for param in node.params:
            if param.default_value is not None or param.kind not in (
                ParameterKind.DEFAULT,
                ParameterKind.POS_ONLY,
            ):
                self._unsupported(
                    "Operator methods cannot use default, variadic, keyword-only "
                    "or block parameters.",
                    param,
                )

    def _check_default_later_refs(
        self, node: nodes.ASTNode, later_names: set[str], param_name: str
    ):
        """Reject default expressions that reference parameters declared later."""
        if isinstance(node, (nodes.FunctionDef, nodes.ClassDef)):
            return
        if isinstance(node, nodes.Name) and node.id in later_names:
            self.error_handler.add(
                OortSyntaxError(
                    f"Default value of {param_name!r} cannot reference later "
                    f"parameter {node.id!r}.",
                    node.position,
                ),
                self.input_info,
            )
        for _, child in node.named_children():
            if child is not None:
                self._check_default_later_refs(child, later_names, param_name)

    def resolve_function(self, node: nodes.FunctionDef):
        prev_func = self._current_func
        self._current_func = node
        prev_decl = self._current_decl
        # A function boundary also ends any enclosing loop for break/continue.
        prev_loop = self._current_loop
        self._current_loop = None
        if self._current_decl == OutsideDeclType.CLASS:
            # Check method names.
            if len(node.names) > 1:
                if node.is_class_method:
                    self._current_decl = OutsideDeclType.CLASS_METHOD
                else:
                    self.error_handler.add(
                        OortSyntaxError(
                            "Cannot define extension method in class scope.", node.name_position
                        ),
                        self.input_info,
                    )
                    self._current_decl = OutsideDeclType.METHOD
            elif node.is_lambda:
                # lambda inside class will be treated as normal function.
                pass
            elif node.name == "__init__":
                self._current_decl = OutsideDeclType.METHOD_INIT
            else:
                self._current_decl = OutsideDeclType.METHOD
        else:
            self._current_decl = OutsideDeclType.FUNCTION

        self.begin_scope()
        # Anonymous parameters are synthesized by the AST builder and are not
        # user declarations, so they bypass the explicit-name check.
        for index in range(node.anonymous_count):
            name = f"${index}"
            self._declare_anonymous(name)
            self.define(name)
        for index, param in enumerate(node.params):
            # Default values of later parameters can use previous parameters. e.g. `def f(a, b=a) {}`
            self.declare(param.name, node.position)
            if param.default_value:
                later_names = {item.name for item in node.params[index + 1 :]}
                if later_names:
                    self._check_default_later_refs(param.default_value, later_names, param.name)
                param.default_value.accept(self)
            self.define(param.name)

        # special variables in methods.
        if self._current_decl.is_method:
            self.declare("this", node.position)
            self.define("this")

        # visit body will create another new scope, so we visit its statements directly.
        for stmt in node.body.statements:
            stmt.accept(self)
        self.end_scope()

        self._current_func = prev_func
        self._current_decl = prev_decl
        self._current_loop = prev_loop
