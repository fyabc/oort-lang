#! /usr/bin/env python

"""Typed HIR for the restricted ``oort-core`` scalar subset (design 15, M1).

The typed path is deliberately parallel to the erased HIR path: it reuses the
existing instruction classes and register conventions, attaches one static
``IrType`` per register, and accepts only the scalar subset defined in
``docs/design/15-typed-ir.md``. Anything outside the subset is rejected
explicitly; the erased path is never changed.
"""

from __future__ import annotations

import copy
import dataclasses
from enum import Enum
from typing import TYPE_CHECKING, NoReturn

from ..ast import nodes
from ..diagnostics.syntax_errors import UnsupportedSyntax
from ..semantics.core.types import (
    FunctionType,
    NeverType,
    PrimitiveType,
    Type,
    UnknownType,
    describe_type,
)
from .dump import format_instruction
from .lower import HirLowerer
from .nodes import (
    BinOp,
    Call,
    DefineFunction,
    FreshLocals,
    HirFunction,
    Instruction,
    Jump,
    JumpIfFalse,
    JumpIfTrue,
    Label,
    LoadConst,
    LoadGlobal,
    LoadLocal,
    Move,
    Return,
    StoreGlobal,
    StoreLocal,
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

_ARITHMETIC_OPS = {"+", "-", "*", "//", "%"}
_COMPARISON_OPS = {"<", "<=", ">", ">="}
_EQUALITY_OPS = {"==", "!="}
_ALLOWED_BINARY_OPS = _ARITHMETIC_OPS | {"/"} | _COMPARISON_OPS | _EQUALITY_OPS
_ALLOWED_UNARY_OPS = {"+", "-", "not"}


@dataclasses.dataclass(frozen=True, slots=True)
class TypedFunction:
    """One HIR function plus its static signature and register types."""

    hir: HirFunction
    param_types: tuple[IrType, ...]
    ret_type: IrType
    register_types: tuple[IrType | None, ...]


@dataclasses.dataclass(frozen=True, slots=True)
class TypedModule:
    main: TypedFunction
    functions: tuple[TypedFunction, ...]


def _reject(node: nodes.ASTNode, detail: str) -> NoReturn:
    raise UnsupportedSyntax(f"Typed HIR backend does not support {detail}.", node.position)


def _ir_type_from(type_: Type, position, *, allow_function: bool = False) -> IrType:
    if isinstance(type_, PrimitiveType):
        ir_type = _PRIMITIVE_IR.get(type_.name)
        if ir_type is None:
            raise UnsupportedSyntax(
                f"Typed HIR backend does not support primitive type {type_.name}.",
                position,
            )
        return ir_type
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


def _ir_type_for_node(node: nodes.ASTNode, *, allow_function: bool = False) -> IrType:
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
        if isinstance(stmt, (nodes.VarDecl, nodes.Assignment)):
            _reject(stmt, "top-level declarations or assignments (move them into a function)")
        if isinstance(stmt, (nodes.ImportStmt, nodes.ImportFromStmt)):
            _reject(stmt, "module imports")
        if isinstance(stmt, (nodes.ClassDef, nodes.EnumDef, nodes.InterfaceDef)):
            _reject(stmt, f"{type(stmt).__name__.removesuffix('Def')} definitions")
        _validate_expr(stmt)


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
        if not isinstance(param_type, PrimitiveType):
            _reject(node, "higher-order or non-scalar parameters")
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
                nodes.ForExpr,
                nodes.BreakExpr,
                nodes.ContinueExpr,
                nodes.MatchExpr,
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
    if not isinstance(target_type, PrimitiveType):
        _reject(node, "variables without a scalar type")
    if _ir_type_from(target_type, node.position) is IrType.UNIT:
        _reject(node, "Unit variables")
    _validate_expr(node.init_value)


def _validate_assignment(node: nodes.Assignment) -> None:
    if node.op.text != "=":
        _reject(node, f"augmented assignment {node.op.text!r}")
    if not isinstance(node.lhs, nodes.Name):
        _reject(node, "assignment targets other than plain names")
    lhs_type = node.lhs.metadata.get("type_obj")
    if not isinstance(lhs_type, PrimitiveType):
        _reject(node, "assignments without a scalar type")
    _validate_expr(node.rhs)


def _validate_block(node: nodes.BlockExpr) -> None:
    _validate_statements(node.statements)
    type_ = node.metadata.get("type_obj")
    if isinstance(type_, NeverType):
        # A block that always returns/breaks has no value to type.
        return
    _ir_type_for_node(node)


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
    _reject(node, type(node).__name__)


# ---------------------------------------------------------------------------
# Typed lowering: reuse the shared lowerer and record register types
# ---------------------------------------------------------------------------


class _TypedHirLowerer(HirLowerer):
    def __init__(self) -> None:
        super().__init__()
        self.register_types: dict[str, dict[int, IrType]] = {}
        self.function_types: dict[str, FunctionType] = {}
        self._current_ret = IrType.UNIT

    def _record(self, register: int, ir_type: IrType, position) -> None:
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

    def _lower_expr(self, node: nodes.ASTNode | None) -> int | None:
        register = super()._lower_expr(node)
        if register is not None and node is not None:
            type_ = node.metadata.get("type_obj")
            if isinstance(type_, NeverType):
                # Bottom: the register cannot be observed on a normal path,
                # so give it the enclosing function's return type.
                ir_type = self._current_ret
            else:
                # Pre-validation already restricts function-typed values to
                # callee position, so allowing them here keeps the register
                # typed.
                ir_type = _ir_type_for_node(node, allow_function=True)
            self._record(register, ir_type, node.position)
        return register

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
    function: HirFunction, recorded: dict[int, IrType]
) -> tuple[IrType | None, ...]:
    table: list[IrType | None] = [None] * function.local_count
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
    """Return a shallow copy without compiler-injected statements.

    The core prelude injects ``Option``/``Result`` enums; they are irrelevant
    to the scalar typed subset and would otherwise add ``BUILD_ENUM``
    instructions with no typed register meaning.
    """

    statements = [stmt for stmt in module.body.statements if not getattr(stmt, "synthetic", False)]
    if len(statements) == len(module.body.statements):
        return module
    filtered = copy.copy(module)
    body = copy.copy(module.body)
    body.statements = statements
    filtered.body = body
    return filtered


def _main_return_type(function: HirFunction, register_types: tuple[IrType | None, ...]) -> IrType:
    """The main body's value type is the final return register's type."""

    for instruction in reversed(function.code):
        if isinstance(instruction, Return):
            register = instruction.src
            if 0 <= register < len(register_types) and register_types[register] is not None:
                return register_types[register]  # type: ignore[return-value]
            return IrType.UNIT
    return IrType.UNIT


def lower_typed_module(module: nodes.ModuleNode) -> TypedModule:
    """Lower a checked ``oort-core`` module to typed HIR.

    Only the scalar subset is accepted; anything else raises
    ``UnsupportedSyntax`` rather than silently falling back.
    """

    module = _user_module(module)
    _validate_module(module)
    lowerer = _TypedHirLowerer()
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
        register_types = _filled_register_types(
            function, lowerer.register_types.get(function.name, {})
        )
        typed_functions.append(TypedFunction(function, param_types, ret_type, register_types))

    main_register_types = _filled_register_types(
        hir.main, lowerer.register_types.get(hir.main.name, {})
    )
    main = TypedFunction(
        hir.main,
        (),
        _main_return_type(hir.main, main_register_types),
        main_register_types,
    )
    typed_module = TypedModule(main, tuple(typed_functions))
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


def _is_numeric(ir_type: IrType | None) -> bool:
    return ir_type in (IrType.INT, IrType.FLOAT)


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
    if value is not function.ret_type:
        _invalid(
            function,
            instruction,
            f"return type {value} != {function.ret_type}",
        )


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
                if source is not target:
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
            elif isinstance(
                instruction,
                (LoadConst, LoadLocal, StoreLocal, Label, Jump, DefineFunction, FreshLocals),
            ):
                continue
            else:
                _invalid(
                    function, instruction, f"unsupported instruction {type(instruction).__name__}"
                )


# ---------------------------------------------------------------------------
# Dump
# ---------------------------------------------------------------------------


def _register_type_name(types: tuple[IrType | None, ...], register: int) -> str:
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
