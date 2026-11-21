#! /usr/bin/env python

"""Independent static checker for the `oort-core` thin probe.

The checker is intentionally small: `Int`, `Bool`, `Unit` and functions.
It runs after pass 1 (name resolution / unsupported-feature checks) and only
when pass 1 succeeded, so it can assume bindings exist and focus on types.
"""

import dataclasses
from collections.abc import Callable, Iterable
from pathlib import Path, PurePosixPath

from ...ast import nodes
from ...ast.ast_visitor import ASTVisitor
from ...diagnostics import TypeCheckError, UnsupportedSyntax
from ...diagnostics.error_handler import CompilerErrorHandler
from ...parser.dialect import DialectConfig
from ...source.input_info import InputInfo
from ...source.source_position import SourcePosition
from .types import (
    BOOL,
    INT,
    NEVER,
    UNIT,
    UNKNOWN,
    CoreModuleInfo,
    FunctionType,
    ModuleType,
    NeverType,
    Type,
    UnknownType,
    describe_type,
    is_assignable,
    join_types,
)

ModuleResolver = Callable[[str, Path, SourcePosition], CoreModuleInfo | None]

_ARITHMETIC = frozenset({"+", "-", "*", "//", "%"})
_ORDERING = frozenset({"<", "<=", ">", ">="})
_EQUALITY = frozenset({"==", "!="})


@dataclasses.dataclass(slots=True)
class NameInfo:
    type: Type
    mutable: bool
    is_function: bool = False


class CoreTypeChecker(ASTVisitor[Type]):
    """Type-check the `oort-core` subset and record inferred types."""

    def __init__(
        self,
        error_handler: CompilerErrorHandler,
        input_info: InputInfo,
        dialect: DialectConfig,
        module_resolver: ModuleResolver | None = None,
    ):
        self.error_handler = error_handler
        self.input_info = input_info
        self.dialect = dialect
        self.module_resolver = module_resolver
        self.scopes: list[dict[str, NameInfo]] = [{}]
        self.current_function: FunctionType | None = None
        self.current_function_name: str | None = None
        self.module_level = True
        self.module_exports: tuple[tuple[str, Type], ...] = ()

    # ------------------------------------------------------------------
    # Entry point and scopes
    # ------------------------------------------------------------------

    def parse(self, node: nodes.ASTNode) -> Type | None:
        return node.accept(self)

    def visit_module(self, node: nodes.ModuleNode) -> Type:
        statements = list(node.body.statements)
        # Match runtime hoisting: bind imports before checking any body.
        imports = [
            stmt
            for stmt in statements
            if isinstance(stmt, (nodes.ImportStmt, nodes.ImportFromStmt))
        ]
        for stmt in imports:
            stmt.accept(self)
        self._check_statements(
            stmt
            for stmt in statements
            if not isinstance(stmt, (nodes.ImportStmt, nodes.ImportFromStmt))
        )
        self.module_exports = tuple((name, info.type) for name, info in self.scopes[0].items())
        return UNIT

    def visit_block_expr(self, node: nodes.BlockExpr) -> Type:
        previous_module_level = self.module_level
        self.module_level = False
        self.scopes.append({})
        try:
            return self._check_statements(node.statements)
        finally:
            self.scopes.pop()
            self.module_level = previous_module_level

    def _check_statements(self, statements: Iterable[nodes.ASTNode]) -> Type:
        result: Type = UNIT
        saw_never = False
        for stmt in statements:
            statement_type = stmt.accept(self)
            if statement_type is None:
                statement_type = UNKNOWN
            if isinstance(statement_type, NeverType):
                saw_never = True
            elif not saw_never:
                result = statement_type
        return NEVER if saw_never else result

    def lookup(self, name: str) -> NameInfo | None:
        for scope in reversed(self.scopes):
            info = scope.get(name)
            if info is not None:
                return info
        return None

    def declare(
        self,
        name: str,
        type_: Type,
        *,
        mutable: bool,
        position,
        is_function: bool = False,
    ) -> None:
        scope = self.scopes[-1]
        if name in scope:
            self._error(f"Duplicate declaration of '{name}' in oort-core.", position)
            return
        scope[name] = NameInfo(type_, mutable, is_function)

    # ------------------------------------------------------------------
    # Declarations and statements
    # ------------------------------------------------------------------

    def visit_var_decl(self, node: nodes.VarDecl) -> Type:
        if len(node.decl_targets) != 1:
            return self._unsupported(
                node, "Multi-target declarations are not supported in oort-core yet."
            )
        target = node.decl_targets[0]
        if node.init_value is None:
            return self._unsupported(
                node, "Variable declarations require an initializer in oort-core."
            )

        annotation = None
        if target.type_expr is not None:
            annotation = self.resolve_annotation(target.type_expr, allow_unit=False)

        init_type = node.init_value.accept(self)
        if init_type is None:
            init_type = UNKNOWN

        if annotation is not None:
            type_ = annotation
            if not isinstance(annotation, UnknownType):
                self.expect(annotation, init_type, node.init_value)
        elif isinstance(init_type, UnknownType):
            # The initializer already reported an error; do not add a cascade.
            type_ = UNKNOWN
        elif isinstance(init_type, (NeverType, FunctionType, ModuleType)) or init_type == UNIT:
            self._error(
                f"Cannot infer a usable type for '{target.name}' "
                f"(initializer has type {describe_type(init_type)}).",
                node.position,
            )
            type_ = UNKNOWN
        else:
            type_ = init_type

        self.declare(
            target.name,
            type_,
            mutable=node.mutable,
            position=target.position,
        )
        target.metadata["type"] = describe_type(type_)
        return UNIT

    def visit_assignment(self, node: nodes.Assignment) -> Type:
        if node.op.text != "=":
            return self._unsupported(
                node, "Augmented assignment is not supported in oort-core yet."
            )
        if not isinstance(node.lhs, nodes.Name):
            return self._unsupported(node, "Only plain name assignment is supported in oort-core.")

        value_type = node.rhs.accept(self)
        if value_type is None:
            value_type = UNKNOWN

        info = self.lookup(node.lhs.id)
        if info is None:
            self._error(f"Unknown name '{node.lhs.id}'.", node.lhs.position)
            return UNIT
        if not info.mutable:
            self._error(
                f"Cannot assign to immutable binding '{node.lhs.id}' (declared with `val`).",
                node.position,
            )
            return UNIT

        self.expect(info.type, value_type, node.rhs)
        node.lhs.metadata["type"] = describe_type(info.type)
        return UNIT

    def visit_function_def(self, node: nodes.FunctionDef) -> Type:
        if node.is_lambda:
            return self._unsupported(node, "Lambdas are not supported in oort-core yet.")
        if node.is_extension:
            return self._unsupported(node, "Extension methods are not supported in oort-core yet.")
        if node.is_class_method or len(node.names) != 1:
            return self._unsupported(
                node, "Only plain top-level functions are supported in oort-core."
            )
        if node.type_params:
            return self._unsupported(node, "Generic functions are not supported in oort-core yet.")
        if node.operator_symbol is not None:
            return self._unsupported(
                node, "Operator definitions are not supported in oort-core yet."
            )
        if not self.module_level:
            return self._unsupported(
                node, "Nested function definitions are not supported in oort-core yet."
            )

        param_types: list[Type] = []
        for param in node.params:
            if param.kind != nodes.ParameterKind.DEFAULT or param.default_value is not None:
                self._unsupported(
                    param,
                    "Defaults, keyword-only/positional-only markers, "
                    "*args, **kwargs and &block are not supported in oort-core yet.",
                )
                param_types.append(UNKNOWN)
                continue
            if param.type_expr is None:
                self._error(
                    f"Parameter '{param.name}' requires a type annotation in oort-core.",
                    param.position,
                )
                param_types.append(UNKNOWN)
                continue
            param_type = self.resolve_annotation(param.type_expr, allow_unit=False)
            param_types.append(param_type)

        return_type: Type
        if node.ret_type is None:
            self._error(
                f"Function '{node.name}' requires a return type annotation in oort-core.",
                node.name_position,
            )
            return_type = UNKNOWN
        else:
            return_type = self.resolve_annotation(node.ret_type, allow_unit=True)

        signature = FunctionType(tuple(param_types), return_type)
        self.declare(
            node.name,
            signature,
            mutable=False,
            position=node.name_position,
            is_function=True,
        )
        node.metadata["type"] = describe_type(signature)

        previous_function = self.current_function
        previous_name = self.current_function_name
        previous_module_level = self.module_level
        self.current_function = signature
        self.current_function_name = node.name
        self.module_level = False
        self.scopes.append({})
        try:
            for param, param_type in zip(node.params, param_types):
                self.declare(
                    param.name,
                    param_type,
                    mutable=False,
                    position=param.position,
                )
            body_type = self._check_statements(node.body.statements)
        finally:
            self.scopes.pop()
            self.current_function = previous_function
            self.current_function_name = previous_name
            self.module_level = previous_module_level

        if not isinstance(body_type, NeverType) and not is_assignable(return_type, body_type):
            self._error(
                f"Function '{node.name}' is declared to return "
                f"{describe_type(return_type)}, but its body has type "
                f"{describe_type(body_type)}.",
                node.position,
            )
        return UNIT

    def visit_return_expr(self, node: nodes.ReturnExpr) -> Type:
        if self.current_function is None:
            self._error("Return outside function.", node.position)
            return NEVER

        return_type = self.current_function.ret
        if node.value is None:
            if return_type != UNIT and not isinstance(return_type, UnknownType):
                self._error(
                    f"Function '{self.current_function_name}' is declared to return "
                    f"{describe_type(return_type)}; a bare return is only allowed "
                    f"for Unit functions.",
                    node.position,
                )
        else:
            value_type = node.value.accept(self)
            if value_type is None:
                value_type = UNKNOWN
            self.expect(return_type, value_type, node.value)
        return NEVER

    # ------------------------------------------------------------------
    # Expressions
    # ------------------------------------------------------------------

    def visit_int_constant(self, node: nodes.IntConstant) -> Type:
        return self._record(node, INT)

    def visit_boolean_constant(self, node: nodes.BooleanConstant) -> Type:
        return self._record(node, BOOL)

    def visit_name(self, node: nodes.Name) -> Type:
        info = self.lookup(node.id)
        if info is None:
            if node.id == "print":
                self._error(
                    "The built-in 'print' can only be called directly in oort-core.",
                    node.position,
                )
            else:
                self._error(f"Unknown name '{node.id}'.", node.position)
            return self._record(node, UNKNOWN)
        return self._record(node, info.type)

    def visit_call(self, node: nodes.Call) -> Type:
        if node.infix:
            return self._unsupported(node, "Infix calls are not supported in oort-core yet.")
        if not isinstance(node.func, (nodes.Name, nodes.Attribute)):
            return self._unsupported(
                node, "Only calls to named functions are supported in oort-core."
            )

        argument_types: list[Type] = []
        for arg in node.args:
            if arg.keyword is not None or arg.kind != nodes.ArgumentKind.DEFAULT:
                self._unsupported(
                    arg,
                    "Keyword, variadic and block arguments are not supported in oort-core yet.",
                )
                argument_types.append(UNKNOWN)
                continue
            arg_type = arg.value.accept(self)
            argument_types.append(UNKNOWN if arg_type is None else arg_type)

        if isinstance(node.func, nodes.Name):
            name = node.func.id
            info = self.lookup(name)
            if info is None:
                if name == "print":
                    return self._check_print_call(node, argument_types)
                self._error(f"Unknown function '{name}'.", node.func.position)
                return self._record(node, UNKNOWN)
            if not isinstance(info.type, FunctionType):
                self._error(f"'{name}' is not callable.", node.func.position)
                return self._record(node, UNKNOWN)
            signature = info.type
            display_name = name
        else:
            callee_type = node.func.accept(self)
            if isinstance(callee_type, UnknownType):
                return self._record(node, UNKNOWN)
            if not isinstance(callee_type, FunctionType):
                self._error(
                    f"'{node.func.attribute}' is not callable.",
                    node.func.position,
                )
                return self._record(node, UNKNOWN)
            signature = callee_type
            display_name = node.func.attribute

        if len(argument_types) != len(signature.params):
            self._error(
                f"Function '{display_name}' expects {len(signature.params)} arguments, "
                f"got {len(argument_types)}.",
                node.position,
            )
        for expected, actual, arg in zip(signature.params, argument_types, node.args):
            self.expect(expected, actual, arg.value)
        return self._record(node, signature.ret)

    def _check_print_call(self, node: nodes.Call, argument_types: list[Type]) -> Type:
        for arg_type, arg in zip(argument_types, node.args):
            if isinstance(arg_type, (UnknownType, NeverType)):
                continue
            if arg_type not in (INT, BOOL, UNIT):
                self._error(
                    "The built-in 'print' only accepts Int, Bool or Unit "
                    f"arguments in oort-core, got {describe_type(arg_type)}.",
                    arg.value.position,
                )
        return self._record(node, UNIT)

    def visit_unary_expr(self, node: nodes.UnaryExpr) -> Type:
        operand_type = node.operand.accept(self)
        if operand_type is None:
            operand_type = UNKNOWN
        operator = node.op.text
        if operator in {"+", "-"}:
            self.expect(INT, operand_type, node.operand)
            return self._record(node, INT)
        if operator == "not":
            self.expect(BOOL, operand_type, node.operand)
            return self._record(node, BOOL)
        return self._unsupported(
            node, f"Unary operator '{operator}' is not supported in oort-core yet."
        )

    def visit_binary_expr(self, node: nodes.BinaryExpr) -> Type:
        left_type = node.lhs.accept(self)
        right_type = node.rhs.accept(self)
        if left_type is None:
            left_type = UNKNOWN
        if right_type is None:
            right_type = UNKNOWN
        operator = node.op.text

        if operator in _ARITHMETIC:
            self.expect(INT, left_type, node.lhs)
            self.expect(INT, right_type, node.rhs)
            return self._record(node, INT)
        if operator in _ORDERING:
            self.expect(INT, left_type, node.lhs)
            self.expect(INT, right_type, node.rhs)
            return self._record(node, BOOL)
        if operator in _EQUALITY:
            return self._check_equality(node, left_type, right_type)
        if operator == "/":
            return self._unsupported(
                node, "The '/' operator is not supported in oort-core yet; it produces a Float."
            )
        if operator == "**":
            return self._unsupported(
                node,
                "The '**' operator is not supported in oort-core yet; a negative "
                "exponent produces a Float.",
            )
        return self._unsupported(node, f"Operator '{operator}' is not supported in oort-core yet.")

    def _check_equality(self, node: nodes.BinaryExpr, left: Type, right: Type) -> Type:
        if isinstance(left, UnknownType) or isinstance(right, UnknownType):
            return self._record(node, BOOL)
        if left == right and (left in (INT, BOOL)):
            return self._record(node, BOOL)
        self._error(
            f"Operator '{node.op.text}' requires two Int or two Bool operands, "
            f"got {describe_type(left)} and {describe_type(right)}.",
            node.position,
        )
        return self._record(node, UNKNOWN)

    def visit_and_expr(self, node: nodes.AndExpr) -> Type:
        return self._check_boolean_operator(node)

    def visit_or_expr(self, node: nodes.OrExpr) -> Type:
        return self._check_boolean_operator(node)

    def _check_boolean_operator(self, node: nodes.BooleanExpr) -> Type:
        left_type = node.lhs.accept(self)
        right_type = node.rhs.accept(self)
        if left_type is None:
            left_type = UNKNOWN
        if right_type is None:
            right_type = UNKNOWN
        self.expect(BOOL, left_type, node.lhs)
        self.expect(BOOL, right_type, node.rhs)
        return self._record(node, BOOL)

    def visit_if_expr(self, node: nodes.IfExpr) -> Type:
        condition_type = node.condition.accept(self)
        if condition_type is None:
            condition_type = UNKNOWN
        self.expect(BOOL, condition_type, node.condition, "if condition must be Bool")

        then_type = node.if_block.accept(self) or UNKNOWN
        if node.else_block is None:
            return self._record(node, UNIT)

        else_type = node.else_block.accept(self) or UNKNOWN
        joined = join_types(then_type, else_type)
        if joined is None:
            self._error(
                "The branches of this if have incompatible types: "
                f"{describe_type(then_type)} and {describe_type(else_type)}.",
                node.position,
            )
            return self._record(node, UNKNOWN)
        return self._record(node, joined)

    # ------------------------------------------------------------------
    # Annotations, diagnostics and unsupported constructs
    # ------------------------------------------------------------------

    def resolve_annotation(self, node: nodes.ASTNode, *, allow_unit: bool) -> Type:
        if not isinstance(node, nodes.Name):
            self._error(
                "Only Int, Bool and Unit type names are supported in oort-core.",
                node.position,
            )
            return UNKNOWN
        if node.id == "Int":
            return INT
        if node.id == "Bool":
            return BOOL
        if node.id == "Unit":
            if allow_unit:
                return UNIT
            self._error(
                "Unit is only allowed as a function return type in oort-core.",
                node.position,
            )
            return UNKNOWN
        self._error(
            f"Unknown type '{node.id}' in oort-core. Known types: Int, Bool, Unit.",
            node.position,
        )
        return UNKNOWN

    def expect(
        self,
        expected: Type,
        actual: Type,
        node: nodes.ASTNode,
        message: str | None = None,
    ) -> None:
        if is_assignable(expected, actual):
            return
        if message is None:
            message = f"Expected {describe_type(expected)}, got {describe_type(actual)}."
        else:
            message = f"{message}, got {describe_type(actual)}."
        self._error(message, node.position)

    def _record(self, node: nodes.ASTNode, type_: Type) -> Type:
        node.metadata["type"] = describe_type(type_)
        return type_

    def _error(self, message: str, position) -> None:
        self.error_handler.add(TypeCheckError(message, position), self.input_info)

    def _unsupported(self, node: nodes.ASTNode, message: str | None = None) -> Type:
        if message is None:
            message = f"{type(node).__name__} is not supported in oort-core yet."
        self.error_handler.add(UnsupportedSyntax(message, node.position), self.input_info)
        return UNKNOWN

    # Any AST kind without an explicit visitor method is out of the probe.
    def visit_children(self, node) -> Type:
        if node is None:
            return UNIT
        return self._unsupported(node)

    def visit_class_def(self, node: nodes.ClassDef) -> Type:
        return self._unsupported(node, "Classes are not supported in oort-core yet.")

    def visit_while_expr(self, node: nodes.WhileExpr) -> Type:
        return self._unsupported(node, "Loops are not supported in oort-core yet.")

    def visit_for_expr(self, node: nodes.ForExpr) -> Type:
        return self._unsupported(node, "Loops are not supported in oort-core yet.")

    def visit_continue_expr(self, node: nodes.ContinueExpr) -> Type:
        return self._unsupported(node, "Loops are not supported in oort-core yet.")

    def visit_break_expr(self, node: nodes.BreakExpr) -> Type:
        return self._unsupported(node, "Loops are not supported in oort-core yet.")

    def visit_import_stmt(self, node: nodes.ImportStmt) -> Type:
        if not self.module_level:
            return self._unsupported(node, "Imports are only allowed at module top level.")
        module_type = self._resolve_import(node, node.module_path)
        name = node.alias or self._derive_binding_name(node.module_path)
        if name is None:
            self._error(
                f"Cannot derive a binding name from module path {node.module_path!r}; "
                "use 'as <name>' to choose one.",
                node.position,
            )
            return UNIT
        if module_type is None:
            # Keep the binding to avoid cascades; the import error already fails.
            self.declare(name, UNKNOWN, mutable=False, position=node.position)
            return UNIT
        self.declare(name, module_type, mutable=False, position=node.position)
        node.metadata["type"] = describe_type(module_type)
        return UNIT

    def visit_import_from_stmt(self, node: nodes.ImportFromStmt) -> Type:
        if not self.module_level:
            return self._unsupported(node, "Imports are only allowed at module top level.")
        module_type = self._resolve_import(node, node.module_path)
        if module_type is None:
            for source_name, alias in node.names.items():
                self.declare(
                    alias or source_name,
                    UNKNOWN,
                    mutable=False,
                    position=node.position,
                )
            return UNIT
        for source_name, alias in node.names.items():
            export_type = module_type.get(source_name)
            if export_type is None:
                self._error(
                    f"Module {node.module_path!r} does not export {source_name!r}.",
                    node.position,
                )
                export_type = UNKNOWN
            self.declare(
                alias or source_name,
                export_type,
                mutable=False,
                position=node.position,
            )
        return UNIT

    def _resolve_import(
        self, node: nodes.ImportStmt | nodes.ImportFromStmt, spec: str
    ) -> ModuleType | None:
        if self.module_resolver is None:
            self._error(
                "Module imports require a compiler context in oort-core.",
                node.position,
            )
            return None
        info = self.module_resolver(spec, self.input_info.module_dir, node.position)
        if info is None:
            return None
        if info.dialect_name == "native":
            self._error(
                "Native modules are not supported in oort-core imports yet.",
                node.position,
            )
            return None
        if info.dialect_name != self.dialect.name:
            self._error(
                f"Cannot import a {info.dialect_name!r} module from an "
                f"{self.dialect.name!r} module; cross-dialect imports require "
                f"an explicit FFI boundary.",
                node.position,
            )
            return None
        return ModuleType(info.name, info.exports)

    @staticmethod
    def _derive_binding_name(spec: str) -> str | None:
        name = PurePosixPath(spec.replace("\\", "/")).name
        if name.lower().endswith(".ort"):
            name = name[: -len(".ort")]
        return name if name.isidentifier() else None

    def visit_attribute(self, node: nodes.Attribute) -> Type:
        value_type = node.value.accept(self)
        if isinstance(value_type, UnknownType):
            return self._record(node, UNKNOWN)
        if isinstance(value_type, ModuleType):
            export_type = value_type.get(node.attribute)
            if export_type is None:
                self._error(
                    f"Module {value_type.name!r} does not export {node.attribute!r}.",
                    node.position,
                )
                return self._record(node, UNKNOWN)
            return self._record(node, export_type)
        return self._unsupported(
            node,
            "Attribute access is only supported on imported modules in oort-core yet.",
        )

    def visit_subscript(self, node: nodes.Subscript) -> Type:
        return self._unsupported(node, "Subscripts are not supported in oort-core yet.")

    def visit_slice_literal(self, node: nodes.SliceLiteral) -> Type:
        return self._unsupported(node, "Slices are not supported in oort-core yet.")

    def visit_list_literal(self, node: nodes.ListLiteral) -> Type:
        return self._unsupported(node, "Lists are not supported in oort-core yet.")

    def visit_tuple_literal(self, node: nodes.TupleLiteral) -> Type:
        return self._unsupported(node, "Tuples are not supported in oort-core yet.")

    def visit_dict_literal(self, node: nodes.DictLiteral) -> Type:
        return self._unsupported(node, "Dicts are not supported in oort-core yet.")

    def visit_set_literal(self, node: nodes.SetLiteral) -> Type:
        return self._unsupported(node, "Sets are not supported in oort-core yet.")

    def visit_float_constant(self, node: nodes.FloatConstant) -> Type:
        return self._unsupported(node, "Float is not supported in oort-core yet.")

    def visit_string_constant(self, node: nodes.StringConstant) -> Type:
        return self._unsupported(node, "String is not supported in oort-core yet.")

    def visit_null_constant(self, node: nodes.NullConstant) -> Type:
        return self._unsupported(node, "null is not supported in oort-core yet.")

    def visit_ellipsis_constant(self, node: nodes.EllipsisConstant) -> Type:
        return self._unsupported(node, "Ellipsis is not supported in oort-core yet.")

    def visit_yield_expr(self, node: nodes.YieldExpr) -> Type:
        return self._unsupported(node, "Generators are not supported in oort-core yet.")

    def visit_await_expr(self, node: nodes.AwaitExpr) -> Type:
        return self._unsupported(node, "Async/await is not supported in oort-core yet.")

    def visit_macro_def(self, node: nodes.MacroDef) -> Type:
        return self._unsupported(node, "Macros are not supported in oort-core yet.")

    def visit_macro_call(self, node: nodes.MacroCall) -> Type:
        return self._unsupported(node, "Macros are not supported in oort-core yet.")

    def visit_compiler_attribute(self, node: nodes.CompilerAttribute) -> Type:
        return self._unsupported(node, "Compiler attributes are not supported in oort-core yet.")

    def visit_implicit_super_expr(self, node: nodes.ImplicitSuperExpr) -> Type:
        return self._unsupported(node, "super is not supported in oort-core yet.")
