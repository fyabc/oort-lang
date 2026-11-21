#! /usr/bin/env python

"""Lexical scope entry management and name binding."""

from ..ast import nodes
from ..ast.binding import Binding
from ..diagnostics.error_handler import CompilerErrorHandler
from ..diagnostics.runtime_errors import OortNameError
from ..parser.names import anonymous_param_index
from ..source.input_info import InputInfo
from ..source.source_position import SourcePosition
from .scope import ScopeLayout


class ScopeResolverMixin:
    scopes: list[ScopeLayout]
    error_handler: CompilerErrorHandler
    input_info: InputInfo
    _current_func: nodes.FunctionDef | None

    def begin_scope(self, function: nodes.FunctionDef | None = None):
        self.scopes.append(ScopeLayout(function))

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
        anonymous = anonymous_param_index(name) is not None
        for depth, scope in enumerate(reversed(self.scopes)):
            # Any named function, and any lambda with an explicit parameter
            # list, is a barrier for `$n`: its body must not silently capture
            # an anonymous parameter from an enclosing lambda.
            if (
                anonymous
                and scope.function is not None
                and (not scope.function.is_lambda or scope.function.has_explicit_param_list)
            ):
                break
            binding = scope.resolve(name, depth)
            if binding is not None:
                node.binding = binding
                return binding
        binding = Binding.global_binding(name)
        node.binding = binding
        return binding
