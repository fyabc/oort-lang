#! /usr/bin/env python

"""Static types used by the `oort-core` checker.

The model is deliberately local: primitives, function signatures, built-in
collections, nominal classes and ADTs, plus two internal types for error
recovery (`Unknown`) and non-fallthrough expressions (`Never`).  Generic ADTs
add a small template/applied-type split: an ``AdtTemplate`` is the declaration
(a type constructor) and an ``AdtType`` is one application such as
``Option[Int]``.  Generic constructor schemes are represented by
``ForallType``.  Runtime `OortType` objects are a different concept and are
not reused here; this module belongs to semantic analysis only.
"""

from __future__ import annotations

import dataclasses
from enum import Enum


class Variance(Enum):
    """Declaration-site variance of one enum type parameter."""

    INVARIANT = 0
    COVARIANT = 1
    CONTRAVARIANT = 2


class Type:
    """Base class for static types."""


@dataclasses.dataclass(frozen=True, slots=True)
class PrimitiveType(Type):
    name: str


@dataclasses.dataclass(frozen=True, slots=True)
class ListType(Type):
    element: Type


@dataclasses.dataclass(frozen=True, slots=True)
class SetType(Type):
    element: Type


@dataclasses.dataclass(frozen=True, slots=True)
class DictType(Type):
    key: Type
    value: Type


@dataclasses.dataclass(frozen=True, slots=True)
class TupleType(Type):
    elements: tuple[Type, ...]


@dataclasses.dataclass(frozen=True, slots=True)
class FunctionType(Type):
    params: tuple[Type, ...]
    ret: Type


@dataclasses.dataclass(frozen=True, slots=True)
class ModuleType(Type):
    """A read-only module namespace with typed value and type exports."""

    name: str
    exports: tuple[tuple[str, Type], ...]
    type_exports: tuple[tuple[str, Type | AdtTemplate], ...] = ()

    def get(self, name: str) -> Type | None:
        for export_name, export_type in self.exports:
            if export_name == name:
                return export_type
        return None

    def get_type(self, name: str) -> Type | AdtTemplate | None:
        for export_name, export_type in self.type_exports:
            if export_name == name:
                return export_type
        return None


@dataclasses.dataclass(frozen=True, slots=True)
class CoreModuleInfo:
    """Resolver result for one imported `oort-core` module."""

    name: str
    dialect_name: str
    exports: tuple[tuple[str, Type], ...]
    type_exports: tuple[tuple[str, Type | AdtTemplate], ...] = ()


@dataclasses.dataclass(frozen=True, slots=True)
class TypeParameterType(Type):
    """A rigid type variable referenced inside one generic declaration."""

    name: str
    variance: Variance = Variance.INVARIANT


@dataclasses.dataclass(frozen=True, slots=True)
class ConstructorInfo:
    """One enum constructor and its payload field types."""

    name: str
    field_names: tuple[str, ...]
    payload: tuple[Type, ...]


@dataclasses.dataclass(frozen=True, slots=True)
class SlotInfo:
    """One declared instance slot in a static class."""

    name: str
    slot_type: Type
    mutable: bool
    has_initializer: bool


@dataclasses.dataclass(eq=False, slots=True)
class ClassType(Type):
    """A nominal static class with fixed slots and methods.

    Equality and hashing use `(origin, name)` only; slots, methods and bases
    are filled after the declaration is registered so recursive types work.
    Single inheritance is represented by at most one entry in ``bases``.
    """

    origin: str
    name: str
    slots: tuple[SlotInfo, ...] = ()
    methods: tuple[tuple[str, FunctionType], ...] = ()
    bases: tuple[ClassType, ...] = ()

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, ClassType) and self.origin == other.origin and self.name == other.name
        )

    def __hash__(self) -> int:
        return hash((self.origin, self.name))

    def __repr__(self) -> str:
        return f"<ClassType {self.name!r} @ {self.origin!r}>"

    def mro(self) -> tuple[ClassType, ...]:
        """This class followed by its single-inheritance ancestor chain."""
        chain: list[ClassType] = []
        seen: set[tuple[str, str]] = set()
        current: ClassType | None = self
        while current is not None and (current.origin, current.name) not in seen:
            chain.append(current)
            seen.add((current.origin, current.name))
            current = current.bases[0] if current.bases else None
        return tuple(chain)

    def is_subclass_of(self, other: ClassType) -> bool:
        return other in self.mro()

    def slot(self, name: str) -> SlotInfo | None:
        """Look up a slot on this class or an ancestor; derived classes win."""
        for class_type in self.mro():
            for slot in class_type.slots:
                if slot.name == name:
                    return slot
        return None

    def method(self, name: str) -> FunctionType | None:
        """Look up a method on this class or an ancestor; overrides win."""
        for class_type in self.mro():
            for method_name, method_type in class_type.methods:
                if method_name == name:
                    return method_type
        return None

    def all_slots(self) -> tuple[SlotInfo, ...]:
        """Inherited slots in base-to-derived declaration order."""
        slots: list[SlotInfo] = []
        for class_type in reversed(self.mro()):
            slots.extend(class_type.slots)
        return tuple(slots)


@dataclasses.dataclass(eq=False, slots=True)
class AdtTemplate:
    """The declaration of an enum: a nominal type constructor.

    Payload types may reference this template's own ``TypeParameterType``
    parameters.  ``constructors`` is filled after the declaration is
    registered so recursive payloads can refer back to the template.
    """

    origin: str
    name: str
    params: tuple[TypeParameterType, ...] = ()
    constructors: tuple[ConstructorInfo, ...] = ()

    def constructor(self, name: str) -> ConstructorInfo | None:
        for constructor in self.constructors:
            if constructor.name == name:
                return constructor
        return None


@dataclasses.dataclass(eq=False, slots=True)
class AdtType(Type):
    """An applied tagged-union type, for example ``Option[Int]``.

    Equality and hashing are nominal on ``(template.origin, template.name)``
    and structural on the type arguments.  A monomorphic enum is the special
    case with an empty argument tuple.
    """

    template: AdtTemplate
    args: tuple[Type, ...] = ()

    @property
    def origin(self) -> str:
        return self.template.origin

    @property
    def name(self) -> str:
        return self.template.name

    @property
    def constructors(self) -> tuple[ConstructorInfo, ...]:
        return self.template.constructors

    def variance_at(self, index: int) -> Variance:
        if index < len(self.template.params):
            return self.template.params[index].variance
        return Variance.INVARIANT

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, AdtType)
            and self.template.origin == other.template.origin
            and self.template.name == other.template.name
            and self.args == other.args
        )

    def __hash__(self) -> int:
        return hash((self.template.origin, self.template.name, self.args))

    def __repr__(self) -> str:
        return f"<AdtType {describe_type(self)}>"

    def constructor(self, name: str) -> ConstructorInfo | None:
        return self.template.constructor(name)


@dataclasses.dataclass(frozen=True, slots=True)
class ForallType(Type):
    """A polymorphic value scheme, currently only used by constructors."""

    params: tuple[TypeParameterType, ...]
    body: Type


@dataclasses.dataclass(frozen=True, slots=True)
class UnknownType(Type):
    """Error-recovery type; compatible with everything."""


@dataclasses.dataclass(frozen=True, slots=True)
class NeverType(Type):
    """Type of an expression that cannot fall through (for example `return`)."""


INT = PrimitiveType("Int")
FLOAT = PrimitiveType("Float")
BOOL = PrimitiveType("Bool")
STRING = PrimitiveType("String")
UNIT = PrimitiveType("Unit")
UNKNOWN = UnknownType()
NEVER = NeverType()


def describe_type(type_: Type) -> str:
    if isinstance(type_, PrimitiveType):
        return type_.name
    if isinstance(type_, TypeParameterType):
        return type_.name
    if isinstance(type_, ListType):
        return f"List[{describe_type(type_.element)}]"
    if isinstance(type_, SetType):
        return f"Set[{describe_type(type_.element)}]"
    if isinstance(type_, DictType):
        return f"Dict[{describe_type(type_.key)}, {describe_type(type_.value)}]"
    if isinstance(type_, TupleType):
        elements = ", ".join(describe_type(element) for element in type_.elements)
        return f"Tuple[{elements}]"
    if isinstance(type_, FunctionType):
        params = ", ".join(describe_type(param) for param in type_.params)
        return f"({params}) -> {describe_type(type_.ret)}"
    if isinstance(type_, ModuleType):
        return f"<module {type_.name}>"
    if isinstance(type_, AdtType):
        if not type_.args:
            return type_.name
        args = ", ".join(describe_type(arg) for arg in type_.args)
        return f"{type_.name}[{args}]"
    if isinstance(type_, ForallType):
        params = ", ".join(param.name for param in type_.params)
        return f"forall {params}. {describe_type(type_.body)}"
    if isinstance(type_, ClassType):
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
    if isinstance(expected, TypeParameterType) or isinstance(actual, TypeParameterType):
        return expected == actual
    if isinstance(expected, PrimitiveType) and isinstance(actual, PrimitiveType):
        return expected == actual
    if isinstance(expected, ListType) and isinstance(actual, ListType):
        return is_assignable(expected.element, actual.element)
    if isinstance(expected, SetType) and isinstance(actual, SetType):
        return is_assignable(expected.element, actual.element)
    if isinstance(expected, DictType) and isinstance(actual, DictType):
        return is_assignable(expected.key, actual.key) and is_assignable(
            expected.value, actual.value
        )
    if isinstance(expected, TupleType) and isinstance(actual, TupleType):
        return len(expected.elements) == len(actual.elements) and all(
            is_assignable(expected_element, actual_element)
            for expected_element, actual_element in zip(expected.elements, actual.elements)
        )
    if isinstance(expected, FunctionType) and isinstance(actual, FunctionType):
        return (
            len(expected.params) == len(actual.params)
            # Function parameters are contravariant: the provided function
            # must accept everything the expected signature can pass it.
            and all(
                is_assignable(actual_param, expected_param)
                for expected_param, actual_param in zip(expected.params, actual.params)
            )
            and is_assignable(expected.ret, actual.ret)
        )
    if isinstance(expected, ModuleType) and isinstance(actual, ModuleType):
        return expected == actual
    if isinstance(expected, AdtType) and isinstance(actual, AdtType):
        if not _same_template(expected, actual) or len(expected.args) != len(actual.args):
            return False
        # Variance-aware; with no subtyping today every case degenerates to
        # equality, but Unknown still participates in error recovery.
        for index, (expected_arg, actual_arg) in enumerate(zip(expected.args, actual.args)):
            variance = expected.variance_at(index)
            if variance is Variance.COVARIANT:
                if not is_assignable(expected_arg, actual_arg):
                    return False
            elif variance is Variance.CONTRAVARIANT:
                if not is_assignable(actual_arg, expected_arg):
                    return False
            elif not (
                is_assignable(expected_arg, actual_arg) and is_assignable(actual_arg, expected_arg)
            ):
                return False
        return True
    if isinstance(expected, ClassType) and isinstance(actual, ClassType):
        return actual.is_subclass_of(expected)
    if isinstance(expected, ForallType) and isinstance(actual, ForallType):
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
    if isinstance(left, AdtType) and isinstance(right, AdtType):
        if not _same_template(left, right) or len(left.args) != len(right.args):
            return None
        joined_args: list[Type] = []
        for left_arg, right_arg in zip(left.args, right.args):
            joined = join_types(left_arg, right_arg)
            if joined is None:
                return None
            joined_args.append(joined)
        return AdtType(left.template, tuple(joined_args))
    if isinstance(left, ClassType) and isinstance(right, ClassType):
        if left.is_subclass_of(right):
            return right
        if right.is_subclass_of(left):
            return left
        return None
    return None


def substitute(type_: Type, mapping: dict[str, Type]) -> Type:
    """Replace rigid type parameters by the given mapping."""
    if isinstance(type_, TypeParameterType):
        return mapping.get(type_.name, type_)
    if isinstance(type_, ListType):
        return ListType(substitute(type_.element, mapping))
    if isinstance(type_, SetType):
        return SetType(substitute(type_.element, mapping))
    if isinstance(type_, DictType):
        return DictType(substitute(type_.key, mapping), substitute(type_.value, mapping))
    if isinstance(type_, TupleType):
        return TupleType(tuple(substitute(element, mapping) for element in type_.elements))
    if isinstance(type_, FunctionType):
        return FunctionType(
            tuple(substitute(param, mapping) for param in type_.params),
            substitute(type_.ret, mapping),
        )
    if isinstance(type_, AdtType):
        return AdtType(type_.template, tuple(substitute(arg, mapping) for arg in type_.args))
    if isinstance(type_, ForallType):
        inner = {key: value for key, value in mapping.items() if key not in _param_names(type_)}
        return ForallType(type_.params, substitute(type_.body, inner))
    return type_


def _param_names(scheme: ForallType) -> frozenset[str]:
    return frozenset(param.name for param in scheme.params)


def _same_template(left: AdtType, right: AdtType) -> bool:
    return (
        left.template.origin == right.template.origin and left.template.name == right.template.name
    )


@dataclasses.dataclass(slots=True)
class UnifyFailure:
    """Why constructor-call inference failed: a parameter conflict or a mismatch."""

    kind: str
    parameter: str | None
    expected: Type
    actual: Type


def unify(pattern: Type, actual: Type, bindings: dict[str, Type]) -> UnifyFailure | None:
    """Solve the constructor's type parameters against one argument type.

    Returns ``None`` on success (bindings may have grown) or a failure
    describing the first conflicting position.  This is a small first-order
    unifier used only for constructor instantiation; it is not HM inference.
    """
    if isinstance(pattern, TypeParameterType):
        existing = bindings.get(pattern.name)
        if existing is None:
            bindings[pattern.name] = actual
            return None
        if (
            existing == actual
            or isinstance(existing, (UnknownType, NeverType))
            or isinstance(actual, (UnknownType, NeverType))
        ):
            return None
        return UnifyFailure("conflict", pattern.name, existing, actual)
    if isinstance(pattern, (UnknownType, NeverType)):
        return None
    if isinstance(actual, (UnknownType, NeverType)):
        return None
    if isinstance(pattern, PrimitiveType) and isinstance(actual, PrimitiveType):
        if pattern == actual:
            return None
        return UnifyFailure("mismatch", None, pattern, actual)
    if isinstance(pattern, ListType) and isinstance(actual, ListType):
        return unify(pattern.element, actual.element, bindings)
    if isinstance(pattern, SetType) and isinstance(actual, SetType):
        return unify(pattern.element, actual.element, bindings)
    if isinstance(pattern, DictType) and isinstance(actual, DictType):
        return unify(pattern.key, actual.key, bindings) or unify(
            pattern.value, actual.value, bindings
        )
    if isinstance(pattern, TupleType) and isinstance(actual, TupleType):
        if len(pattern.elements) != len(actual.elements):
            return UnifyFailure("mismatch", None, pattern, actual)
        for pattern_element, actual_element in zip(pattern.elements, actual.elements):
            failure = unify(pattern_element, actual_element, bindings)
            if failure is not None:
                return failure
        return None
    if isinstance(pattern, FunctionType) and isinstance(actual, FunctionType):
        if len(pattern.params) != len(actual.params):
            return UnifyFailure("mismatch", None, pattern, actual)
        for pattern_param, actual_param in zip(pattern.params, actual.params):
            failure = unify(pattern_param, actual_param, bindings)
            if failure is not None:
                return failure
        return unify(pattern.ret, actual.ret, bindings)
    if isinstance(pattern, AdtType) and isinstance(actual, AdtType):
        if not _same_template(pattern, actual) or len(pattern.args) != len(actual.args):
            return UnifyFailure("mismatch", None, pattern, actual)
        for pattern_arg, actual_arg in zip(pattern.args, actual.args):
            failure = unify(pattern_arg, actual_arg, bindings)
            if failure is not None:
                return failure
        return None
    if pattern == actual:
        return None
    return UnifyFailure("mismatch", None, pattern, actual)
