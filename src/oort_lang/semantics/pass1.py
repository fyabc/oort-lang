#! /usr/bin/env python

from typing import TypeVar

from ..ast import nodes
from ..ast.ast_visitor import ASTVisitor
from ..diagnostics import OortSyntaxError
from ..diagnostics.error_handler import CompilerErrorHandler
from ..diagnostics.runtime_errors import OortNameError
from ..diagnostics.syntax_errors import UnsupportedSyntax
from ..parser.dialect import DEFAULT_DIALECT, DialectConfig
from ..parser.names import anonymous_param_index
from ..source.input_info import InputInfo
from ..source.source_position import SourcePosition
from .decl import OutsideDeclType
from .functions import FunctionResolverMixin
from .resolution import ScopeResolverMixin

T = TypeVar("T")


class Pass1Analyzer(ScopeResolverMixin, FunctionResolverMixin, ASTVisitor[T]):
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
        self.scopes = []

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
        self._check_import_location(node)

    def visit_import_from_stmt(self, node: nodes.ImportFromStmt) -> T | None:
        self._check_import_location(node)

    def _check_import_location(self, node: nodes.ASTNode):
        """Imports are static module declarations, not local statements."""
        if self.scopes:
            self.error_handler.add(
                OortSyntaxError("Imports are only allowed at module top level.", node.position),
                self.input_info,
            )

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

    def visit_enum_def(self, node: nodes.EnumDef) -> T | None:
        if not self.dialect.features.adt:
            self._unsupported("Enums are only supported in oort-core yet.", node)
            return None
        if self.scopes:
            self._unsupported(
                "Enum declarations are only allowed at module top level in oort-core.",
                node,
            )
        return None

    def visit_match_expr(self, node: nodes.MatchExpr) -> T | None:
        if not self.dialect.features.adt:
            self._unsupported("match is only supported in oort-core yet.", node)
            return None
        node.scrutinee.accept(self)
        for arm in node.arms:
            self.begin_scope()
            try:
                bindings = self._pattern_bindings(arm.pattern)
                for name, position in bindings:
                    self.declare(name, position)
                for name, _ in bindings:
                    self.define(name)
                if arm.guard is not None:
                    arm.guard.accept(self)
                arm.body.accept(self)
            finally:
                self.end_scope()
        return None

    def _pattern_bindings(self, pattern: nodes.Pattern) -> list[tuple[str, SourcePosition]]:
        """Unique binding names in one pattern, including or-alternatives.

        Alternatives in an or-pattern reuse the same arm scope; dedupe so
        Pass1 does not report duplicates before the checker can validate that
        every alternative binds the same names.
        """
        names: list[tuple[str, SourcePosition]] = []

        def walk(current: nodes.Pattern) -> None:
            if isinstance(current, nodes.NamePattern):
                names.append((current.name, current.position))
            elif isinstance(current, nodes.ConstructorPattern):
                for arg in current.args:
                    walk(arg)
            elif isinstance(current, nodes.TuplePattern):
                for item in current.patterns:
                    walk(item)
            elif isinstance(current, nodes.OrPattern):
                for alternative in current.patterns:
                    walk(alternative)

        walk(pattern)
        seen: set[str] = set()
        unique: list[tuple[str, SourcePosition]] = []
        for name, position in names:
            if name not in seen:
                seen.add(name)
                unique.append((name, position))
        return unique

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
