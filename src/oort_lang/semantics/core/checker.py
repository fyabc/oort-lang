#! /usr/bin/env python

"""Independent static checker for the `oort-core` thin probe.

The checker is intentionally small: `Int`, `Float`, `Bool`, `String`, `Unit`,
collections, functions, monomorphic enums and static classes with fixed slots.
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
from .definite_assignment import DefiniteAssignmentAnalyzer, SlotFact
from .types import (
    BOOL,
    FLOAT,
    INT,
    NEVER,
    STRING,
    UNIT,
    UNKNOWN,
    AdtType,
    ClassType,
    ConstructorInfo,
    CoreModuleInfo,
    DictType,
    FunctionType,
    ListType,
    ModuleType,
    NeverType,
    SetType,
    SlotInfo,
    TupleType,
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
_RESERVED_TYPE_NAMES = frozenset(
    {"Int", "Float", "Bool", "String", "Unit", "List", "Set", "Dict", "Tuple", "_"}
)


def _is_numeric(type_: Type) -> bool:
    return type_ in (INT, FLOAT)


def _is_special_name(name: str) -> bool:
    return len(name) > 4 and name.startswith("__") and name.endswith("__")


def _is_container(type_: Type) -> bool:
    return isinstance(type_, (ListType, SetType, DictType, TupleType))


def _is_same_container(left: Type, right: Type) -> bool:
    return type(left) is type(right) and is_assignable(left, right) and is_assignable(right, left)


def _supports_value_equality(type_: Type) -> bool:
    if isinstance(type_, UnknownType):
        return True
    if type_ in (INT, FLOAT, BOOL, STRING):
        return True
    if isinstance(type_, (ListType, SetType)):
        return _supports_value_equality(type_.element)
    if isinstance(type_, DictType):
        return _supports_value_equality(type_.key) and _supports_value_equality(type_.value)
    if isinstance(type_, TupleType):
        return all(_supports_value_equality(element) for element in type_.elements)
    return False


def _is_valid_key_type(type_: Type) -> bool:
    if isinstance(type_, UnknownType):
        return True
    if type_ in (INT, FLOAT, BOOL, STRING) or isinstance(type_, AdtType):
        return True
    if isinstance(type_, TupleType):
        return all(_is_valid_key_type(element) for element in type_.elements)
    return False


@dataclasses.dataclass(slots=True)
class NameInfo:
    type: Type
    mutable: bool
    is_function: bool = False


@dataclasses.dataclass(slots=True)
class PatternResult:
    bindings: list[tuple[str, Type, SourcePosition]]
    covered: set[str] = dataclasses.field(default_factory=set)
    covers_all: bool = False
    irrefutable: bool = False
    failed: bool = False


@dataclasses.dataclass(slots=True)
class _ReturnInfer:
    """Return-type inference state for one function body being checked.

    Pushed on ``CoreTypeChecker._infer_stack`` while the body of a function
    without a return annotation is checked; ``returns`` collects the types of
    its ``return`` expressions and ``recursive`` is set when the body calls the
    function itself (such functions must keep an explicit annotation).
    """

    name: str
    node: nodes.FunctionDef
    returns: list[Type] = dataclasses.field(default_factory=list)
    recursive: bool = False


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
        self.enums: dict[str, AdtType] = {}
        self.constructor_names: dict[str, AdtType] = {}
        self.classes: dict[str, ClassType] = {}
        self.current_class: ClassType | None = None
        self._in_initializer = False
        self._loop_depth = 0
        # Parallel to function-body nesting: an entry is a `_ReturnInfer` when
        # that function's return type is being inferred, else None. The top
        # entry belongs to the innermost function currently being checked.
        self._infer_stack: list[_ReturnInfer | None] = []

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

    def _check_statements_expected(
        self, statements: Iterable[nodes.ASTNode], expected: Type
    ) -> Type:
        statement_list = list(statements)
        result: Type = UNIT
        saw_never = False
        last_index = len(statement_list) - 1
        for index, stmt in enumerate(statement_list):
            if index == last_index and not saw_never:
                statement_type = self._check_expr(stmt, expected)
            else:
                statement_type = stmt.accept(self) or UNKNOWN
            if isinstance(statement_type, NeverType):
                saw_never = True
            elif not saw_never:
                result = statement_type
        return NEVER if saw_never else result

    def _check_expr(
        self,
        node: nodes.ASTNode,
        expected: Type,
        message: str | None = None,
    ) -> Type:
        if not isinstance(expected, UnknownType):
            if isinstance(node, nodes.IfExpr):
                return self._check_if_expected(node, expected)
            if isinstance(node, nodes.BlockExpr):
                return self._check_block_expected(node, expected)
            if isinstance(node, nodes.MatchExpr):
                return self._check_match(node, expected)

        if isinstance(
            node, (nodes.ListLiteral, nodes.TupleLiteral, nodes.DictLiteral, nodes.SetLiteral)
        ):
            return self._check_collection_literal(node, expected)

        if isinstance(node, nodes.FunctionDef) and node.is_lambda:
            # Thread the expected return type into the lambda; without one the
            # lambda infers its return type from the body.
            actual = self._check_lambda(node, expected)
            if isinstance(actual, NeverType):
                return NEVER
            self.expect(expected, actual, node, message)
            if isinstance(expected, UnknownType):
                return actual
            return expected

        actual = node.accept(self)
        if actual is None:
            actual = UNKNOWN
        if isinstance(actual, NeverType):
            return NEVER
        self.expect(expected, actual, node, message)
        if isinstance(expected, UnknownType):
            return actual
        return expected

    def _check_block_expected(self, node: nodes.BlockExpr, expected: Type) -> Type:
        previous_module_level = self.module_level
        self.module_level = False
        self.scopes.append({})
        try:
            result = self._check_statements_expected(node.statements, expected)
        finally:
            self.scopes.pop()
            self.module_level = previous_module_level

        if isinstance(result, NeverType):
            return NEVER
        if isinstance(result, UnknownType):
            return UNKNOWN
        if not is_assignable(expected, result):
            self.expect(expected, result, node)
            return expected
        return expected

    def _check_if_expected(self, node: nodes.IfExpr, expected: Type) -> Type:
        condition_type = node.condition.accept(self) or UNKNOWN
        self.expect(BOOL, condition_type, node.condition, "if condition must be Bool")

        then_type = self._check_block_expected(node.if_block, expected)
        if node.else_block is None:
            if expected != UNIT:
                self._error(
                    f"An if without else has type Unit, expected {describe_type(expected)}.",
                    node.position,
                )
            return UNIT

        else_type = self._check_block_expected(node.else_block, expected)
        if isinstance(then_type, NeverType) and isinstance(else_type, NeverType):
            return NEVER
        return expected

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

        if annotation is not None:
            type_ = annotation
            if not isinstance(annotation, UnknownType):
                self._check_expr(node.init_value, annotation)
        else:
            init_type = node.init_value.accept(self)
            if init_type is None:
                init_type = UNKNOWN
            if isinstance(init_type, UnknownType):
                # The initializer already reported an error; do not cascade.
                type_ = UNKNOWN
            elif isinstance(init_type, (NeverType, ModuleType)) or init_type == UNIT:
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
        if isinstance(node.lhs, nodes.Attribute):
            self._check_slot_assignment(node)
            return UNIT
        if not isinstance(node.lhs, nodes.Name):
            return self._unsupported(
                node,
                "Only plain names and class slots can be assigned in oort-core.",
            )

        info = self.lookup(node.lhs.id)
        if info is None:
            self._error(f"Unknown name '{node.lhs.id}'.", node.lhs.position)
            node.rhs.accept(self)
            return UNIT
        if not info.mutable:
            self._error(
                f"Cannot assign to immutable binding '{node.lhs.id}' (declared with `val`).",
                node.position,
            )
            node.rhs.accept(self)
            return UNIT

        self._check_expr(node.rhs, info.type)
        node.lhs.metadata["type"] = describe_type(info.type)
        return UNIT

    def _check_slot_assignment(self, node: nodes.Assignment) -> None:
        assert isinstance(node.lhs, nodes.Attribute)
        receiver_type = node.lhs.value.accept(self) or UNKNOWN
        if isinstance(receiver_type, UnknownType):
            node.rhs.accept(self)
            return
        if not isinstance(receiver_type, ClassType):
            self._error(
                "Only slots of class instances can be assigned in oort-core.",
                node.lhs.position,
            )
            node.rhs.accept(self)
            return
        slot = receiver_type.slot(node.lhs.attribute)
        if slot is None:
            if receiver_type.method(node.lhs.attribute) is not None:
                self._error(
                    f"Cannot assign to method '{node.lhs.attribute}'.",
                    node.lhs.position,
                )
            else:
                self._error(
                    f"Class '{receiver_type.name}' has no slot '{node.lhs.attribute}'.",
                    node.lhs.position,
                )
            node.rhs.accept(self)
            return
        if not slot.mutable and not (self._in_initializer and not slot.has_initializer):
            self._error(
                f"Cannot assign to read-only slot '{slot.name}' (declared with `val`).",
                node.lhs.position,
            )
        self._check_expr(node.rhs, slot.slot_type)
        node.lhs.metadata["type"] = describe_type(slot.slot_type)
        return

    def visit_class_def(self, node: nodes.ClassDef) -> Type:
        if not self.module_level:
            return self._unsupported(
                node, "Class declarations are only allowed at module top level in oort-core."
            )
        if node.type_params:
            return self._unsupported(node, "Generic classes are not supported in oort-core yet.")
        if node.bases:
            return self._unsupported(node, "Class inheritance is not supported in oort-core yet.")
        if node.meta is not None:
            return self._unsupported(node, "Metaclasses are not supported in oort-core yet.")
        if len(node.names) != 1:
            return self._unsupported(node, "Namespaced classes are not supported in oort-core yet.")

        name = node.name
        if name in _RESERVED_TYPE_NAMES or name in self.classes or name in self.enums:
            self._error(f"Type name '{name}' is already declared or reserved.", node.name_position)
            return UNIT

        class_type = ClassType(self._module_origin(), name)
        self.classes[name] = class_type

        slot_infos: list[SlotInfo] = []
        slot_decls: list[tuple[SlotInfo, nodes.VarDecl, nodes.SingleDeclTarget]] = []
        methods: list[tuple[str, FunctionType, nodes.FunctionDef]] = []
        slot_names: set[str] = set()
        method_names: set[str] = set()
        init_method: tuple[FunctionType, nodes.FunctionDef] | None = None

        for stmt in node.body.statements:
            if isinstance(stmt, nodes.VarDecl):
                if len(stmt.decl_targets) != 1:
                    self._unsupported(
                        stmt, "Multi-target slot declarations are not supported in oort-core yet."
                    )
                    continue
                target = stmt.decl_targets[0]
                if _is_special_name(target.name):
                    self._error(
                        f"Slot name '{target.name}' is reserved in oort-core.",
                        target.position,
                    )
                    continue
                if target.name in slot_names or target.name in method_names:
                    self._error(
                        f"Duplicate member '{target.name}' in class '{name}'.",
                        target.position,
                    )
                    continue
                if target.type_expr is None:
                    self._error(
                        f"Slot '{target.name}' requires a type annotation in oort-core.",
                        target.position,
                    )
                    slot_type: Type = UNKNOWN
                else:
                    slot_type = self.resolve_annotation(target.type_expr, allow_unit=False)
                info = SlotInfo(
                    target.name,
                    slot_type,
                    stmt.mutable,
                    stmt.init_value is not None,
                )
                slot_names.add(target.name)
                slot_infos.append(info)
                slot_decls.append((info, stmt, target))
                target.metadata["type"] = describe_type(slot_type)
                continue

            if isinstance(stmt, nodes.FunctionDef) and not stmt.is_lambda:
                if (
                    stmt.is_extension
                    or stmt.is_class_method
                    or stmt.operator_symbol is not None
                    or stmt.type_params
                ):
                    self._unsupported(
                        stmt,
                        "Only plain instance methods are supported in oort-core classes yet.",
                    )
                    continue
                method_name = stmt.name
                if _is_special_name(method_name) and method_name != "__init__":
                    self._error(
                        f"Special method '{method_name}' is not supported in oort-core.",
                        stmt.name_position,
                    )
                    continue
                if method_name == "on_missing":
                    self._unsupported(
                        stmt,
                        "Attribute fallback hooks are only supported in oort-object.",
                    )
                    continue
                if method_name in method_names or method_name in slot_names:
                    self._error(
                        f"Duplicate member '{method_name}' in class '{name}'.",
                        stmt.name_position,
                    )
                    continue
                display_name = f"{name}.{method_name}"
                if method_name == "__init__":
                    signature = self._check_init_signature(stmt, display_name)
                else:
                    signature = self._build_signature(
                        stmt, display_name, infer_return=stmt.ret_type is None
                    )
                stmt.metadata["type"] = describe_type(signature)
                method_names.add(method_name)
                methods.append((method_name, signature, stmt))
                if method_name == "__init__":
                    init_method = (signature, stmt)
                continue

            self._unsupported(
                stmt,
                "Only slot and method declarations are allowed in oort-core class bodies.",
            )

        class_type.slots = tuple(slot_infos)
        class_type.methods = tuple(
            (method_name, signature) for method_name, signature, _ in methods
        )

        constructor = FunctionType(
            init_method[0].params if init_method is not None else (), class_type
        )
        self.declare(
            name,
            constructor,
            mutable=False,
            position=node.name_position,
            is_function=True,
        )
        node.metadata["type"] = describe_type(class_type)

        for info, declaration, _ in slot_decls:
            if declaration.init_value is not None and not isinstance(info.slot_type, UnknownType):
                self._check_expr(declaration.init_value, info.slot_type)

        self._infer_and_check_methods(methods, class_type, name, method_names)

        slot_facts = [
            SlotFact(info.name, info.mutable, info.has_initializer, target.position)
            for info, _, target in slot_decls
        ]
        uninitialized = [info.name for info in slot_infos if not info.has_initializer]
        if init_method is None:
            if uninitialized:
                self._error(
                    f"Class '{name}' has slots without initializers but no "
                    f"__init__: {', '.join(uninitialized)}.",
                    node.name_position,
                )
        else:
            DefiniteAssignmentAnalyzer(slot_facts, self._error).check(init_method[1])
        return UNIT

    def _check_init_signature(self, node: nodes.FunctionDef, display_name: str) -> FunctionType:
        if node.ret_type is not None:
            return_type = self.resolve_annotation(node.ret_type, allow_unit=True)
            if not (return_type == UNIT or isinstance(return_type, UnknownType)):
                self._error(
                    f"Constructor '{display_name}' must return Unit.",
                    node.ret_type.position,
                )
        return self._build_signature(node, display_name, forced_return=UNIT)

    def _check_method_body(
        self,
        node: nodes.FunctionDef,
        signature: FunctionType,
        display_name: str,
        class_type: ClassType,
        *,
        is_initializer: bool,
        infer_return: bool = False,
    ) -> FunctionType:
        previous_class = self.current_class
        previous_initializer = self._in_initializer
        self.current_class = class_type
        self._in_initializer = is_initializer
        try:
            return self._check_function_body(
                node,
                signature,
                display_name,
                this_type=class_type,
                infer_return=infer_return,
            )
        finally:
            self.current_class = previous_class
            self._in_initializer = previous_initializer

    def _method_dependencies(self, body: nodes.ASTNode, method_names: set[str]) -> set[str]:
        """Same-class methods referenced in a method body (conservative scan).

        Collects attribute names that match a method of the class, covering
        ``this.m()`` calls, calls on other instances and method-as-value uses.
        Matching by name regardless of receiver may add a spurious edge, which
        only constrains the inference order further and stays sound.
        """
        deps: set[str] = set()

        def walk(node: nodes.ASTNode | None) -> None:
            if node is None:
                return
            if isinstance(node, nodes.Attribute) and node.attribute in method_names:
                deps.add(node.attribute)
            for child in node.children():
                walk(child)

        walk(body)
        return deps

    def _infer_and_check_methods(
        self,
        methods: list[tuple[str, FunctionType, nodes.FunctionDef]],
        class_type: ClassType,
        class_name: str,
        method_names: set[str],
    ) -> None:
        """Infer unannotated method returns in dependency order, then check bodies.

        Methods are inferred callees-first (topological order) so a method never
        sees the placeholder return of a method it calls. Methods on a recursive
        call cycle cannot be inferred and require an explicit annotation.
        """
        by_name = {method_name: (sig, fn) for method_name, sig, fn in methods}
        unannotated = [
            method_name
            for method_name, _, fn in methods
            if fn.ret_type is None and method_name != "__init__"
        ]
        deps = {
            method_name: self._method_dependencies(by_name[method_name][1].body, method_names)
            for method_name in unannotated
        }
        pending = set(unannotated)
        order: list[str] = []
        while pending:
            ready = next((m for m in pending if not (deps[m] & pending)), None)
            if ready is None:
                break
            pending.remove(ready)
            order.append(ready)
        blocked = pending  # recursive cycles, including self-recursion

        for method_name in order:
            signature, function = by_name[method_name]
            inferred = self._check_method_body(
                function,
                signature,
                f"{class_name}.{method_name}",
                class_type,
                is_initializer=False,
                infer_return=True,
            )
            class_type.methods = tuple(
                (n, inferred if n == method_name else s) for n, s in class_type.methods
            )
            function.metadata["type"] = describe_type(inferred)

        for method_name in blocked:
            signature, function = by_name[method_name]
            self._error(
                f"Recursive method '{class_name}.{method_name}' requires a return type "
                f"annotation in oort-core; add '-> T'.",
                function.name_position,
            )
            self._check_method_body(
                function,
                signature,
                f"{class_name}.{method_name}",
                class_type,
                is_initializer=False,
            )

        # Annotated methods and __init__ are checked last so their call sites
        # see the already-inferred return types.
        for method_name, signature, function in methods:
            if function.ret_type is not None or method_name == "__init__":
                self._check_method_body(
                    function,
                    signature,
                    f"{class_name}.{method_name}",
                    class_type,
                    is_initializer=method_name == "__init__",
                )

    def visit_enum_def(self, node: nodes.EnumDef) -> Type:
        if not self.module_level:
            return self._unsupported(
                node, "Enum declarations are only allowed at module top level in oort-core."
            )
        if node.type_params:
            return self._unsupported(node, "Generic enums are not supported in oort-core yet.")
        if node.name in _RESERVED_TYPE_NAMES:
            self._error(
                f"Enum name '{node.name}' is reserved in oort-core.",
                node.name_position,
            )
            return UNIT
        if node.name in self.classes:
            self._error(f"Type name '{node.name}' is already declared.", node.name_position)
            return UNIT
        if node.name in self.enums:
            self._error(f"Enum '{node.name}' is already declared.", node.name_position)
            return UNIT
        if not node.constructors:
            self._error("An enum must declare at least one constructor.", node.position)
            return UNIT

        adt = AdtType(self._module_origin(), node.name)
        self.enums[node.name] = adt

        built: list[tuple[ConstructorInfo, nodes.EnumConstructor]] = []
        for case in node.constructors:
            if case.name == "_":
                self._error(
                    "Constructor name '_' is reserved for wildcard patterns.",
                    case.position,
                )
                continue
            if case.name in self.constructor_names:
                self._error(
                    f"Constructor '{case.name}' is already declared.",
                    case.position,
                )
                continue
            field_names: list[str] = []
            payload: list[Type] = []
            seen_fields: set[str] = set()
            for field in case.fields:
                if field.name in seen_fields:
                    self._error(
                        f"Duplicate field '{field.name}' in constructor '{case.name}'.",
                        field.position,
                    )
                seen_fields.add(field.name)
                field_names.append(field.name)
                if field.type_expr is None:
                    self._error(
                        f"Field '{field.name}' requires a type annotation in oort-core.",
                        field.position,
                    )
                    payload.append(UNKNOWN)
                else:
                    payload.append(self.resolve_annotation(field.type_expr, allow_unit=False))
            info = ConstructorInfo(case.name, tuple(field_names), tuple(payload))
            built.append((info, case))
            self.constructor_names[case.name] = adt

        adt.constructors = tuple(info for info, _ in built)
        for info, case in built:
            if info.payload:
                constructor_type: Type = FunctionType(info.payload, adt)
                is_function = True
            else:
                constructor_type = adt
                is_function = False
            self.declare(
                info.name,
                constructor_type,
                mutable=False,
                position=case.position,
                is_function=is_function,
            )
        node.metadata["type"] = describe_type(adt)
        return UNIT

    def _module_origin(self) -> str:
        path = self.input_info.module_path
        return str(path) if path is not None else self.input_info.module_name

    def visit_function_def(self, node: nodes.FunctionDef) -> Type:
        if node.is_lambda:
            return self._check_lambda(node)
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

        infer_return = node.ret_type is None
        signature = self._build_signature(node, node.name, infer_return=infer_return)
        # Declare before checking the body so self-recursive calls resolve; the
        # inferred return type is backfilled afterwards.
        self.declare(
            node.name,
            signature,
            mutable=False,
            position=node.name_position,
            is_function=True,
        )
        signature = self._check_function_body(node, signature, node.name, infer_return=infer_return)
        if infer_return:
            info = self.lookup(node.name)
            if info is not None:
                info.type = signature
        node.metadata["type"] = describe_type(signature)
        return UNIT

    def _check_lambda(self, node: nodes.FunctionDef, expected: Type = UNKNOWN) -> Type:
        if not node.has_explicit_param_list:
            return self._unsupported(
                node,
                "Lambdas without an explicit parameter list are not supported in oort-core yet.",
            )
        if node.type_params:
            return self._unsupported(node, "Generic lambdas are not supported in oort-core yet.")
        default_return: Type | None = None
        infer_return = False
        if node.ret_type is None:
            if isinstance(expected, FunctionType):
                # An expected function type supplies the return type (check mode).
                default_return = expected.ret
            else:
                infer_return = True
        signature = self._build_signature(
            node, "<lambda>", default_return=default_return, infer_return=infer_return
        )
        signature = self._check_function_body(
            node, signature, "<lambda>", infer_return=infer_return
        )
        node.metadata["type"] = describe_type(signature)
        return signature

    def _build_signature(
        self,
        node: nodes.FunctionDef,
        display_name: str,
        *,
        default_return: Type | None = None,
        forced_return: Type | None = None,
        infer_return: bool = False,
    ) -> FunctionType:
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
            param_types.append(self.resolve_annotation(param.type_expr, allow_unit=False))

        return_type: Type
        if forced_return is not None:
            return_type = forced_return
        elif node.ret_type is None:
            if default_return is not None:
                return_type = default_return
            elif infer_return:
                # Placeholder: the body is checked in infer mode and the real
                # return type is computed afterwards (_check_function_body).
                return_type = UNKNOWN
            else:
                self._error(
                    f"Function '{display_name}' requires a return type annotation in oort-core.",
                    node.name_position,
                )
                return_type = UNKNOWN
        else:
            return_type = self.resolve_annotation(node.ret_type, allow_unit=True)
        return FunctionType(tuple(param_types), return_type)

    def _check_function_body(
        self,
        node: nodes.FunctionDef,
        signature: FunctionType,
        display_name: str,
        *,
        this_type: ClassType | None = None,
        infer_return: bool = False,
    ) -> FunctionType:
        """Check a function body; return its (possibly inferred) signature.

        With ``infer_return`` the body is checked in infer mode and the return
        type is computed from the collected ``return`` types joined with the
        fall-through body type. Otherwise the body is checked against the
        declared return type and the signature is returned unchanged.
        """
        previous_function = self.current_function
        previous_name = self.current_function_name
        previous_module_level = self.module_level
        self.current_function = signature
        self.current_function_name = display_name
        self.module_level = False
        self.scopes.append({})
        frame = _ReturnInfer(display_name, node) if infer_return else None
        self._infer_stack.append(frame)
        try:
            if this_type is not None:
                self.declare(
                    "this",
                    this_type,
                    mutable=False,
                    position=node.name_position,
                )
            for param, param_type in zip(node.params, signature.params):
                self.declare(
                    param.name,
                    param_type,
                    mutable=False,
                    position=param.position,
                )
            start_errors = self.error_handler.error_count
            expected = UNKNOWN if infer_return else signature.ret
            body_type = self._check_statements_expected(node.body.statements, expected)
        finally:
            self.scopes.pop()
            self._infer_stack.pop()
            self.current_function = previous_function
            self.current_function_name = previous_name
            self.module_level = previous_module_level

        if not infer_return:
            if (
                not isinstance(body_type, NeverType)
                and not is_assignable(signature.ret, body_type)
                and self.error_handler.error_count == start_errors
            ):
                self._error(
                    f"Function '{display_name}' is declared to return "
                    f"{describe_type(signature.ret)}, but its body has type "
                    f"{describe_type(body_type)}.",
                    node.position,
                )
            return signature

        assert frame is not None
        had_errors = self.error_handler.error_count != start_errors
        if frame.recursive:
            # A self-recursive call saw the placeholder return type, so the
            # body cannot pin it down; require an explicit annotation (as
            # Kotlin/Scala do for recursive functions).
            if not had_errors:
                self._error(
                    f"Recursive function '{display_name}' requires a return type "
                    f"annotation in oort-core; add '-> T'.",
                    node.name_position,
                )
            return FunctionType(signature.params, UNKNOWN)

        candidates = list(frame.returns)
        if not isinstance(body_type, NeverType):
            candidates.append(body_type)
        inferred: Type = NEVER
        conflict: tuple[Type, Type] | None = None
        for candidate in candidates:
            joined = join_types(inferred, candidate)
            if joined is None:
                conflict = (inferred, candidate)
                break
            inferred = joined
        if had_errors:
            return FunctionType(signature.params, UNKNOWN)
        if conflict is not None:
            self._error(
                f"The return types of function '{display_name}' are incompatible: "
                f"{describe_type(conflict[0])} and {describe_type(conflict[1])}.",
                node.position,
            )
            return FunctionType(signature.params, UNKNOWN)
        if isinstance(inferred, UnknownType):
            return FunctionType(signature.params, UNKNOWN)
        if isinstance(inferred, NeverType):
            inferred = UNIT
        return FunctionType(signature.params, inferred)

    def visit_return_expr(self, node: nodes.ReturnExpr) -> Type:
        if self.current_function is None:
            self._error("Return outside function.", node.position)
            return NEVER

        frame = self._infer_stack[-1] if self._infer_stack else None
        if frame is not None:
            # The current function's return type is being inferred: collect
            # this return's type instead of checking it against a declaration.
            if node.value is None:
                frame.returns.append(UNIT)
            else:
                frame.returns.append(node.value.accept(self))
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
        elif isinstance(return_type, UnknownType):
            node.value.accept(self)
        else:
            self._check_expr(node.value, return_type)
        return NEVER

    # ------------------------------------------------------------------
    # Expressions
    # ------------------------------------------------------------------

    def visit_int_constant(self, node: nodes.IntConstant) -> Type:
        return self._record(node, INT)

    def visit_float_constant(self, node: nodes.FloatConstant) -> Type:
        return self._record(node, FLOAT)

    def visit_string_constant(self, node: nodes.StringConstant) -> Type:
        return self._record(node, STRING)

    def visit_boolean_constant(self, node: nodes.BooleanConstant) -> Type:
        return self._record(node, BOOL)

    def visit_name(self, node: nodes.Name) -> Type:
        if node.id == "this":
            if self.current_class is None:
                self._error("'this' is only available inside methods.", node.position)
                return self._record(node, UNKNOWN)
            return self._record(node, self.current_class)
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

    def _mark_recursive_call(self, name: str) -> None:
        """Flag inference frames whose function is called from its own body.

        Only named functions can be called by name, so this detects the
        self-recursion that return-type inference cannot resolve (forward and
        mutual recursion are already rejected by source-order visibility).
        """
        for frame in self._infer_stack:
            if frame is not None and frame.name == name:
                frame.recursive = True

    def visit_call(self, node: nodes.Call) -> Type:
        if node.infix:
            return self._unsupported(node, "Infix calls are not supported in oort-core yet.")

        if isinstance(node.func, nodes.Name):
            name = node.func.id
            info = self.lookup(name)
            if info is None:
                if name == "print":
                    return self._check_print_call(node)
                if name == "len":
                    return self._check_len_call(node)
                self._error(f"Unknown function '{name}'.", node.func.position)
                self._infer_arguments(node)
                return self._record(node, UNKNOWN)
            if not isinstance(info.type, FunctionType):
                self._error(f"'{name}' is not callable.", node.func.position)
                self._infer_arguments(node)
                return self._record(node, UNKNOWN)
            signature = info.type
            display_name = name
            self._mark_recursive_call(name)
        else:
            callee_type = node.func.accept(self)
            if isinstance(callee_type, UnknownType):
                self._infer_arguments(node)
                return self._record(node, UNKNOWN)
            if not isinstance(callee_type, FunctionType):
                if isinstance(node.func, nodes.Attribute):
                    message = f"'{node.func.attribute}' is not callable."
                else:
                    message = "Expression is not callable."
                self._error(message, node.func.position)
                self._infer_arguments(node)
                return self._record(node, UNKNOWN)
            signature = callee_type
            display_name = (
                node.func.attribute if isinstance(node.func, nodes.Attribute) else "<expression>"
            )

        if len(node.args) != len(signature.params):
            self._error(
                f"Function '{display_name}' expects {len(signature.params)} arguments, "
                f"got {len(node.args)}.",
                node.position,
            )
        for index, arg in enumerate(node.args):
            if arg.keyword is not None or arg.kind != nodes.ArgumentKind.DEFAULT:
                self._unsupported(
                    arg,
                    "Keyword, variadic and block arguments are not supported in oort-core yet.",
                )
                continue
            if index < len(signature.params):
                self._check_expr(arg.value, signature.params[index])
            else:
                arg.value.accept(self)
        return self._record(node, signature.ret)

    def _infer_arguments(self, node: nodes.Call) -> None:
        for arg in node.args:
            if arg.keyword is not None or arg.kind != nodes.ArgumentKind.DEFAULT:
                self._unsupported(
                    arg,
                    "Keyword, variadic and block arguments are not supported in oort-core yet.",
                )
                continue
            arg.value.accept(self)

    def _check_print_call(self, node: nodes.Call) -> Type:
        for arg in node.args:
            if arg.keyword is not None or arg.kind != nodes.ArgumentKind.DEFAULT:
                self._unsupported(
                    arg,
                    "Keyword, variadic and block arguments are not supported in oort-core yet.",
                )
                continue
            arg_type = arg.value.accept(self)
            if arg_type is None:
                arg_type = UNKNOWN
            if isinstance(arg_type, (UnknownType, NeverType)):
                continue
            printable = isinstance(arg_type, (AdtType, ListType, SetType, DictType, TupleType))
            if arg_type not in (INT, FLOAT, BOOL, STRING, UNIT) and not printable:
                self._error(
                    "The built-in 'print' only accepts Int, Float, Bool, String, "
                    "Unit, enum or collection arguments in oort-core, "
                    f"got {describe_type(arg_type)}.",
                    arg.value.position,
                )
        return self._record(node, UNIT)

    def _check_len_call(self, node: nodes.Call) -> Type:
        if len(node.args) != 1:
            self._error(
                f"The built-in 'len' expects 1 argument, got {len(node.args)}.",
                node.position,
            )
            self._infer_arguments(node)
            return self._record(node, INT)
        argument = node.args[0]
        if argument.keyword is not None or argument.kind != nodes.ArgumentKind.DEFAULT:
            self._unsupported(
                argument,
                "Keyword, variadic and block arguments are not supported in oort-core yet.",
            )
            return self._record(node, INT)
        argument_type = argument.value.accept(self) or UNKNOWN
        if isinstance(argument_type, (UnknownType, NeverType)):
            return self._record(node, INT)
        if argument_type == STRING or isinstance(
            argument_type, (ListType, SetType, DictType, TupleType)
        ):
            return self._record(node, INT)
        self._error(
            "The built-in 'len' only accepts String or collection arguments in "
            f"oort-core, got {describe_type(argument_type)}.",
            argument.value.position,
        )
        return self._record(node, INT)

    def visit_unary_expr(self, node: nodes.UnaryExpr) -> Type:
        operand_type = node.operand.accept(self)
        if operand_type is None:
            operand_type = UNKNOWN
        operator = node.op.text
        if isinstance(operand_type, UnknownType):
            return self._record(node, UNKNOWN)
        if operator in {"+", "-"}:
            if not _is_numeric(operand_type):
                self._error(
                    f"Unary operator '{operator}' requires a number, "
                    f"got {describe_type(operand_type)}.",
                    node.position,
                )
                return self._record(node, UNKNOWN)
            return self._record(node, operand_type)
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

        if operator in _ARITHMETIC or operator == "/":
            return self._check_arithmetic(node, left_type, right_type)
        if operator in _ORDERING:
            return self._check_ordering(node, left_type, right_type)
        if operator in _EQUALITY:
            return self._check_equality(node, left_type, right_type)
        if operator == "**":
            return self._unsupported(
                node,
                "The '**' operator is not supported in oort-core yet; its result "
                "type depends on the exponent.",
            )
        return self._unsupported(node, f"Operator '{operator}' is not supported in oort-core yet.")

    def _check_arithmetic(self, node: nodes.BinaryExpr, left: Type, right: Type) -> Type:
        operator = node.op.text
        if isinstance(left, UnknownType) or isinstance(right, UnknownType):
            return self._record(node, UNKNOWN)
        if operator == "+" and left == STRING and right == STRING:
            return self._record(node, STRING)
        if _is_numeric(left) and _is_numeric(right):
            if operator == "/" or FLOAT in (left, right):
                return self._record(node, FLOAT)
            return self._record(node, INT)
        if operator == "+":
            message = (
                "Operator '+' requires two numbers or two String operands, "
                f"got {describe_type(left)} and {describe_type(right)}."
            )
        else:
            message = (
                f"Operator '{operator}' requires two numbers, "
                f"got {describe_type(left)} and {describe_type(right)}."
            )
        self._error(message, node.position)
        return self._record(node, UNKNOWN)

    def _check_ordering(self, node: nodes.BinaryExpr, left: Type, right: Type) -> Type:
        if isinstance(left, UnknownType) or isinstance(right, UnknownType):
            return self._record(node, BOOL)
        if (_is_numeric(left) and _is_numeric(right)) or (left == STRING and right == STRING):
            return self._record(node, BOOL)
        self._error(
            f"Operator '{node.op.text}' requires two numbers or two String operands, "
            f"got {describe_type(left)} and {describe_type(right)}.",
            node.position,
        )
        return self._record(node, UNKNOWN)

    def _check_equality(self, node: nodes.BinaryExpr, left: Type, right: Type) -> Type:
        if isinstance(left, UnknownType) or isinstance(right, UnknownType):
            return self._record(node, BOOL)
        if isinstance(left, AdtType) or isinstance(right, AdtType):
            self._error(
                "Enum equality is not supported in oort-core yet; use match.",
                node.position,
            )
            return self._record(node, UNKNOWN)
        if isinstance(left, ClassType) or isinstance(right, ClassType):
            self._error(
                "Class equality is not supported in oort-core yet.",
                node.position,
            )
            return self._record(node, UNKNOWN)
        if (_is_numeric(left) and _is_numeric(right)) or (left == right and left in (BOOL, STRING)):
            return self._record(node, BOOL)
        if _is_container(left) and _is_container(right):
            if not (_supports_value_equality(left) and _supports_value_equality(right)):
                self._error(
                    "Equality is not supported for collections containing enums "
                    "or functions in oort-core yet.",
                    node.position,
                )
                return self._record(node, UNKNOWN)
            if _is_same_container(left, right):
                return self._record(node, BOOL)
            self._error(
                f"Operator '{node.op.text}' requires both operands to have the same "
                f"collection type, got {describe_type(left)} and {describe_type(right)}.",
                node.position,
            )
            return self._record(node, UNKNOWN)
        self._error(
            f"Operator '{node.op.text}' requires two numbers, two Bool or two String "
            f"operands, got {describe_type(left)} and {describe_type(right)}.",
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

    def visit_match_expr(self, node: nodes.MatchExpr) -> Type:
        return self._check_match(node, None)

    def _check_match(self, node: nodes.MatchExpr, expected: Type | None) -> Type:
        scrutinee_type = node.scrutinee.accept(self) or UNKNOWN
        if isinstance(scrutinee_type, UnknownType):
            scrutinee_ok = False
        elif isinstance(scrutinee_type, AdtType):
            scrutinee_ok = True
        else:
            self._error(
                "The scrutinee of match must have an enum type in oort-core, "
                f"got {describe_type(scrutinee_type)}.",
                node.scrutinee.position,
            )
            scrutinee_type = UNKNOWN
            scrutinee_ok = False

        if not node.arms:
            self._error("match requires at least one arm.", node.position)
            return self._record(node, UNKNOWN)

        arm_types: list[Type] = []
        covered: set[str] = set()
        covers_all = False
        any_failed = False
        for arm in node.arms:
            self.scopes.append({})
            try:
                result = self._check_pattern(arm.pattern, scrutinee_type)
                for name, type_, position in result.bindings:
                    self.declare(name, type_, mutable=False, position=position)
                if expected is None or isinstance(expected, UnknownType):
                    body_type = arm.body.accept(self) or UNKNOWN
                else:
                    body_type = self._check_expr(arm.body, expected)
            finally:
                self.scopes.pop()
            arm_types.append(body_type)
            covered.update(result.covered)
            covers_all = covers_all or result.covers_all
            any_failed = any_failed or result.failed

        joined = arm_types[0]
        for arm_type in arm_types[1:]:
            next_joined = join_types(joined, arm_type)
            if next_joined is None:
                self._error(
                    "The arms of this match have incompatible types: "
                    f"{describe_type(joined)} and {describe_type(arm_type)}.",
                    node.position,
                )
                joined = UNKNOWN
                break
            joined = next_joined

        if (
            scrutinee_ok
            and not any_failed
            and isinstance(scrutinee_type, AdtType)
            and not covers_all
        ):
            missing = [
                constructor.name
                for constructor in scrutinee_type.constructors
                if constructor.name not in covered
            ]
            if missing:
                self._error(
                    f"Match is not exhaustive; missing: {', '.join(missing)}.",
                    node.position,
                )
        return self._record(node, joined)

    def _check_pattern(self, pattern: nodes.Pattern, expected: Type) -> PatternResult:
        if isinstance(pattern, nodes.WildcardPattern):
            return PatternResult([], covers_all=True, irrefutable=True)
        if isinstance(pattern, nodes.NamePattern):
            return self._check_name_pattern(pattern, expected)
        if isinstance(pattern, nodes.ConstructorPattern):
            return self._check_constructor_pattern(pattern, expected)
        self._error("Unknown pattern kind.", pattern.position)
        return PatternResult([], failed=True)

    def _check_name_pattern(self, pattern: nodes.NamePattern, expected: Type) -> PatternResult:
        binding = (pattern.name, expected, pattern.position)
        if isinstance(expected, AdtType):
            constructor = expected.constructor(pattern.name)
            if constructor is not None:
                if constructor.payload:
                    self._error(
                        f"Constructor '{constructor.name}' expects "
                        f"{len(constructor.payload)} argument(s).",
                        pattern.position,
                    )
                    return PatternResult([binding], failed=True)
                return PatternResult(
                    [binding],
                    covered={constructor.name},
                    irrefutable=len(expected.constructors) == 1,
                )
            owner = self.constructor_names.get(pattern.name)
            if owner is not None:
                self._error(
                    f"'{pattern.name}' is not a constructor of enum '{expected.name}'.",
                    pattern.position,
                )
                return PatternResult([binding], failed=True)
        if isinstance(expected, UnknownType):
            return PatternResult([binding], covers_all=True, irrefutable=True)
        return PatternResult([binding], covers_all=True, irrefutable=True)

    def _check_constructor_pattern(
        self, pattern: nodes.ConstructorPattern, expected: Type
    ) -> PatternResult:
        if isinstance(expected, UnknownType):
            bindings: list[tuple[str, Type, SourcePosition]] = []
            for arg in pattern.args:
                result = self._check_pattern(arg, UNKNOWN)
                bindings.extend(result.bindings)
            return PatternResult(bindings, failed=True)

        if not isinstance(expected, AdtType):
            self._error(
                f"Constructor patterns require an enum type, got {describe_type(expected)}.",
                pattern.position,
            )
            bindings = []
            for arg in pattern.args:
                result = self._check_pattern(arg, UNKNOWN)
                bindings.extend(result.bindings)
            return PatternResult(bindings, failed=True)

        constructor = expected.constructor(pattern.name)
        if constructor is None:
            self._error(
                f"Enum '{expected.name}' has no constructor '{pattern.name}'.",
                pattern.position,
            )
            bindings = []
            for arg in pattern.args:
                result = self._check_pattern(arg, UNKNOWN)
                bindings.extend(result.bindings)
            return PatternResult(bindings, failed=True)

        if len(pattern.args) != len(constructor.payload):
            self._error(
                f"Constructor '{constructor.name}' expects "
                f"{len(constructor.payload)} argument(s), got {len(pattern.args)}.",
                pattern.position,
            )

        bindings = []
        irrefutable = True
        failed = len(pattern.args) != len(constructor.payload)
        for arg, payload_type in zip(pattern.args, constructor.payload):
            result = self._check_pattern(arg, payload_type)
            bindings.extend(result.bindings)
            irrefutable = irrefutable and result.irrefutable
            failed = failed or result.failed

        return PatternResult(
            bindings,
            covered={constructor.name} if irrefutable else set(),
            irrefutable=len(expected.constructors) == 1 and irrefutable,
            failed=failed,
        )

    # ------------------------------------------------------------------
    # Annotations, diagnostics and unsupported constructs
    # ------------------------------------------------------------------

    def resolve_annotation(self, node: nodes.ASTNode, *, allow_unit: bool) -> Type:
        if isinstance(node, nodes.BinaryExpr) and node.op.text == "->":
            params = self._resolve_function_params(node.lhs)
            ret = self.resolve_annotation(node.rhs, allow_unit=True)
            return FunctionType(tuple(params), ret)
        if isinstance(node, nodes.Subscript):
            return self._resolve_container_type(node)
        if isinstance(node, nodes.TupleLiteral):
            self._error(
                "Tuple types are written Tuple[Int, Bool] in oort-core.",
                node.position,
            )
            return UNKNOWN
        if not isinstance(node, nodes.Name):
            self._error(
                "Only Int, Float, Bool, String, Unit and enum type names are supported "
                "in oort-core.",
                node.position,
            )
            return UNKNOWN
        if node.id == "Int":
            return INT
        if node.id == "Float":
            return FLOAT
        if node.id == "Bool":
            return BOOL
        if node.id == "String":
            return STRING
        if node.id == "Unit":
            if allow_unit:
                return UNIT
            self._error(
                "Unit is only allowed as a function return type in oort-core.",
                node.position,
            )
            return UNKNOWN
        if node.id in {"List", "Set", "Dict", "Tuple"}:
            self._error(
                f"Type '{node.id}' requires type arguments; write {node.id}[...].",
                node.position,
            )
            return UNKNOWN
        class_type = self.classes.get(node.id)
        if class_type is not None:
            return class_type
        enum_type = self.enums.get(node.id)
        if enum_type is not None:
            return enum_type
        known = ", ".join(["Int", "Float", "Bool", "String", "Unit", *self.classes, *self.enums])
        self._error(
            f"Unknown type '{node.id}' in oort-core. Known types: {known}.",
            node.position,
        )
        return UNKNOWN

    def _resolve_function_params(self, node: nodes.ASTNode) -> list[Type]:
        if isinstance(node, nodes.Name):
            return [self.resolve_annotation(node, allow_unit=False)]
        if isinstance(node, nodes.TupleLiteral):
            return [self.resolve_annotation(element, allow_unit=False) for element in node.elements]
        if isinstance(node, nodes.BinaryExpr) and node.op.text == "->":
            return [self.resolve_annotation(node, allow_unit=False)]
        self._error(
            "Function parameter types must be a type name or a parenthesized list.",
            node.position,
        )
        return []

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

    def visit_while_expr(self, node: nodes.WhileExpr) -> Type:
        condition = node.condition.accept(self) or UNKNOWN
        self.expect(BOOL, condition, node.condition, "while condition must be Bool")
        self._loop_depth += 1
        try:
            node.body.accept(self)
        finally:
            self._loop_depth -= 1
        return self._record(node, UNIT)

    def visit_for_expr(self, node: nodes.ForExpr) -> Type:
        iterable_type = node.iterator.accept(self) or UNKNOWN
        element_type = self._iterable_element_type(iterable_type, node.iterator)
        if len(node.vars) != 1:
            self._unsupported(node, "Multiple loop variables are not supported in oort-core yet.")
            return self._record(node, UNIT)

        loop_var = node.vars[0]
        self.scopes.append({})
        self._loop_depth += 1
        try:
            variable_type = element_type
            if loop_var.type_expr is not None:
                annotation = self.resolve_annotation(loop_var.type_expr, allow_unit=False)
                self.expect(annotation, element_type, loop_var)
                variable_type = annotation
            self.declare(
                loop_var.name,
                variable_type,
                mutable=False,
                position=loop_var.position,
            )
            loop_var.metadata["type"] = describe_type(variable_type)
            node.body.accept(self)
        finally:
            self._loop_depth -= 1
            self.scopes.pop()
        return self._record(node, UNIT)

    def _iterable_element_type(self, type_: Type, node: nodes.ASTNode) -> Type:
        if isinstance(type_, UnknownType):
            return UNKNOWN
        if isinstance(type_, (ListType, SetType)):
            return type_.element
        if isinstance(type_, DictType):
            return type_.key
        if type_ == STRING:
            return STRING
        if isinstance(type_, TupleType):
            if not type_.elements:
                return UNKNOWN
            first = type_.elements[0]
            if all(element == first for element in type_.elements):
                return first
            self._error(
                "Cannot iterate a Tuple with heterogeneous element types in "
                "oort-core yet; index it or use a List.",
                node.position,
            )
            return UNKNOWN
        self._error(
            f"Cannot iterate over values of type {describe_type(type_)} in oort-core.",
            node.position,
        )
        return UNKNOWN

    def visit_continue_expr(self, node: nodes.ContinueExpr) -> Type:
        if self._loop_depth == 0:
            self._error("continue is only allowed inside a loop.", node.position)
        return self._record(node, NEVER)

    def visit_break_expr(self, node: nodes.BreakExpr) -> Type:
        if self._loop_depth == 0:
            self._error("break is only allowed inside a loop.", node.position)
        if node.value is not None:
            self._unsupported(node, "break values are not supported in oort-core yet.")
        return self._record(node, NEVER)

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
        if isinstance(value_type, ClassType):
            slot = value_type.slot(node.attribute)
            if slot is not None:
                return self._record(node, slot.slot_type)
            method = value_type.method(node.attribute)
            if method is not None:
                return self._record(node, method)
            self._error(
                f"Class '{value_type.name}' has no member '{node.attribute}'.",
                node.position,
            )
            return self._record(node, UNKNOWN)
        return self._unsupported(
            node,
            "Attribute access is only supported on imported modules and "
            "static class members in oort-core yet.",
        )

    def visit_subscript(self, node: nodes.Subscript) -> Type:
        if isinstance(node.index, nodes.SliceLiteral):
            return self._unsupported(node, "Slices are not supported in oort-core yet.")

        value_type = node.value.accept(self)
        if isinstance(value_type, UnknownType):
            node.index.accept(self)
            return self._record(node, UNKNOWN)
        if isinstance(value_type, ListType):
            self._check_expr(node.index, INT)
            return self._record(node, value_type.element)
        if isinstance(value_type, DictType):
            self._check_expr(node.index, value_type.key)
            return self._record(node, value_type.value)
        if value_type == STRING:
            self._check_expr(node.index, INT)
            return self._record(node, STRING)
        if isinstance(value_type, TupleType):
            return self._check_tuple_subscript(node, value_type)
        self._error(
            f"Type {describe_type(value_type)} is not subscriptable in oort-core.",
            node.position,
        )
        node.index.accept(self)
        return self._record(node, UNKNOWN)

    def _check_tuple_subscript(self, node: nodes.Subscript, tuple_type: TupleType) -> Type:
        index_type = node.index.accept(self) or UNKNOWN
        self.expect(INT, index_type, node.index)
        if isinstance(node.index, nodes.IntConstant):
            index = node.index.value
            assert isinstance(index, int)
            if not -len(tuple_type.elements) <= index < len(tuple_type.elements):
                self._error(
                    f"Index {index} is out of range for {describe_type(tuple_type)}.",
                    node.index.position,
                )
                return self._record(node, UNKNOWN)
            return self._record(node, tuple_type.elements[index])
        if not tuple_type.elements:
            self._error("Cannot index an empty Tuple in oort-core.", node.position)
            return self._record(node, UNKNOWN)
        first = tuple_type.elements[0]
        if all(element == first for element in tuple_type.elements):
            return self._record(node, first)
        self._error(
            "Tuple subscripts with a non-literal index require all elements to "
            "have the same type in oort-core.",
            node.position,
        )
        return self._record(node, UNKNOWN)

    def visit_slice_literal(self, node: nodes.SliceLiteral) -> Type:
        return self._unsupported(node, "Slices are not supported in oort-core yet.")

    def visit_list_literal(self, node: nodes.ListLiteral) -> Type:
        return self._check_collection_literal(node, UNKNOWN)

    def visit_tuple_literal(self, node: nodes.TupleLiteral) -> Type:
        return self._check_collection_literal(node, UNKNOWN)

    def visit_dict_literal(self, node: nodes.DictLiteral) -> Type:
        return self._check_collection_literal(node, UNKNOWN)

    def visit_set_literal(self, node: nodes.SetLiteral) -> Type:
        return self._check_collection_literal(node, UNKNOWN)

    # -- collection literal checking -----------------------------------

    def _check_collection_literal(self, node: nodes.ASTNode, expected: Type) -> Type:
        if isinstance(node, nodes.ListLiteral):
            return self._check_list_literal(node, expected)
        if isinstance(node, nodes.TupleLiteral):
            return self._check_tuple_literal(node, expected)
        if isinstance(node, nodes.DictLiteral):
            return self._check_dict_literal(node, expected)
        assert isinstance(node, nodes.SetLiteral)
        return self._check_set_literal(node, expected)

    def _check_list_literal(self, node: nodes.ListLiteral, expected: Type) -> Type:
        if isinstance(expected, ListType):
            for element in node.elements:
                self._check_expr(element, expected.element)
            return self._record(node, expected)
        if not node.elements:
            self._error(
                "Cannot infer the element type of an empty List; add a type annotation.",
                node.position,
            )
            actual = ListType(UNKNOWN)
        else:
            actual = ListType(self._infer_homogeneous(node.elements, "List"))
        return self._finish_literal(node, expected, actual)

    def _check_set_literal(self, node: nodes.SetLiteral, expected: Type) -> Type:
        if isinstance(expected, SetType):
            for element in node.elements:
                self._check_expr(element, expected.element)
            return self._record(node, expected)
        if not node.elements:
            self._error(
                "Cannot infer the element type of an empty Set; add a type annotation.",
                node.position,
            )
            actual = SetType(UNKNOWN)
        else:
            actual = SetType(self._infer_homogeneous(node.elements, "Set", key_elements=True))
        return self._finish_literal(node, expected, actual)

    def _check_tuple_literal(self, node: nodes.TupleLiteral, expected: Type) -> Type:
        if isinstance(expected, TupleType):
            if len(node.elements) != len(expected.elements):
                self._error(
                    f"Tuple has {len(node.elements)} elements, expected {len(expected.elements)}.",
                    node.position,
                )
                for element in node.elements:
                    element.accept(self)
                return self._record(node, expected)
            for element, element_type in zip(node.elements, expected.elements):
                self._check_expr(element, element_type)
            return self._record(node, expected)

        element_types: list[Type] = []
        for element in node.elements:
            element_type = element.accept(self) or UNKNOWN
            element_types.append(self._validate_value_type(element_type, "Tuple", element.position))
        actual = TupleType(tuple(element_types))
        return self._finish_literal(node, expected, actual)

    def _check_dict_literal(self, node: nodes.DictLiteral, expected: Type) -> Type:
        if isinstance(expected, DictType):
            for key, value in node.items:
                if key is None:
                    self._unsupported(node, "Dict unpacking is not supported in oort-core yet.")
                    continue
                self._check_expr(key, expected.key)
                self._check_expr(value, expected.value)
            return self._record(node, expected)

        if not node.items:
            self._error(
                "Cannot infer the key/value types of an empty Dict; add a type annotation.",
                node.position,
            )
            actual = DictType(UNKNOWN, UNKNOWN)
        else:
            key_types: list[nodes.ASTNode] = []
            value_types: list[nodes.ASTNode] = []
            for key, value in node.items:
                if key is None:
                    self._unsupported(node, "Dict unpacking is not supported in oort-core yet.")
                    continue
                key_types.append(key)
                value_types.append(value)
            if not key_types:
                actual = DictType(UNKNOWN, UNKNOWN)
            else:
                key_type = self._infer_homogeneous(
                    key_types, "Dict", key_elements=True, label="Dict keys"
                )
                value_type = self._infer_homogeneous(value_types, "Dict", label="Dict values")
                actual = DictType(key_type, value_type)
        return self._finish_literal(node, expected, actual)

    def _finish_literal(self, node: nodes.ASTNode, expected: Type, actual: Type) -> Type:
        if isinstance(expected, UnknownType):
            return self._record(node, actual)
        self.expect(expected, actual, node)
        return self._record(node, expected)

    def _infer_homogeneous(
        self,
        elements: Iterable[nodes.ASTNode],
        kind: str,
        *,
        key_elements: bool = False,
        label: str | None = None,
    ) -> Type:
        label = label or f"{kind} elements"
        result: Type = UNKNOWN
        started = False
        for element in elements:
            element_type = element.accept(self) or UNKNOWN
            if key_elements:
                element_type = self._validate_key_type(element_type, kind, label, element.position)
            else:
                element_type = self._validate_value_type(element_type, kind, element.position)
            if not started:
                result = element_type
                started = True
                continue
            joined = join_types(result, element_type)
            if joined is None:
                self._error(
                    f"{label} have incompatible types: "
                    f"{describe_type(result)} and {describe_type(element_type)}.",
                    element.position,
                )
                result = UNKNOWN
            else:
                result = joined
        return result

    def _validate_value_type(self, type_: Type, kind: str, position) -> Type:
        if isinstance(type_, NeverType):
            return UNKNOWN
        if type_ == UNIT:
            self._error(f"Unit cannot be stored in a {kind} in oort-core.", position)
            return UNKNOWN
        if isinstance(type_, ModuleType):
            self._error(f"Modules cannot be stored in a {kind} in oort-core.", position)
            return UNKNOWN
        return type_

    def _validate_key_type(self, type_: Type, container: str, label: str, position) -> Type:
        type_ = self._validate_value_type(type_, container, position)
        if isinstance(type_, UnknownType) or _is_valid_key_type(type_):
            return type_
        self._error(
            f"{label} must be Int, Float, Bool, String, an enum or a Tuple "
            f"of key types, got {describe_type(type_)}.",
            position,
        )
        return UNKNOWN

    def _resolve_container_type(self, node: nodes.Subscript) -> Type:
        base = node.value
        if not isinstance(base, nodes.Name) or base.id not in {"List", "Set", "Dict", "Tuple"}:
            self._error(
                "Generic type applications are only supported for List, Set, Dict and Tuple.",
                node.position,
            )
            return UNKNOWN

        if isinstance(node.index, nodes.TupleLiteral):
            arguments = node.index.elements
        else:
            arguments = [node.index]

        name = base.id
        expected_count = {"List": 1, "Set": 1, "Dict": 2}.get(name)
        if expected_count is not None and len(arguments) != expected_count:
            self._error(
                f"Type '{name}' expects {expected_count} type argument(s), got {len(arguments)}.",
                node.position,
            )
            return UNKNOWN
        if name == "Tuple" and not arguments:
            self._error("Tuple requires at least one element type.", node.position)
            return UNKNOWN

        resolved = [self.resolve_annotation(argument, allow_unit=False) for argument in arguments]
        if name == "List":
            return ListType(resolved[0])
        if name == "Set":
            if not _is_valid_key_type(resolved[0]):
                self._error(
                    "Set elements must be Int, Float, Bool, String, an enum or a "
                    f"Tuple of key types, got {describe_type(resolved[0])}.",
                    node.position,
                )
                return SetType(UNKNOWN)
            return SetType(resolved[0])
        if name == "Dict":
            if not _is_valid_key_type(resolved[0]):
                self._error(
                    "Dict keys must be Int, Float, Bool, String, an enum or a "
                    f"Tuple of key types, got {describe_type(resolved[0])}.",
                    node.position,
                )
                return DictType(UNKNOWN, resolved[1])
            return DictType(resolved[0], resolved[1])
        return TupleType(tuple(resolved))

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
