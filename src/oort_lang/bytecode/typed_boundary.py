#! /usr/bin/env python

"""Semantic boundary between object modules and typed core modules (B1).

The dynamic side imports a checked ``oort-core`` module.  The module is lowered
to typed HIR/bytecode and executed by :class:`TypedCodeVM`; each exported
function is then exposed as a native Oort callable.  Boundary stubs copy
container values and guard arguments, so the two sides never share mutable
container objects.

This is the B1 semantic prototype from design 17: ADTs are copied and guarded
by nominal identity; callbacks, classes/interfaces and a performance boundary
are still out of scope.  Unsupported core features fail explicitly when the
imported module is lowered.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..diagnostics.runtime_errors import OortTypeError
from ..hir.typed import (
    AdtType,
    ContainerType,
    IrType,
    IrTypeLike,
    adt_runtime_name,
)
from ..runtime.functions import OortNativeFunction
from ..runtime.native import NativeMode
from ..runtime.objects import (
    OortADT,
    OortBool,
    OortDict,
    OortFloat,
    OortInt,
    OortList,
    OortNull,
    OortObject,
    OortSet,
    OortString,
    OortTuple,
)
from ..source.source_position import SourcePosition
from .typed_vm import TypedCodeVM

if TYPE_CHECKING:
    from ..runtime.environment import Environment
    from ..runtime.interpreter import ASTInterpreter
    from ..runtime.native import NativeContext
    from .typed_compile import TypedProgram, TypedProto

_BOUNDARY_POSITION = SourcePosition.from_location(1, 0, "", filename="<boundary>")


def _position(position: SourcePosition | None) -> SourcePosition:
    return position or _BOUNDARY_POSITION


def _value_kind(value: OortObject) -> str:
    if isinstance(value, OortList):
        return "List"
    if isinstance(value, OortTuple):
        return "Tuple"
    if isinstance(value, OortSet):
        return "Set"
    if isinstance(value, OortDict):
        return "Dict"
    return value.type.name


def _guard(
    expected: IrTypeLike,
    value: OortObject,
    label: str,
    position: SourcePosition,
) -> None:
    """Recursively check one dynamic value against a typed core type."""

    def fail() -> OortTypeError:
        return OortTypeError(
            f"Boundary guard failed for {label}: expected {expected}, got {_value_kind(value)}.",
            position,
        )

    if isinstance(expected, AdtType):
        if type(value) is not OortADT or value.type.name != adt_runtime_name(expected):
            raise fail()
        return

    if isinstance(expected, ContainerType):
        if expected.kind == "List":
            if type(value) is not OortList:
                raise fail()
            for index, item in enumerate(value.value):
                _guard(expected.args[0], item, f"{label}[{index}]", position)
            return
        if expected.kind == "Tuple":
            if type(value) is not OortTuple:
                raise fail()
            if len(value.value) != len(expected.args):
                raise fail()
            for index, (item, item_type) in enumerate(zip(value.value, expected.args, strict=True)):
                _guard(item_type, item, f"{label}[{index}]", position)
            return
        if expected.kind == "Set":
            if type(value) is not OortSet:
                raise fail()
            for index, item in enumerate(value.value):
                _guard(expected.args[0], item, f"{label}{{{index}}}", position)
            return
        if expected.kind == "Dict":
            if type(value) is not OortDict:
                raise fail()
            for index, (key, item) in enumerate(value.value.items()):
                _guard(expected.args[0], key, f"{label}.key[{index}]", position)
                _guard(expected.args[1], item, f"{label}.value[{index}]", position)
            return
        raise fail()

    ok = (
        (expected is IrType.INT and type(value) is OortInt)
        or (expected is IrType.FLOAT and type(value) is OortFloat)
        or (expected is IrType.BOOL and type(value) is OortBool)
        or (expected is IrType.STRING and type(value) is OortString)
        or (expected is IrType.UNIT and type(value) is OortNull)
    )
    if not ok:
        raise fail()


def _copy_value(value: OortObject) -> OortObject:
    """Copy containers across the boundary; scalars are immutable and shared."""

    if type(value) is OortADT:
        return OortADT(
            value.type,
            value.variant,
            tuple(_copy_value(item) for item in value.values),
        )
    if type(value) is OortList:
        return OortList([_copy_value(item) for item in value.value])
    if type(value) is OortTuple:
        return OortTuple(tuple(_copy_value(item) for item in value.value))
    if type(value) is OortSet:
        return OortSet({_copy_value(item) for item in value.value})
    if type(value) is OortDict:
        return OortDict({_copy_value(key): _copy_value(item) for key, item in value.value.items()})
    if isinstance(
        value,
        (OortInt, OortFloat, OortBool, OortString, OortNull),
    ):
        return value
    raise OortTypeError(
        f"Boundary cannot copy value of type {_value_kind(value)}.",
        _BOUNDARY_POSITION,
    )


class TypedBoundaryFunction(OortNativeFunction):
    """A core function exposed as a dynamic native callable."""

    def __init__(self, vm: TypedCodeVM, proto: TypedProto):
        self.vm = vm
        self.proto = proto
        super().__init__(self._invoke, name=proto.name, mode=NativeMode.CONTEXT)

    def _invoke(self, context: NativeContext, *arguments: OortObject) -> OortObject:
        position = _position(context.position)
        expected = [self.proto.types[type_id] for type_id in self.proto.param_types]
        if len(arguments) != len(expected):
            raise OortTypeError(
                f"Core function '{self.proto.name}' expects {len(expected)} "
                f"arguments, got {len(arguments)}.",
                position,
            )
        copied: list[OortObject] = []
        for index, (expected_type, argument) in enumerate(zip(expected, arguments, strict=True)):
            _guard(expected_type, argument, f"'{self.proto.name}' argument {index}", position)
            copied.append(_copy_value(argument))
        result = self.vm.invoke(self.proto, copied, position)
        return_type = self.proto.types[self.proto.ret_type]
        _guard(return_type, result, f"'{self.proto.name}' return value", position)
        return _copy_value(result)


def execute_core_module(
    env: Environment,
    interpreter: ASTInterpreter,
    program: TypedProgram,
    exports: tuple[str, ...],
) -> None:
    """Run a linked core program and bind the module's exports in ``env``."""

    vm = TypedCodeVM(interpreter)
    vm.run(program)
    protos = {proto.name: proto for proto in program.functions}
    for name in exports:
        proto = protos.get(name)
        if proto is None:
            raise OortTypeError(
                f"Core module export '{name}' is missing from the linked program.",
                _BOUNDARY_POSITION,
            )
        env.define(name, TypedBoundaryFunction(vm, proto))


__all__ = ["TypedBoundaryFunction", "execute_core_module"]
