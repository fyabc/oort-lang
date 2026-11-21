#! /usr/bin/env python

"""Static types used by the `oort-core` thin probe.

The probe is deliberately small: primitives, function signatures, plus two
internal types for error recovery (`Unknown`) and non-fallthrough expressions
(`Never`).  Runtime `OortType` objects are a different concept and are not
reused here; this module belongs to semantic analysis only.
"""

import dataclasses


class Type:
    """Base class for static types."""


@dataclasses.dataclass(frozen=True, slots=True)
class PrimitiveType(Type):
    name: str


@dataclasses.dataclass(frozen=True, slots=True)
class FunctionType(Type):
    params: tuple[Type, ...]
    ret: Type


@dataclasses.dataclass(frozen=True, slots=True)
class ModuleType(Type):
    """A read-only module namespace with typed exports."""

    name: str
    exports: tuple[tuple[str, Type], ...]

    def get(self, name: str) -> Type | None:
        for export_name, export_type in self.exports:
            if export_name == name:
                return export_type
        return None


@dataclasses.dataclass(frozen=True, slots=True)
class CoreModuleInfo:
    """Resolver result for one imported `oort-core` module."""

    name: str
    dialect_name: str
    exports: tuple[tuple[str, Type], ...]


@dataclasses.dataclass(frozen=True, slots=True)
class ConstructorInfo:
    """One enum constructor and its payload field types."""

    name: str
    field_names: tuple[str, ...]
    payload: tuple[Type, ...]


@dataclasses.dataclass(eq=False, slots=True)
class AdtType(Type):
    """A nominal tagged-union type.

    Equality and hashing use `(origin, name)` only; `constructors` is filled
    after the declaration is registered so recursive payloads can refer back
    to the type being declared.
    """

    origin: str
    name: str
    constructors: tuple[ConstructorInfo, ...] = ()

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, AdtType) and self.origin == other.origin and self.name == other.name
        )

    def __hash__(self) -> int:
        return hash((self.origin, self.name))

    def __repr__(self) -> str:
        return f"<AdtType {self.name!r} @ {self.origin!r}>"

    def constructor(self, name: str) -> ConstructorInfo | None:
        for constructor in self.constructors:
            if constructor.name == name:
                return constructor
        return None


@dataclasses.dataclass(frozen=True, slots=True)
class UnknownType(Type):
    """Error-recovery type; compatible with everything."""


@dataclasses.dataclass(frozen=True, slots=True)
class NeverType(Type):
    """Type of an expression that cannot fall through (for example `return`)."""


INT = PrimitiveType("Int")
BOOL = PrimitiveType("Bool")
UNIT = PrimitiveType("Unit")
UNKNOWN = UnknownType()
NEVER = NeverType()


def describe_type(type_: Type) -> str:
    if isinstance(type_, PrimitiveType):
        return type_.name
    if isinstance(type_, FunctionType):
        params = ", ".join(describe_type(param) for param in type_.params)
        return f"({params}) -> {describe_type(type_.ret)}"
    if isinstance(type_, ModuleType):
        return f"<module {type_.name}>"
    if isinstance(type_, AdtType):
        return type_.name
    if isinstance(type_, UnknownType):
        return "Unknown"
    if isinstance(type_, NeverType):
        return "Never"
    return repr(type_)


def is_assignable(expected: Type, actual: Type) -> bool:
    """Whether a value of `actual` may be used where `expected` is required."""
    if isinstance(expected, UnknownType) or isinstance(actual, UnknownType):
        return True
    if isinstance(actual, NeverType):
        return True
    if isinstance(expected, NeverType):
        return isinstance(actual, NeverType)
    if isinstance(expected, PrimitiveType) and isinstance(actual, PrimitiveType):
        return expected == actual
    if isinstance(expected, FunctionType) and isinstance(actual, FunctionType):
        return expected == actual
    if isinstance(expected, ModuleType) and isinstance(actual, ModuleType):
        return expected == actual
    if isinstance(expected, AdtType) and isinstance(actual, AdtType):
        return expected == actual
    return False


def join_types(left: Type, right: Type) -> Type | None:
    """Least upper bound used for `if` branches; None means incompatible."""
    if isinstance(left, UnknownType) or isinstance(right, UnknownType):
        return UNKNOWN
    if isinstance(left, NeverType):
        return right
    if isinstance(right, NeverType):
        return left
    if left == right:
        return left
    return None
