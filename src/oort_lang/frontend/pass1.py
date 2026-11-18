#! /usr/bin/env python

from enum import Enum
from typing import TypeVar

from ..ast import nodes
from ..ast.ast_visitor import ASTVisitor
from ..ast.binding import Binding
from ..ast.nodes.declarations import ParameterKind
from ..exceptions import OortSyntaxError
from ..exceptions.runtime_errors import OortNameError
from ..exceptions.syntax_errors import UnsupportedSyntax
from ..frontend.dialect import DEFAULT_DIALECT, DialectConfig
from ..frontend.error_handler import CompilerErrorHandler
from ..frontend.names import anonymous_param_index
from ..frontend.operator_defs import validate_operator_definition
from ..frontend.scope import ScopeLayout
from ..support.input_info import InputInfo
from ..support.source_position import SourcePosition

T = TypeVar("T")


class OutsideDeclType(Enum):
    """Current outside declaration type."""

    NONE = 0  # global
    FUNCTION = 1  # free function
    CLASS = 2  # class
    METHOD = 3  # method
    METHOD_INIT = 4  # initializer
    CLASS_METHOD = 5  # static method

    @property
    def is_function(self) -> bool:
        return self in [
            OutsideDeclType.FUNCTION,
            OutsideDeclType.METHOD,
            OutsideDeclType.METHOD_INIT,
            OutsideDeclType.CLASS_METHOD,
        ]

    @property
    def is_method(self) -> bool:
        return self in [
            OutsideDeclType.METHOD,
            OutsideDeclType.METHOD_INIT,
            OutsideDeclType.CLASS_METHOD,
        ]


class Pass1Analyzer(ASTVisitor[T]):
    """Pass-1 semantic analyzer.

    Including:
        - name resolving
        - detect: return outside function, break/continue outside loop
        - detect: unsupported syntax features
        - detect: bad initializer syntax.
        - etc.
    """

    def __init__(
        self,
        error_handler: CompilerErrorHandler,
        input_info: InputInfo,
        dialect: DialectConfig = DEFAULT_DIALECT,
    ):
        self.error_handler = error_handler
        self.input_info = input_info
        self.dialect = dialect

        # All scopes (except <global>)
        self.scopes: list[ScopeLayout] = []

        self._current_decl = OutsideDeclType.NONE
        self._current_func: nodes.FunctionDef | None = None
        self._current_class: nodes.ClassDef | None = None
        self._current_loop: nodes.ASTNode | None = None

    def parse(self, node: nodes.ASTNode) -> T | None:
        return node.accept(self)

    def visit_module(self, node: nodes.ModuleNode) -> T | None:
        # Skip extra scope for `body`.
        return self.visit_children(node.body)

    def visit_block_expr(self, node: nodes.BlockExpr) -> T | None:
        self.begin_scope()
        for stmt in node.statements:
            stmt.accept(self)
        self.end_scope()

    def visit_var_decl(self, node: nodes.VarDecl) -> T | None:
        for decl_target in node.decl_targets:
            self.declare(decl_target.name, decl_target.position)

        if node.init_value is not None:
            node.init_value.accept(self)

        for decl_target in node.decl_targets:
            self.define(decl_target.name)

    def _unsupported(self, message: str, node: nodes.ASTNode):
        self.error_handler.add(UnsupportedSyntax(message, node.position), self.input_info)

    def visit_import_stmt(self, node: nodes.ImportStmt) -> T | None:
        self._unsupported("The module system is not implemented yet.", node)

    def visit_import_from_stmt(self, node: nodes.ImportFromStmt) -> T | None:
        self._unsupported("The module system is not implemented yet.", node)

    def visit_compiler_attribute(self, node: nodes.CompilerAttribute) -> T | None:
        self._unsupported("Compiler attributes are not implemented yet.", node)

    def visit_macro_def(self, node: nodes.MacroDef) -> T | None:
        self._unsupported("The macro system is not implemented yet.", node)

    def visit_macro_call(self, node: nodes.MacroCall) -> T | None:
        self._unsupported("The macro system is not implemented yet.", node)

    def visit_yield_expr(self, node: nodes.YieldExpr) -> T | None:
        self._unsupported("Generators (`yield`) are not implemented yet.", node)

    def visit_await_expr(self, node: nodes.AwaitExpr) -> T | None:
        self._unsupported("Async/await is not implemented yet.", node)

    def visit_call(self, node: nodes.Call) -> T | None:
        seen_keyword = False
        seen_keywords: set[str] = set()
        for arg in node.args:
            if arg.keyword is None:
                if arg.kind != nodes.ArgumentKind.BLOCK and seen_keyword:
                    self.error_handler.add(
                        OortSyntaxError(
                            "Positional argument follows keyword argument.", arg.position
                        ),
                        self.input_info,
                    )
            else:
                seen_keyword = True
                if arg.keyword in seen_keywords:
                    self.error_handler.add(
                        OortSyntaxError(
                            f"Keyword argument {arg.keyword!r} is given more than once.",
                            arg.position,
                        ),
                        self.input_info,
                    )
                seen_keywords.add(arg.keyword)
            arg.accept(self)
        node.func.accept(self)

    def visit_assignment(self, node: nodes.Assignment) -> T | None:
        node.rhs.accept(self)

        if node.op.text != "=" and isinstance(node.lhs, nodes.TupleLiteral):
            self.error_handler.add(
                OortSyntaxError("Augmented assignment cannot target a tuple.", node.lhs.position),
                self.input_info,
            )
            return None

        self._check_assign_target(node.lhs)

    def _check_assign_target(self, lhs: nodes.ASTNode):
        if isinstance(lhs, nodes.TupleLiteral):
            for element in lhs.elements:
                self._check_assign_target(element)
        elif isinstance(lhs, nodes.Name):
            self.resolve_local(lhs, lhs.id)
        elif isinstance(lhs, nodes.LValue):
            lhs.accept(self)
        else:
            self.error_handler.add(
                OortSyntaxError("Cannot assign to expression here.", lhs.position),
                self.input_info,
            )

    def visit_return_expr(self, node: nodes.ReturnExpr) -> T | None:
        if not self._current_decl.is_function:
            self.error_handler.add(
                OortSyntaxError("Return outside function.", node.position),
                self.input_info,
            )
        if self._current_decl == OutsideDeclType.METHOD_INIT and node.value is not None:
            self.error_handler.add(
                OortSyntaxError("Return inside method initializer.", node.position),
                self.input_info,
            )
        if node.value:
            node.value.accept(self)

    def visit_continue_expr(self, node: nodes.ContinueExpr) -> T | None:
        if self._current_loop is None:
            self.error_handler.add(
                OortSyntaxError("Continue outside loop.", node.position),
                self.input_info,
            )

    def visit_break_expr(self, node: nodes.BreakExpr) -> T | None:
        if self._current_loop is None:
            self.error_handler.add(
                OortSyntaxError("Break outside loop.", node.position),
                self.input_info,
            )
        if node.value is not None:
            node.value.accept(self)

    def visit_implicit_super_expr(self, node: nodes.ImplicitSuperExpr) -> T | None:
        binding = self.resolve_local(node, "this")
        if binding.is_global:
            self.error_handler.add(
                OortNameError("Can't use implicit 'super' outside method.", node.position),
                self.input_info,
            )

    def visit_class_def(self, node: nodes.ClassDef) -> T | None:
        if node.type_params:
            self._unsupported("Generic classes are not implemented yet.", node)
        if len(node.names) > 1:
            self._unsupported("Namespaced classes are not implemented yet.", node)
            return None
        for base in node.bases:
            base.accept(self)
        if node.meta is not None:
            node.meta.accept(self)

        prev_class = self._current_class
        self._current_class = node
        prev_decl = self._current_decl
        self._current_decl = OutsideDeclType.CLASS

        if not node.is_lambda:
            self.declare(node.name, node.name_position)
            self.define(node.name)

        self.begin_scope()
        try:
            for stmt in node.body.statements:
                self._check_class_body_statement(stmt)
                stmt.accept(self)
        finally:
            self.end_scope()
            self._current_class = prev_class
            self._current_decl = prev_decl

    def _check_class_body_statement(self, stmt: nodes.ASTNode):
        """Apply dialect-specific rules to statements directly in a class body."""
        if isinstance(stmt, nodes.VarDecl) and not self.dialect.features.class_body_vars:
            self.error_handler.add(
                OortSyntaxError(
                    f"Class-body variable declarations are not supported in "
                    f"the `{self.dialect.name}` dialect; assign instance fields "
                    f"in `__init__` instead (`this.name = ...`).",
                    stmt.position,
                ),
                self.input_info,
            )

    def visit_function_def(self, node: nodes.FunctionDef) -> T | None:
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

    def visit_for_expr(self, node: nodes.ForExpr) -> T | None:
        node.iterator.accept(self)

        prev_loop = self._current_loop
        self._current_loop = node
        self.begin_scope()
        try:
            for var in node.vars:
                self.declare(var.name, var.position)
            for var in node.vars:
                self.define(var.name)
            node.body.accept(self)
        finally:
            self.end_scope()
            self._current_loop = prev_loop

    def visit_while_expr(self, node: nodes.WhileExpr) -> T | None:
        node.condition.accept(self)
        prev_loop = self._current_loop
        self._current_loop = node
        node.body.accept(self)
        self._current_loop = prev_loop

    def visit_name(self, node: nodes.Name) -> T | None:
        if self.scopes:
            entry = self.scopes[-1].get(node.id, None)
            if entry and entry.is_ready is False:
                self.error_handler.add(
                    OortNameError(
                        f"Can't read local variable {node.id} in its own initializer.",
                        node.position,
                    ),
                    self.input_info,
                )
        binding = self.resolve_local(node, node.id)

        if anonymous_param_index(node.id) is not None and binding.is_global:
            if self._current_func is None:
                message = "Anonymous parameters are only allowed inside a lambda."
            elif not self._current_func.is_lambda:
                message = "Anonymous parameters are only allowed in lambdas."
            elif self._current_func.has_explicit_param_list:
                message = "Anonymous parameters cannot be combined with an explicit parameter list."
            else:
                message = "Anonymous parameter is not available in this scope."
            self.error_handler.add(OortNameError(message, node.position), self.input_info)

        if node.id == "this" and binding.is_global:
            self.error_handler.add(
                OortNameError("Can't access 'this' outside method.", node.position),
                self.input_info,
            )

    def begin_scope(self):
        self.scopes.append(ScopeLayout())

    def end_scope(self):
        self.scopes.pop()

    def declare(self, name: str, position: SourcePosition):
        if anonymous_param_index(name) is not None:
            self.error_handler.add(
                OortNameError("Anonymous parameter names cannot be declared explicitly.", position),
                self.input_info,
            )
        if not self.scopes:
            return
        scope = self.scopes[-1]
        if name in scope:
            self.error_handler.add(
                OortNameError(f"Variable {name} is already defined.", position),
                self.input_info,
            )
        scope.put(name)

    def _declare_anonymous(self, name: str):
        """Declare a synthesized `$0`, `$1`, ... parameter (bypasses the check)."""
        if not self.scopes:
            return
        self.scopes[-1].put(name)

    def define(self, name: str):
        if not self.scopes:
            return
        self.scopes[-1].set_ready(name)

    def resolve_local(self, node: nodes.ASTNode, name: str) -> Binding:
        """Resolve a name and attach its typed binding to the AST node."""
        for depth, scope in enumerate(reversed(self.scopes)):
            binding = scope.resolve(name, depth)
            if binding is not None:
                node.binding = binding
                return binding
        binding = Binding.global_binding(name)
        node.binding = binding
        return binding

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
