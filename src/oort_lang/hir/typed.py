#! /usr/bin/env python

"""Typed HIR for the restricted ``oort-core`` scalar subset (design 15, M1).

The typed path is deliberately parallel to the erased HIR path: it reuses the
existing instruction classes and register conventions, attaches one static
``IrType`` per register, and accepts only the scalar subset defined in
``docs/design/15-typed-ir.md``. Anything outside the subset is rejected
explicitly; the erased path is never changed.
"""

from __future__ import annotations

import dataclasses
from enum import Enum
from typing import TYPE_CHECKING, NoReturn

from ..ast import nodes
from ..diagnostics.syntax_errors import UnsupportedSyntax
from ..semantics.core.prelude import CORE_PRELUDE_ORIGIN
from ..semantics.core.types import (
    AdtType as CoreAdtType,
)
from ..semantics.core.types import (
    DictType,
    FunctionType,
    ListType,
    NeverType,
    PrimitiveType,
    SetType,
    TupleType,
    Type,
    UnknownType,
    describe_type,
    substitute,
)
from .dump import format_instruction
from .lower import HirLowerer
from .nodes import (
    AdtField,
    AdtTag,
    BinOp,
    BuildAdt,
    BuildDict,
    BuildList,
    BuildSet,
    BuildTuple,
    Call,
    DefineFunction,
    FreshLocals,
    GetItem,
    HirFunction,
    Instruction,
    IteratorNext,
    Jump,
    JumpIfFalse,
    JumpIfTrue,
    Label,
    LoadConst,
    LoadGlobal,
    LoadLocal,
    Move,
    OpenIterator,
    Return,
    SetItem,
    StoreGlobal,
    StoreLocal,
    TupleItem,
    UnOp,
    register_reads,
    register_writes,
)

if TYPE_CHECKING:
    from collections.abc import Iterable


class IrType(Enum):
    """Static types carried by typed HIR (v0: scalars plus opaque functions)."""

    INT = "Int"
    FLOAT = "Float"
    BOOL = "Bool"
    UNIT = "Unit"
    STRING = "String"
    ITERATOR = "<iterator>"
    FUNCTION = "<function>"

    def __str__(self) -> str:
        return self.value


_PRIMITIVE_IR = {
    "Int": IrType.INT,
    "Float": IrType.FLOAT,
    "Bool": IrType.BOOL,
    "Unit": IrType.UNIT,
    "String": IrType.STRING,
}


@dataclasses.dataclass(frozen=True, slots=True)
class ContainerType:
    """A container type with recursive element/key/value types."""

    kind: str
    args: tuple[IrTypeLike, ...] = ()

    def __str__(self) -> str:
        if self.kind == "Tuple":
            return "Tuple[" + ", ".join(str(arg) for arg in self.args) + "]"
        return f"{self.kind}[{', '.join(str(arg) for arg in self.args)}]"


@dataclasses.dataclass(frozen=True, slots=True)
class AdtType:
    """A nominal monomorphic ADT type (generic args arrive in S4b)."""

    origin: str
    name: str
    args: tuple[IrTypeLike, ...] = ()

    def __str__(self) -> str:
        if not self.args:
            return self.name
        return f"{self.name}[{', '.join(str(arg) for arg in self.args)}]"


IrTypeLike = IrType | ContainerType | AdtType


@dataclasses.dataclass(frozen=True, slots=True)
class AdtConstructor:
    name: str
    payload: tuple[IrTypeLike, ...] = ()
    arity: int = 0

    def __post_init__(self) -> None:
        if not self.arity:
            object.__setattr__(self, "arity", len(self.payload))


@dataclasses.dataclass(frozen=True, slots=True)
class AdtDecl:
    """One module-level enum declaration and its constructors."""

    origin: str
    name: str
    constructors: tuple[AdtConstructor, ...]


class ConstructorSite:
    """Where a constructor lives in the module ADT table."""

    __slots__ = ("arity", "constructor_id", "ctor_index", "decl_index", "payload")

    def __init__(
        self,
        constructor_id: int,
        decl_index: int,
        ctor_index: int,
        payload: tuple[IrTypeLike, ...],
        arity: int,
    ):
        self.constructor_id = constructor_id
        self.decl_index = decl_index
        self.ctor_index = ctor_index
        self.payload = payload
        self.arity = arity


def list_type(element: IrTypeLike) -> ContainerType:
    return ContainerType("List", (element,))


def tuple_type(*elements: IrTypeLike) -> ContainerType:
    return ContainerType("Tuple", tuple(elements))


_TYPE_TAGS = {
    IrType.INT: 1,
    IrType.FLOAT: 2,
    IrType.BOOL: 3,
    IrType.UNIT: 4,
    IrType.FUNCTION: 5,
    IrType.STRING: 6,
    IrType.ITERATOR: 11,
}
_CONTAINER_TAGS = {"List": 7, "Set": 8, "Dict": 9, "Tuple": 10}


def ir_type_tag(ir_type: IrTypeLike) -> int:
    """Wire tag for a type-table descriptor (spec 14)."""

    if isinstance(ir_type, ContainerType):
        return _CONTAINER_TAGS[ir_type.kind]
    if isinstance(ir_type, AdtType):
        return 12
    return _TYPE_TAGS[ir_type]


_ARITHMETIC_OPS = {"+", "-", "*", "//", "%"}
_COMPARISON_OPS = {"<", "<=", ">", ">="}
_EQUALITY_OPS = {"==", "!="}
_ALLOWED_BINARY_OPS = _ARITHMETIC_OPS | {"/"} | _COMPARISON_OPS | _EQUALITY_OPS
_ALLOWED_UNARY_OPS = {"+", "-", "not"}


@dataclasses.dataclass(frozen=True, slots=True)
class TypedFunction:
    """One HIR function plus its static signature and register types."""

    hir: HirFunction
    param_types: tuple[IrTypeLike, ...]
    ret_type: IrTypeLike
    register_types: tuple[IrTypeLike | None, ...]


@dataclasses.dataclass(frozen=True, slots=True)
class TypedModule:
    main: TypedFunction
    functions: tuple[TypedFunction, ...]
    adt_decls: tuple[AdtDecl, ...] = ()


def _reject(node: nodes.ASTNode, detail: str) -> NoReturn:
    raise UnsupportedSyntax(f"Typed HIR backend does not support {detail}.", node.position)


def _ir_type_from(type_: Type, position, *, allow_function: bool = False) -> IrTypeLike:
    if isinstance(type_, PrimitiveType):
        ir_type = _PRIMITIVE_IR.get(type_.name)
        if ir_type is None:
            raise UnsupportedSyntax(
                f"Typed HIR backend does not support primitive type {type_.name}.",
                position,
            )
        return ir_type
    if isinstance(type_, ListType):
        return list_type(_ir_type_from(type_.element, position))
    if isinstance(type_, SetType):
        return ContainerType("Set", (_ir_type_from(type_.element, position),))
    if isinstance(type_, DictType):
        return ContainerType(
            "Dict",
            (
                _ir_type_from(type_.key, position),
                _ir_type_from(type_.value, position),
            ),
        )
    if isinstance(type_, TupleType):
        return tuple_type(*(_ir_type_from(element, position) for element in type_.elements))
    if isinstance(type_, CoreAdtType):
        origin = CORE_PRELUDE_ORIGIN if type_.origin == CORE_PRELUDE_ORIGIN else "<typed-module>"
        return AdtType(
            origin,
            type_.name,
            tuple(_ir_type_from(argument, position) for argument in type_.args),
        )
    if isinstance(type_, FunctionType) and allow_function:
        return IrType.FUNCTION
    if isinstance(type_, FunctionType):
        raise UnsupportedSyntax(
            "Typed HIR backend does not support first-class function values.",
            position,
        )
    if isinstance(type_, (UnknownType, NeverType)):
        raise UnsupportedSyntax(
            f"Typed HIR backend cannot carry type {describe_type(type_)}.",
            position,
        )
    raise UnsupportedSyntax(
        f"Typed HIR backend does not support type {describe_type(type_)}.",
        position,
    )


def _ir_type_for_node(node: nodes.ASTNode, *, allow_function: bool = False) -> IrTypeLike:
    type_ = node.metadata.get("type_obj")
    if not isinstance(type_, Type):
        raise UnsupportedSyntax(
            f"Typed HIR backend is missing type metadata for {type(node).__name__}.",
            node.position,
        )
    return _ir_type_from(type_, node.position, allow_function=allow_function)


# ---------------------------------------------------------------------------
# Subset validation (the typed path only accepts this slice)
# ---------------------------------------------------------------------------


def _validate_module(module: nodes.ModuleNode) -> None:
    for stmt in module.body.statements:
        if getattr(stmt, "synthetic", False):
            # Compiler-injected nodes (for example the core prelude enums) are
            # not part of the user program.
            continue
        if isinstance(stmt, nodes.FunctionDef):
            _validate_function(stmt)
            continue
        if isinstance(stmt, nodes.EnumDef):
            _validate_enum(stmt)
            continue
        if isinstance(stmt, (nodes.VarDecl, nodes.Assignment)):
            _reject(stmt, "top-level declarations or assignments (move them into a function)")
        if isinstance(stmt, (nodes.ImportStmt, nodes.ImportFromStmt)):
            _reject(stmt, "module imports")
        if isinstance(stmt, (nodes.ClassDef, nodes.InterfaceDef)):
            _reject(stmt, f"{type(stmt).__name__.removesuffix('Def')} definitions")
        _validate_expr(stmt)


def _validate_enum(node: nodes.EnumDef) -> None:
    enum_type = node.metadata.get("type_obj")
    if not isinstance(enum_type, CoreAdtType):
        _reject(node, "enum without a checked type")
    if node.type_params:
        return
    _ir_type_from(enum_type, node.position)


def _validate_function(node: nodes.FunctionDef) -> None:
    if node.is_lambda:
        _reject(node, "lambdas")
    if node.is_extension:
        _reject(node, "extension methods")
    if node.is_class_method:
        _reject(node, "class methods")
    if node.type_params:
        _reject(node, "generic functions")
    if node.operator_symbol is not None:
        _reject(node, "operator definitions")
    signature = node.metadata.get("type_obj")
    if not isinstance(signature, FunctionType):
        _reject(node, "function without a checked signature")
    for param_type in signature.params:
        _ir_type_from(param_type, node.position)
    _ir_type_from(signature.ret, node.position)
    _validate_statements(node.body.statements)


def _validate_statements(statements: Iterable[nodes.ASTNode]) -> None:
    for stmt in statements:
        if getattr(stmt, "synthetic", False):
            continue
        if isinstance(stmt, nodes.VarDecl):
            _validate_var_decl(stmt)
        elif isinstance(stmt, nodes.Assignment):
            _validate_assignment(stmt)
        elif isinstance(stmt, nodes.ReturnExpr):
            if stmt.value is not None:
                _validate_expr(stmt.value)
        elif isinstance(stmt, nodes.FunctionDef):
            _reject(stmt, "nested function definitions")
        elif isinstance(
            stmt,
            (
                nodes.ClassDef,
                nodes.EnumDef,
                nodes.InterfaceDef,
                nodes.ImportStmt,
                nodes.ImportFromStmt,
                nodes.BreakExpr,
                nodes.ContinueExpr,
            ),
        ):
            _reject(stmt, type(stmt).__name__)
        else:
            _validate_expr(stmt)


def _validate_var_decl(node: nodes.VarDecl) -> None:
    if len(node.decl_targets) != 1:
        _reject(node, "multi-target declarations")
    if node.init_value is None:
        _reject(node, "declarations without an initializer")
    target_type = node.decl_targets[0].metadata.get("type_obj")
    if not isinstance(target_type, Type):
        _reject(node, "variables without a type")
    if _ir_type_from(target_type, node.position) is IrType.UNIT:
        _reject(node, "Unit variables")
    _validate_expr(node.init_value)


def _validate_assignment(node: nodes.Assignment) -> None:
    if node.op.text != "=":
        _reject(node, f"augmented assignment {node.op.text!r}")
    if isinstance(node.lhs, nodes.Subscript):
        container_type = _ir_type_for_node(node.lhs.value)
        if not isinstance(container_type, ContainerType) or container_type.kind != "List":
            _reject(node, "only List element assignment is supported")
        _validate_expr(node.lhs.value)
        _validate_expr(node.lhs.index)
        _validate_expr(node.rhs)
        return
    if not isinstance(node.lhs, nodes.Name):
        _reject(node, "assignment targets other than plain names or List elements")
    lhs_type = node.lhs.metadata.get("type_obj")
    if not isinstance(lhs_type, Type):
        _reject(node, "assignments without a type")
    _ir_type_from(lhs_type, node.position)
    _validate_expr(node.rhs)


def _validate_block(node: nodes.BlockExpr) -> None:
    _validate_statements(node.statements)
    type_ = node.metadata.get("type_obj")
    if isinstance(type_, NeverType):
        # A block that always returns/breaks has no value to type.
        return
    _ir_type_for_node(node)


def _validate_pattern(pattern: nodes.Pattern, expected: Type) -> None:
    if isinstance(pattern, nodes.WildcardPattern):
        return
    if isinstance(pattern, nodes.NamePattern):
        if isinstance(expected, CoreAdtType):
            constructor = expected.constructor(pattern.name)
            if constructor is not None:
                if constructor.payload:
                    _reject(pattern, f"constructor '{constructor.name}' requires arguments")
                return
        _ir_type_from(expected, pattern.position)
        return
    if isinstance(pattern, nodes.LiteralPattern):
        if not isinstance(expected, PrimitiveType) or expected.name not in (
            "Int",
            "Float",
            "Bool",
            "String",
        ):
            _reject(pattern, "literal pattern on unsupported type")
        _ir_type_from(expected, pattern.position)
        return
    if isinstance(pattern, nodes.TuplePattern):
        if not isinstance(expected, TupleType):
            _reject(pattern, "tuple pattern on non-Tuple values")
        if len(pattern.patterns) != len(expected.elements):
            _reject(pattern, "tuple pattern arity mismatch")
        for item, item_type in zip(pattern.patterns, expected.elements, strict=True):
            _validate_pattern(item, item_type)
        return
    if isinstance(pattern, nodes.OrPattern):
        for alternative in pattern.patterns:
            _validate_pattern(alternative, expected)
        return
    if isinstance(pattern, nodes.ConstructorPattern):
        if not isinstance(expected, CoreAdtType):
            _reject(pattern, "constructor patterns on non-ADT values")
        constructor = expected.constructor(pattern.name)
        if constructor is None:
            _reject(pattern, f"unknown constructor '{pattern.name}'")
        if len(pattern.args) != len(constructor.payload):
            _reject(pattern, f"constructor '{pattern.name}' arity mismatch")
        for argument, payload_type in zip(
            pattern.args, _instantiated_payload(expected, constructor), strict=True
        ):
            _validate_pattern(argument, payload_type)
        return
    _reject(pattern, f"pattern {type(pattern).__name__}")


def _validate_expr(node: nodes.ASTNode, *, as_callee: bool = False) -> None:
    if isinstance(
        node, (nodes.IntConstant, nodes.FloatConstant, nodes.BooleanConstant, nodes.StringConstant)
    ):
        _ir_type_for_node(node)
        return
    if isinstance(node, nodes.Name):
        ir_type = _ir_type_for_node(node, allow_function=as_callee)
        if ir_type is IrType.FUNCTION and not as_callee:
            _reject(node, "first-class function values")
        return
    if isinstance(node, nodes.UnaryExpr):
        if node.op.text not in _ALLOWED_UNARY_OPS:
            _reject(node, f"unary operator {node.op.text!r}")
        _validate_expr(node.operand)
        _ir_type_for_node(node)
        return
    if isinstance(node, (nodes.AndExpr, nodes.OrExpr)):
        _validate_expr(node.lhs)
        _validate_expr(node.rhs)
        _ir_type_for_node(node)
        return
    if isinstance(node, nodes.BinaryExpr):
        if node.op.text not in _ALLOWED_BINARY_OPS:
            _reject(node, f"binary operator {node.op.text!r}")
        _validate_expr(node.lhs)
        _validate_expr(node.rhs)
        _ir_type_for_node(node)
        return
    if isinstance(node, (nodes.AndExpr, nodes.OrExpr)):
        _validate_expr(node.lhs)
        _validate_expr(node.rhs)
        _ir_type_for_node(node)
        return
    if isinstance(node, nodes.Call):
        if node.infix:
            _reject(node, "infix calls")
        if not isinstance(node.func, nodes.Name):
            _reject(node, "calls to values other than plain function names")
        callee_type = _ir_type_for_node(node.func, allow_function=True)
        if callee_type is not IrType.FUNCTION:
            _reject(node.func, "calls to non-function names")
        for arg in node.args:
            if arg.kind != nodes.ArgumentKind.DEFAULT or arg.keyword is not None:
                _reject(arg, "keyword, variadic or block arguments")
            _validate_expr(arg.value)
        ir_type = _ir_type_for_node(node)
        if ir_type is IrType.FUNCTION:
            _reject(node, "calls returning first-class functions")
        return
    if isinstance(node, nodes.IfExpr):
        _validate_expr(node.condition)
        _validate_block(node.if_block)
        if node.else_block is not None:
            _validate_block(node.else_block)
        if not isinstance(node.metadata.get("type_obj"), NeverType):
            _ir_type_for_node(node)
        return
    if isinstance(node, nodes.BlockExpr):
        _validate_block(node)
        return
    if isinstance(node, nodes.WhileExpr):
        _validate_expr(node.condition)
        _validate_block(node.body)
        _ir_type_for_node(node)
        return
    if isinstance(node, (nodes.ListLiteral, nodes.TupleLiteral, nodes.SetLiteral)):
        for element in node.elements:
            _validate_expr(element)
        _ir_type_for_node(node)
        return
    if isinstance(node, nodes.DictLiteral):
        for key, value in node.items:
            if key is None:
                _reject(node, "Dict unpacking")
            _validate_expr(key)
            _validate_expr(value)
        _ir_type_for_node(node)
        return
    if isinstance(node, nodes.Subscript):
        _validate_expr(node.value)
        _validate_expr(node.index)
        _ir_type_for_node(node)
        return
    if isinstance(node, nodes.MatchExpr):
        scrutinee = node.scrutinee.metadata.get("type_obj")
        if not isinstance(scrutinee, (CoreAdtType, TupleType, PrimitiveType)):
            _reject(node, "match on unsupported values")
        if isinstance(scrutinee, PrimitiveType) and scrutinee.name not in (
            "Int",
            "Float",
            "Bool",
            "String",
        ):
            _reject(node, "match on unsupported scalar values")
        _validate_expr(node.scrutinee)
        for arm in node.arms:
            _validate_pattern(arm.pattern, scrutinee)
            if arm.guard is not None:
                _validate_expr(arm.guard)
            _validate_expr(arm.body)
        _ir_type_for_node(node)
        return
    if isinstance(node, nodes.ForExpr):
        if len(node.vars) != 1:
            _reject(node, "for loops with multiple variables")
        iterable_type = _ir_type_for_node(node.iterator)
        _iterated_element_type(iterable_type, node)
        _validate_expr(node.iterator)
        _validate_block(node.body)
        _ir_type_for_node(node)
        return
    _reject(node, type(node).__name__)


# ---------------------------------------------------------------------------
# Typed lowering: reuse the shared lowerer and record register types
# ---------------------------------------------------------------------------


def _instantiated_payload(expected: CoreAdtType, constructor) -> tuple[Type, ...]:
    mapping = {
        parameter.name: argument
        for parameter, argument in zip(expected.template.params, expected.args)
    }
    return tuple(substitute(payload, mapping) for payload in constructor.payload)


def _constructor_payload(
    enum_type: CoreAdtType, constructor: nodes.EnumConstructor
) -> tuple[IrTypeLike, ...]:
    info = enum_type.constructor(constructor.name)
    if info is None:
        raise UnsupportedSyntax(
            f"Enum is missing constructor '{constructor.name}'.", constructor.position
        )
    return tuple(_ir_type_from(payload_type, constructor.position) for payload_type in info.payload)


def _collect_adt_decls(
    module: nodes.ModuleNode,
) -> tuple[tuple[AdtDecl, ...], dict[str, ConstructorSite]]:
    decls: list[AdtDecl] = []
    sites: dict[str, ConstructorSite] = {}
    next_constructor = 0
    for stmt in module.body.statements:
        if not isinstance(stmt, nodes.EnumDef):
            continue
        origin = stmt.declaration_origin or "<typed-module>"
        enum_type = stmt.metadata.get("type_obj")
        if not isinstance(enum_type, CoreAdtType):
            raise UnsupportedSyntax("Enum is missing a checked type.", stmt.position)
        if stmt.type_params:
            # Generic payload types depend on the instantiation. S4b erases
            # runtime type arguments; constructors keep arity here.
            constructors = tuple(
                AdtConstructor(ctor.name, arity=len(ctor.fields)) for ctor in stmt.constructors
            )
        else:
            constructors = tuple(
                AdtConstructor(
                    ctor.name,
                    _constructor_payload(enum_type, ctor),
                )
                for ctor in stmt.constructors
            )
        decls.append(AdtDecl(origin, stmt.name, constructors))
        decl_index = len(decls) - 1
        for ctor_index, constructor in enumerate(constructors):
            sites[constructor.name] = ConstructorSite(
                next_constructor,
                decl_index,
                ctor_index,
                constructor.payload,
                constructor.arity,
            )
            next_constructor += 1
    return tuple(decls), sites


class _TypedHirLowerer(HirLowerer):
    def __init__(
        self,
        adt_decls: tuple[AdtDecl, ...] = (),
        constructors: dict[str, ConstructorSite] | None = None,
    ) -> None:
        super().__init__()
        self.register_types: dict[str, dict[int, IrTypeLike]] = {}
        self.function_types: dict[str, FunctionType] = {}
        self.adt_decls = adt_decls
        self.constructors = constructors or {}
        self._current_ret: IrTypeLike = IrType.UNIT

    def _record(self, register: int, ir_type: IrTypeLike, position) -> None:
        table = self.register_types.setdefault(self.state.name, {})
        existing = table.get(register)
        # A register may first be written by the Unit placeholder used to
        # initialise if-expression results; the enclosing expression then
        # provides the real type.
        if existing is not None and existing not in (ir_type, IrType.UNIT):
            raise UnsupportedSyntax(
                f"Typed HIR register R{register} has conflicting types {existing} and {ir_type}.",
                position,
            )
        table[register] = ir_type

    def _lower_enum_def(self, node: nodes.EnumDef) -> None:
        # Enum declarations live in the module ADT table, not in main.
        return

    def _lower_expr(self, node: nodes.ASTNode | None) -> int | None:
        if isinstance(node, nodes.Call) and isinstance(node.func, nodes.Name):
            site = self.constructors.get(node.func.id)
            binding = node.func.binding
            if site is not None and (binding is None or binding.is_global):
                arguments = tuple(self._require_value(arg.value) for arg in node.args)
                if len(arguments) != site.arity:
                    raise UnsupportedSyntax(
                        f"Constructor '{node.func.id}' expects {site.arity} argument(s), "
                        f"got {len(arguments)}.",
                        node.position,
                    )
                dst = self._alloc(node.position)
                self._emit(BuildAdt(node.position, dst, site.constructor_id, arguments))
                self._record(dst, _ir_type_for_node(node), node.position)
                return dst
        if isinstance(node, nodes.Name):
            site = self.constructors.get(node.id)
            binding = node.binding
            if site is not None and (binding is None or binding.is_global):
                if site.arity != 0:
                    raise UnsupportedSyntax(
                        f"Constructor '{node.id}' requires {site.arity} argument(s).",
                        node.position,
                    )
                dst = self._alloc(node.position)
                self._emit(BuildAdt(node.position, dst, site.constructor_id, ()))
                self._record(dst, _ir_type_for_node(node), node.position)
                return dst
        register = super()._lower_expr(node)
        if register is not None and node is not None:
            type_ = node.metadata.get("type_obj")
            if isinstance(type_, NeverType):
                ir_type = self._current_ret
            else:
                ir_type = _ir_type_for_node(node, allow_function=True)
            self._record(register, ir_type, node.position)
        return register

    def _lower_match(self, node: nodes.MatchExpr) -> int:
        scrutinee = self._require_value(node.scrutinee)
        scrutinee_type = node.scrutinee.metadata.get("type_obj")
        if not isinstance(scrutinee_type, Type):
            raise UnsupportedSyntax("Typed match is missing the scrutinee type.", node.position)
        result_type = _ir_type_for_node(node)
        dst = self._alloc(node.position)
        self._record(dst, result_type, node.position)
        end_label = self._new_label("match_end")
        arm_labels = [self._new_label("match_arm") for _ in node.arms]
        arm_labels.append(end_label)

        for index, (arm, arm_label) in enumerate(zip(node.arms, arm_labels)):
            fail_label = arm_labels[index + 1]
            self._emit(Label(arm.position, arm_label))
            self._push_scope()
            try:
                self._lower_pattern(arm.pattern, scrutinee, scrutinee_type, fail_label)
                if arm.guard is not None:
                    guard = self._require_value(arm.guard)
                    self._emit(JumpIfFalse(arm.guard.position, guard, fail_label))
                body = self._require_value(arm.body)
                self._emit(Move(arm.body.position, dst, body))
                self._emit(Jump(arm.body.position, end_label))
            finally:
                self._pop_scope()

        self._emit(Label(node.position, end_label))
        return dst

    def _emit_tag_test(
        self,
        value: int,
        constructor_index: int,
        fail_label: str,
        position,
    ) -> None:
        tag = self._alloc(position)
        self._record(tag, IrType.INT, position)
        self._emit(AdtTag(position, tag, value))
        expected = self._const(constructor_index, position)
        self._record(expected, IrType.INT, position)
        ok = self._alloc(position)
        self._record(ok, IrType.BOOL, position)
        self._emit(BinOp(position, ok, "==", tag, expected))
        self._emit(JumpIfFalse(position, ok, fail_label))

    def _binding_types(self, pattern: nodes.Pattern, expected: Type) -> list[tuple[str, Type]]:
        if isinstance(pattern, nodes.NamePattern):
            if isinstance(expected, CoreAdtType):
                constructor = expected.constructor(pattern.name)
                if constructor is not None:
                    return []
            return [(pattern.name, expected)]
        if isinstance(pattern, nodes.ConstructorPattern):
            if not isinstance(expected, CoreAdtType):
                return []
            constructor = expected.constructor(pattern.name)
            if constructor is None:
                return []
            payload = _instantiated_payload(expected, constructor)
            return [
                binding
                for argument, payload_type in zip(pattern.args, payload, strict=True)
                for binding in self._binding_types(argument, payload_type)
            ]
        if isinstance(pattern, nodes.TuplePattern):
            if not isinstance(expected, TupleType):
                return []
            return [
                binding
                for item, item_type in zip(pattern.patterns, expected.elements, strict=True)
                for binding in self._binding_types(item, item_type)
            ]
        if isinstance(pattern, nodes.OrPattern):
            return self._binding_types(pattern.patterns[0], expected) if pattern.patterns else []
        return []

    def _lower_pattern(
        self,
        pattern: nodes.Pattern,
        value: int,
        expected: Type,
        fail_label: str,
        bindings: dict[str, int] | None = None,
    ) -> None:
        if isinstance(pattern, nodes.WildcardPattern):
            return
        if isinstance(pattern, nodes.NamePattern):
            if isinstance(expected, CoreAdtType):
                constructor = expected.constructor(pattern.name)
                if constructor is not None:
                    if constructor.payload:
                        raise UnsupportedSyntax(
                            f"Constructor '{constructor.name}' requires arguments.",
                            pattern.position,
                        )
                    index = next(
                        index
                        for index, item in enumerate(expected.constructors)
                        if item.name == constructor.name
                    )
                    self._emit_tag_test(value, index, fail_label, pattern.position)
                    return
            slot = None if bindings is None else bindings.get(pattern.name)
            if slot is None:
                slot = self._declare_local(pattern.name, mutable=False, position=pattern.position)
                slot_type = _ir_type_from(expected, pattern.position)
                self._record(slot, slot_type, pattern.position)
            self._emit(Move(pattern.position, slot, value))
            return
        if isinstance(pattern, nodes.LiteralPattern):
            expected_type = _ir_type_from(expected, pattern.position)
            constant = self._const(pattern.value, pattern.position)
            self._record(constant, expected_type, pattern.position)
            ok = self._alloc(pattern.position)
            self._record(ok, IrType.BOOL, pattern.position)
            self._emit(BinOp(pattern.position, ok, "==", value, constant))
            self._emit(JumpIfFalse(pattern.position, ok, fail_label))
            return
        if isinstance(pattern, nodes.TuplePattern):
            if not isinstance(expected, TupleType):
                raise UnsupportedSyntax(
                    "Tuple patterns require a Tuple scrutinee.", pattern.position
                )
            for index, (item, item_type) in enumerate(
                zip(pattern.patterns, expected.elements, strict=True)
            ):
                slot_type = _ir_type_from(item_type, pattern.position)
                slot = self._alloc(pattern.position)
                self._record(slot, slot_type, pattern.position)
                self._emit(TupleItem(pattern.position, slot, value, index))
                self._lower_pattern(item, slot, item_type, fail_label, bindings)
            return
        if isinstance(pattern, nodes.OrPattern):
            if not pattern.patterns:
                return
            slot_map = dict(bindings or {})
            for name, binding_type in self._binding_types(pattern.patterns[0], expected):
                if name not in slot_map:
                    slot = self._declare_local(name, mutable=False, position=pattern.position)
                    self._record(
                        slot, _ir_type_from(binding_type, pattern.position), pattern.position
                    )
                    slot_map[name] = slot
            success = self._new_label("or_success")
            for alt_index, alternative in enumerate(pattern.patterns):
                alt_fail = (
                    fail_label
                    if alt_index == len(pattern.patterns) - 1
                    else self._new_label("or_fail")
                )
                self._lower_pattern(alternative, value, expected, alt_fail, slot_map)
                self._emit(Jump(pattern.position, success))
                if alt_index != len(pattern.patterns) - 1:
                    self._emit(Label(pattern.position, alt_fail))
            self._emit(Label(pattern.position, success))
            return
        if isinstance(pattern, nodes.ConstructorPattern):
            if not isinstance(expected, CoreAdtType):
                raise UnsupportedSyntax(
                    "Constructor patterns require an ADT scrutinee.", pattern.position
                )
            constructor = expected.constructor(pattern.name)
            if constructor is None or len(constructor.payload) != len(pattern.args):
                raise UnsupportedSyntax(
                    f"Constructor pattern '{pattern.name}' does not match the ADT.",
                    pattern.position,
                )
            index = next(
                index
                for index, item in enumerate(expected.constructors)
                if item.name == constructor.name
            )
            self._emit_tag_test(value, index, fail_label, pattern.position)
            for field_index, (argument, payload_type) in enumerate(
                zip(pattern.args, _instantiated_payload(expected, constructor), strict=True)
            ):
                field = self._alloc(pattern.position)
                field_type = _ir_type_from(payload_type, pattern.position)
                self._record(field, field_type, pattern.position)
                self._emit(AdtField(pattern.position, field, value, field_index))
                self._lower_pattern(argument, field, payload_type, fail_label, bindings)
            return
        raise UnsupportedSyntax(
            f"Typed HIR backend does not support pattern {type(pattern).__name__}.",
            pattern.position,
        )

    def _lower_function(self, node: nodes.FunctionDef, index: int) -> HirFunction:
        signature = node.metadata.get("type_obj")
        if not isinstance(signature, FunctionType):
            raise UnsupportedSyntax(
                f"Typed HIR backend is missing the signature of '{node.name}'.",
                node.position,
            )
        self._current_ret = _ir_type_from(signature.ret, node.position)
        result = super()._lower_function(node, index)
        self.function_types[node.name] = signature
        return result

    def _lower_function_body(self, node: nodes.FunctionDef) -> int:
        last: int | None = None
        for stmt in node.body.statements:
            last = self._lower_stmt(stmt)
        if last is None:
            # An explicit trailing return already ended every path; do not
            # append the unreachable Unit return the erased path emits.
            if node.body.statements and isinstance(node.body.statements[-1], nodes.ReturnExpr):
                return -1
            last = self._const(None, node.position)
        self._emit(Return(node.position, last))
        return last


def _filled_register_types(
    function: HirFunction, recorded: dict[int, IrTypeLike]
) -> tuple[IrTypeLike | None, ...]:
    table: list[IrTypeLike | None] = [None] * function.local_count
    for register, ir_type in recorded.items():
        if 0 <= register < function.local_count:
            table[register] = ir_type
    for instruction in function.code:
        if isinstance(instruction, LoadConst) and table[instruction.dst] is None:
            table[instruction.dst] = _constant_ir_type(instruction.value)
    return tuple(table)


def _constant_ir_type(value: object) -> IrType | None:
    if value is None:
        return IrType.UNIT
    if isinstance(value, bool):
        return IrType.BOOL
    if isinstance(value, int):
        return IrType.INT
    if isinstance(value, float):
        return IrType.FLOAT
    return None


def _user_module(module: nodes.ModuleNode) -> nodes.ModuleNode:
    """Keep prelude enums: Option/Result constructors participate in S4b.

    The typed lowerer turns EnumDef into module declarations and a no-op main
    instruction, so prelude enums no longer introduce BUILD_ENUM code.
    """

    return module


def _main_return_type(
    function: HirFunction, register_types: tuple[IrTypeLike | None, ...]
) -> IrTypeLike:
    """The main body's value type is the final return register's type."""

    for instruction in reversed(function.code):
        if isinstance(instruction, Return):
            register = instruction.src
            if 0 <= register < len(register_types) and register_types[register] is not None:
                return register_types[register]  # type: ignore[return-value]
            return IrType.UNIT
    return IrType.UNIT


def _iterated_type(ir_type: IrTypeLike | None) -> IrTypeLike | None:
    if isinstance(ir_type, ContainerType):
        if ir_type.kind in ("List", "Set"):
            return ir_type.args[0]
        if ir_type.kind == "Dict":
            return ir_type.args[0]
        if ir_type.kind == "Tuple" and len(set(ir_type.args)) == 1:
            return ir_type.args[0]
    if ir_type is IrType.STRING:
        return IrType.STRING
    return None


def _infer_control_register_types(function: HirFunction, recorded: dict[int, IrTypeLike]) -> None:
    """Record iterator/value registers created by the shared for-loop lowering."""

    iterator_elements: dict[int, IrTypeLike] = {}
    for instruction in function.code:
        if isinstance(instruction, OpenIterator):
            element = _iterated_type(recorded.get(instruction.iterable))
            if element is not None:
                recorded[instruction.dst] = IrType.ITERATOR
                iterator_elements[instruction.dst] = element
        elif isinstance(instruction, IteratorNext):
            element = iterator_elements.get(instruction.iterator)
            if element is not None:
                recorded[instruction.value_dst] = element


def lower_typed_module(module: nodes.ModuleNode) -> TypedModule:
    """Lower a checked ``oort-core`` module to typed HIR.

    Only the scalar subset is accepted; anything else raises
    ``UnsupportedSyntax`` rather than silently falling back.
    """

    module = _user_module(module)
    _validate_module(module)
    adt_decls, constructors = _collect_adt_decls(module)
    lowerer = _TypedHirLowerer(adt_decls, constructors)
    hir = lowerer.lower(module)

    typed_functions: list[TypedFunction] = []
    for function in hir.functions:
        signature = lowerer.function_types.get(function.name)
        if signature is None:
            raise UnsupportedSyntax(
                f"Typed HIR backend is missing the signature of '{function.name}'.",
                function.position,
            )
        param_types = tuple(_ir_type_from(param, function.position) for param in signature.params)
        ret_type = _ir_type_from(signature.ret, function.position)
        recorded = lowerer.register_types.get(function.name, {})
        _infer_control_register_types(function, recorded)
        register_types = _filled_register_types(function, recorded)
        typed_functions.append(TypedFunction(function, param_types, ret_type, register_types))

    main_recorded = lowerer.register_types.get(hir.main.name, {})
    _infer_control_register_types(hir.main, main_recorded)
    main_register_types = _filled_register_types(hir.main, main_recorded)
    main = TypedFunction(
        hir.main,
        (),
        _main_return_type(hir.main, main_register_types),
        main_register_types,
    )
    typed_module = TypedModule(main, tuple(typed_functions), adt_decls)
    validate_typed_module(typed_module)
    return typed_module


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def _invalid(function: TypedFunction, instruction: Instruction, message: str) -> NoReturn:
    raise UnsupportedSyntax(
        f"Typed HIR validation failed in '{function.hir.name}': {message}.",
        instruction.position,
    )


def _is_numeric(ir_type: IrTypeLike | None) -> bool:
    return isinstance(ir_type, IrType) and ir_type in (IrType.INT, IrType.FLOAT)


def _check_binop(function: TypedFunction, instruction: BinOp) -> None:
    table = function.register_types
    lhs = table[instruction.lhs]
    rhs = table[instruction.rhs]
    result = table[instruction.dst]
    op = instruction.op
    if op == "+" and lhs is IrType.STRING and rhs is IrType.STRING:
        if result is not IrType.STRING:
            _invalid(function, instruction, f"+ result {result} != String")
        return
    if op in _ARITHMETIC_OPS | {"/"}:
        if not (_is_numeric(lhs) and _is_numeric(rhs)):
            _invalid(function, instruction, f"non-numeric operands for {op}")
        expected = (
            IrType.FLOAT if op == "/" or lhs is IrType.FLOAT or rhs is IrType.FLOAT else IrType.INT
        )
        if result is not expected:
            _invalid(function, instruction, f"{op} result {result} != {expected}")
        return
    if op in _COMPARISON_OPS:
        if lhs is IrType.STRING and rhs is IrType.STRING:
            if result is not IrType.BOOL:
                _invalid(function, instruction, f"{op} result {result} != Bool")
            return
        if not (_is_numeric(lhs) and _is_numeric(rhs)):
            _invalid(function, instruction, f"non-numeric operands for {op}")
        if result is not IrType.BOOL:
            _invalid(function, instruction, f"{op} result {result} != Bool")
        return
    if op in _EQUALITY_OPS:
        if isinstance(lhs, AdtType) and isinstance(rhs, AdtType) and lhs == rhs:
            if result is not IrType.BOOL:
                _invalid(function, instruction, f"{op} result {result} != Bool")
            return
        if (
            isinstance(lhs, ContainerType)
            and isinstance(rhs, ContainerType)
            and lhs.kind in ("List", "Tuple", "Set", "Dict")
            and lhs == rhs
        ):
            if result is not IrType.BOOL:
                _invalid(function, instruction, f"{op} result {result} != Bool")
            return
        if lhs is IrType.STRING and rhs is IrType.STRING:
            if result is not IrType.BOOL:
                _invalid(function, instruction, f"{op} result {result} != Bool")
            return
        comparable = (_is_numeric(lhs) and _is_numeric(rhs)) or (
            lhs is rhs and lhs in (IrType.INT, IrType.FLOAT, IrType.BOOL)
        )
        if not comparable:
            _invalid(function, instruction, f"incompatible operands for {op}")
        if result is not IrType.BOOL:
            _invalid(function, instruction, f"{op} result {result} != Bool")
        return
    _invalid(function, instruction, f"unsupported binary operator {op!r}")


def _check_unop(function: TypedFunction, instruction: UnOp) -> None:
    table = function.register_types
    operand = table[instruction.operand]
    result = table[instruction.dst]
    if instruction.op in {"+", "-"}:
        if not _is_numeric(operand):
            _invalid(function, instruction, f"non-numeric operand for {instruction.op}")
        if result is not operand:
            _invalid(function, instruction, f"{instruction.op} result {result} != {operand}")
        return
    if instruction.op == "not":
        if operand is not IrType.BOOL or result is not IrType.BOOL:
            _invalid(function, instruction, "not requires Bool -> Bool")
        return
    _invalid(function, instruction, f"unsupported unary operator {instruction.op!r}")


def _check_return(function: TypedFunction, instruction: Return) -> None:
    value = function.register_types[instruction.src]
    if value != function.ret_type:
        _invalid(
            function,
            instruction,
            f"return type {value} != {function.ret_type}",
        )


def _iterated_element_type(container: IrTypeLike, node: nodes.ASTNode) -> IrTypeLike:
    if isinstance(container, ContainerType):
        if container.kind in ("List", "Set", "Dict"):
            return container.args[0]
        if container.kind == "Tuple":
            if len(set(container.args)) != 1:
                _reject(node, "iteration over a heterogeneous Tuple")
            return container.args[0]
    if container is IrType.STRING:
        return IrType.STRING
    _reject(node, f"iteration over {container}")


def _validate_sequence(
    function: TypedFunction, instruction: BuildList | BuildSet | BuildTuple
) -> None:
    table = function.register_types
    target = table[instruction.dst]
    if isinstance(instruction, BuildList):
        expected_kind = "List"
    elif isinstance(instruction, BuildSet):
        expected_kind = "Set"
    else:
        expected_kind = "Tuple"
    if not isinstance(target, ContainerType) or target.kind != expected_kind:
        _invalid(
            function, instruction, f"{expected_kind} literal has unexpected target type {target}"
        )
    if expected_kind in ("List", "Set"):
        if len(target.args) != 1:
            _invalid(function, instruction, f"{expected_kind} type must have one element type")
        element_type = target.args[0]
        for register in instruction.elements:
            if table[register] != element_type:
                _invalid(
                    function,
                    instruction,
                    f"{expected_kind} element type {table[register]} != {element_type}",
                )
    else:
        if len(instruction.elements) != len(target.args):
            _invalid(function, instruction, "Tuple literal arity does not match its type")
        for register, expected in zip(instruction.elements, target.args, strict=True):
            if table[register] != expected:
                _invalid(
                    function, instruction, f"Tuple element type {table[register]} != {expected}"
                )


def _validate_dict(function: TypedFunction, instruction: BuildDict) -> None:
    table = function.register_types
    target = table[instruction.dst]
    if not isinstance(target, ContainerType) or target.kind != "Dict":
        _invalid(function, instruction, f"Dict literal has unexpected target type {target}")
    if len(target.args) != 2:
        _invalid(function, instruction, "Dict type must have a key and a value type")
    key_type, value_type = target.args
    for key, value in instruction.items:
        if table[key] != key_type:
            _invalid(function, instruction, f"Dict key type {table[key]} != {key_type}")
        if table[value] != value_type:
            _invalid(function, instruction, f"Dict value type {table[value]} != {value_type}")


def _validate_get_item(function: TypedFunction, instruction: GetItem) -> None:
    table = function.register_types
    container = table[instruction.container]
    index_type = table[instruction.index]
    if isinstance(container, ContainerType) and container.kind == "Dict":
        if len(container.args) != 2:
            _invalid(function, instruction, "Dict type must have a key and a value type")
        if index_type != container.args[0]:
            _invalid(function, instruction, f"Dict key type {index_type} != {container.args[0]}")
        expected = container.args[1]
    else:
        if index_type is not IrType.INT:
            _invalid(function, instruction, "index is not Int")
        if isinstance(container, ContainerType):
            if container.kind == "List":
                expected = container.args[0]
            elif container.kind == "Tuple":
                if len(set(container.args)) != 1:
                    _invalid(function, instruction, "heterogeneous tuple indexing is not supported")
                expected = container.args[0]
            else:
                _invalid(function, instruction, f"cannot index {container.kind}")
        elif container is IrType.STRING:
            expected = IrType.STRING
        else:
            _invalid(function, instruction, f"cannot index {container}")
    if table[instruction.dst] != expected:
        _invalid(function, instruction, f"index result {table[instruction.dst]} != {expected}")


def _adt_decl_index(module: TypedModule) -> dict[tuple[str, str], int]:
    return {(decl.origin, decl.name): index for index, decl in enumerate(module.adt_decls)}


def _flat_constructors(
    module: TypedModule,
) -> list[tuple[AdtDecl, AdtConstructor]]:
    result: list[tuple[AdtDecl, AdtConstructor]] = []
    for decl in module.adt_decls:
        result.extend((decl, constructor) for constructor in decl.constructors)
    return result


def validate_typed_module(module: TypedModule) -> None:
    """Assert typed-HIR invariants; raise ``UnsupportedSyntax`` on violation."""

    for function in (module.main, *module.functions):
        hir = function.hir
        if len(function.register_types) != hir.local_count:
            raise UnsupportedSyntax(
                f"Typed HIR function '{hir.name}' has {len(function.register_types)} "
                f"register types for {hir.local_count} registers.",
                hir.position,
            )
        if len(function.param_types) != len(hir.params):
            raise UnsupportedSyntax(
                f"Typed HIR function '{hir.name}' has {len(function.param_types)} "
                f"param types for {len(hir.params)} parameters.",
                hir.position,
            )
        table = function.register_types
        iterator_elements: dict[int, IrTypeLike] = {}
        for instruction in hir.code:
            for register in (*register_reads(instruction), *register_writes(instruction)):
                if not 0 <= register < len(function.register_types):
                    _invalid(function, instruction, f"register R{register} out of range")
                if function.register_types[register] is None:
                    _invalid(function, instruction, f"register R{register} has no type")
            if isinstance(instruction, BinOp):
                _check_binop(function, instruction)
            elif isinstance(instruction, UnOp):
                _check_unop(function, instruction)
            elif isinstance(instruction, Return):
                _check_return(function, instruction)
            elif isinstance(instruction, (JumpIfFalse, JumpIfTrue)):
                if function.register_types[instruction.src] is not IrType.BOOL:
                    _invalid(function, instruction, "branch condition is not Bool")
            elif isinstance(instruction, Move):
                source = function.register_types[instruction.src]
                target = function.register_types[instruction.dst]
                if source != target:
                    _invalid(function, instruction, f"move {source} -> {target}")
            elif isinstance(instruction, Call):
                if function.register_types[instruction.callee] is not IrType.FUNCTION:
                    _invalid(function, instruction, "callee is not a function")
                if instruction.keywords or instruction.block is not None:
                    _invalid(function, instruction, "keyword or block arguments")
                for register in instruction.args:
                    if function.register_types[register] is IrType.FUNCTION:
                        _invalid(function, instruction, "function argument")
                if function.register_types[instruction.dst] is IrType.FUNCTION:
                    _invalid(function, instruction, "call returning a function")
            elif isinstance(instruction, LoadGlobal):
                if function.register_types[instruction.dst] is not IrType.FUNCTION:
                    _invalid(function, instruction, "non-function global")
            elif isinstance(instruction, StoreGlobal):
                _invalid(function, instruction, "global stores")
            elif isinstance(instruction, (BuildList, BuildSet, BuildTuple)):
                _validate_sequence(function, instruction)
            elif isinstance(instruction, BuildDict):
                _validate_dict(function, instruction)
            elif isinstance(instruction, BuildAdt):
                candidates = _flat_constructors(module)
                if not 0 <= instruction.constructor_id < len(candidates):
                    _invalid(function, instruction, "ADT constructor id out of range")
                _, constructor = candidates[instruction.constructor_id]
                target = table[instruction.dst]
                if not isinstance(target, AdtType):
                    _invalid(function, instruction, "ADT constructor target is not an ADT")
                if len(instruction.args) != constructor.arity:
                    _invalid(function, instruction, "ADT constructor arity mismatch")
                if constructor.payload:
                    for argument, expected in zip(
                        instruction.args, constructor.payload, strict=True
                    ):
                        if table[argument] != expected:
                            _invalid(
                                function,
                                instruction,
                                f"ADT payload {table[argument]} != {expected}",
                            )
            elif isinstance(instruction, AdtTag):
                if not isinstance(table[instruction.value], AdtType):
                    _invalid(function, instruction, "ADT tag source is not an ADT")
                if table[instruction.dst] is not IrType.INT:
                    _invalid(function, instruction, "ADT tag target is not Int")
            elif isinstance(instruction, AdtField):
                source = table[instruction.value]
                if not isinstance(source, AdtType):
                    _invalid(function, instruction, "ADT field source is not an ADT")
                target = table[instruction.dst]
                field_types = [
                    constructor.payload[instruction.index]
                    for decl in module.adt_decls
                    if (decl.origin, decl.name) == (source.origin, source.name)
                    for constructor in decl.constructors
                    if instruction.index < len(constructor.payload)
                ]
                if field_types and not any(candidate == target for candidate in field_types):
                    _invalid(function, instruction, "ADT field type mismatch")
            elif isinstance(instruction, TupleItem):
                source = table[instruction.value]
                if not isinstance(source, ContainerType) or source.kind != "Tuple":
                    _invalid(function, instruction, "TupleItem source is not a Tuple")
                if not 0 <= instruction.index < len(source.args):
                    _invalid(function, instruction, "TupleItem index out of range")
                if table[instruction.dst] != source.args[instruction.index]:
                    _invalid(function, instruction, "TupleItem type mismatch")
            elif isinstance(instruction, GetItem):
                _validate_get_item(function, instruction)
            elif isinstance(instruction, SetItem):
                container = table[instruction.container]
                if not isinstance(container, ContainerType) or container.kind != "List":
                    _invalid(function, instruction, "SetItem target is not a List")
                if table[instruction.index] is not IrType.INT:
                    _invalid(function, instruction, "SetItem index is not Int")
                if table[instruction.src] != container.args[0]:
                    _invalid(function, instruction, "SetItem value type mismatch")
            elif isinstance(instruction, OpenIterator):
                if table[instruction.dst] is not IrType.ITERATOR:
                    _invalid(function, instruction, "iterator destination is not Iterator")
                element = _iterated_type(table[instruction.iterable])
                if element is None:
                    _invalid(
                        function,
                        instruction,
                        f"iteration over {table[instruction.iterable]}",
                    )
                iterator_elements[instruction.dst] = element
            elif isinstance(instruction, IteratorNext):
                expected_element = iterator_elements.get(instruction.iterator)
                if expected_element is None:
                    _invalid(function, instruction, "iterator was not opened in this function")
                if table[instruction.value_dst] != expected_element:
                    _invalid(function, instruction, "iterator value type mismatch")
            elif isinstance(
                instruction,
                (
                    LoadConst,
                    LoadLocal,
                    StoreLocal,
                    Label,
                    Jump,
                    DefineFunction,
                    FreshLocals,
                ),
            ):
                continue
            else:
                _invalid(
                    function, instruction, f"unsupported instruction {type(instruction).__name__}"
                )


# ---------------------------------------------------------------------------
# Dump
# ---------------------------------------------------------------------------


def _register_type_name(types: tuple[IrTypeLike | None, ...], register: int) -> str:
    if 0 <= register < len(types) and types[register] is not None:
        return str(types[register])
    return "?"


def format_typed_function(function: TypedFunction) -> str:
    hir = function.hir
    params = ", ".join(
        f"{name}: {ir_type}" for name, ir_type in zip(hir.params, function.param_types)
    )
    lines = [f"{hir.name}({params}) -> {function.ret_type} local_count={hir.local_count}"]
    for index, instruction in enumerate(hir.code):
        line = f"  {index:4d}  {format_instruction(instruction)}"
        written = [
            f"R{register}:{_register_type_name(function.register_types, register)}"
            for register in register_writes(instruction)
        ]
        if written:
            line += "   ; " + " ".join(written)
        lines.append(line)
    return "\n".join(lines)


def format_typed_module(module: TypedModule) -> str:
    lines = [format_typed_function(module.main)]
    for function in module.functions:
        lines.append("")
        lines.append(format_typed_function(function))
    return "\n".join(lines)
