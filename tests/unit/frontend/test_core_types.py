#! /usr/bin/env python

"""Unit tests for the static type model used by `oort-core`."""

from oort_lang.semantics.core.types import (
    BOOL,
    INT,
    NEVER,
    STRING,
    UNIT,
    UNKNOWN,
    AdtTemplate,
    AdtType,
    ClassType,
    ConstructorInfo,
    FunctionType,
    InterfaceType,
    ListType,
    ModuleType,
    SlotInfo,
    TypeParameterType,
    UnknownType,
    Variance,
    describe_type,
    is_assignable,
    join_types,
    substitute,
    unify,
)


def test_describe_primitive_types():
    assert describe_type(INT) == "Int"
    assert describe_type(BOOL) == "Bool"
    assert describe_type(UNIT) == "Unit"


def test_describe_function_type():
    function = FunctionType((INT, BOOL), UNIT)
    assert describe_type(function) == "(Int, Bool) -> Unit"


def test_assignability():
    assert is_assignable(INT, INT)
    assert not is_assignable(INT, BOOL)
    assert is_assignable(INT, UNKNOWN)
    assert is_assignable(UNKNOWN, INT)
    assert is_assignable(INT, NEVER)
    assert not is_assignable(NEVER, INT)
    assert is_assignable(NEVER, NEVER)


def test_function_types_compare_structurally():
    first = FunctionType((INT,), BOOL)
    second = FunctionType((INT,), BOOL)
    third = FunctionType((BOOL,), BOOL)
    assert first == second
    assert first != third
    assert is_assignable(first, second)
    assert not is_assignable(first, third)


def test_join_types():
    assert join_types(INT, INT) is INT
    assert join_types(NEVER, INT) is INT
    assert join_types(INT, NEVER) is INT
    assert join_types(UNKNOWN, INT) is UNKNOWN
    assert join_types(INT, BOOL) is None


def test_unknown_is_not_never():
    assert isinstance(UNKNOWN, UnknownType)
    assert UNKNOWN != NEVER


def test_module_type_exports():
    module = ModuleType("./lib", (("value", INT), ("add", FunctionType((INT, INT), INT))))
    assert module.get("value") is INT
    assert module.get("missing") is None
    assert describe_type(module) == "<module ./lib>"
    assert is_assignable(module, module)


def test_module_type_namespace_is_separate_from_values():
    template = _template("Color")
    module = ModuleType("./lib", (("Red", AdtType(template, ())),), (("Color", template),))
    assert module.get("Red") == AdtType(template, ())
    assert module.get_type("Color") is template
    assert module.get("Color") is None
    assert module.get_type("Red") is None


def _template(
    name: str = "Option", origin: str = "main.ort", params: tuple[str, ...] = ()
) -> AdtTemplate:
    return AdtTemplate(origin, name, tuple(TypeParameterType(param) for param in params))


def test_adt_type_is_nominal():
    first = AdtType(_template(), ())
    same = AdtType(_template(), ())
    other_module = AdtType(_template(origin="lib.ort"), ())
    other_name = AdtType(_template("Result"), ())
    assert first == same
    assert first != other_module
    assert first != other_name
    assert hash(first) == hash(same)


def test_adt_type_constructors_and_description():
    template = _template()
    adt = AdtType(template, ())
    some = ConstructorInfo("Some", ("value",), (INT,))
    none = ConstructorInfo("None", (), ())
    template.constructors = (some, none)
    assert adt.constructor("Some") is some
    assert adt.constructor("Missing") is None
    assert describe_type(adt) == "Option"
    assert is_assignable(adt, AdtType(_template(), ()))
    assert not is_assignable(adt, AdtType(_template("Result"), ()))
    assert join_types(adt, AdtType(_template(), ())) == adt
    assert join_types(adt, AdtType(_template("Result"), ())) is None


def test_generic_adt_type_description_and_equality():
    template = _template(params=("T",))
    int_option = AdtType(template, (INT,))
    assert describe_type(int_option) == "Option[Int]"
    assert int_option == AdtType(_template(params=("T",)), (INT,))
    assert int_option != AdtType(template, (BOOL,))
    assert hash(int_option) == hash(AdtType(_template(params=("T",)), (INT,)))


def test_generic_adt_assignability_is_invariant():
    template = _template(params=("T",))
    int_option = AdtType(template, (INT,))
    assert is_assignable(int_option, AdtType(template, (INT,)))
    assert not is_assignable(int_option, AdtType(template, (BOOL,)))
    # Unknown still participates in error recovery.
    assert is_assignable(int_option, AdtType(template, (UNKNOWN,)))
    assert is_assignable(AdtType(template, (UNKNOWN,)), int_option)


def test_join_generic_adt_types():
    template = _template(params=("T",))
    int_option = AdtType(template, (INT,))
    unknown_option = AdtType(template, (UNKNOWN,))
    assert join_types(int_option, int_option) == int_option
    assert join_types(int_option, unknown_option) == unknown_option
    assert join_types(int_option, AdtType(template, (BOOL,))) is None


def test_variance_aware_assignability_through_never():
    covariant = AdtTemplate("main.ort", "Producer", (TypeParameterType("T", Variance.COVARIANT),))
    invariant = AdtTemplate("main.ort", "Box", (TypeParameterType("T", Variance.INVARIANT),))
    contravariant = AdtTemplate(
        "main.ort", "Consumer", (TypeParameterType("T", Variance.CONTRAVARIANT),)
    )

    assert is_assignable(AdtType(covariant, (INT,)), AdtType(covariant, (NEVER,)))
    assert not is_assignable(AdtType(covariant, (NEVER,)), AdtType(covariant, (INT,)))
    assert not is_assignable(AdtType(invariant, (INT,)), AdtType(invariant, (NEVER,)))
    assert not is_assignable(AdtType(invariant, (NEVER,)), AdtType(invariant, (INT,)))
    assert is_assignable(AdtType(contravariant, (NEVER,)), AdtType(contravariant, (INT,)))
    assert not is_assignable(AdtType(contravariant, (INT,)), AdtType(contravariant, (NEVER,)))


def test_substitute_type_parameters():
    template = _template(params=("T",))
    param = TypeParameterType("T")
    applied = AdtType(template, (param,))
    assert substitute(applied, {"T": INT}) == AdtType(template, (INT,))
    assert substitute(ListType(param), {"T": INT}) == ListType(INT)
    assert substitute(FunctionType((param,), param), {"T": INT}) == FunctionType((INT,), INT)


def test_unify_binds_and_detects_conflicts():
    param = TypeParameterType("T")
    bindings = {}
    assert unify(param, INT, bindings) is None
    assert bindings == {"T": INT}
    conflict = unify(param, BOOL, bindings)
    assert conflict is not None
    assert conflict.kind == "conflict"
    assert conflict.parameter == "T"

    list_param = ListType(param)
    bindings = {}
    assert unify(list_param, ListType(INT), bindings) is None
    assert bindings == {"T": INT}
    mismatch = unify(list_param, INT, bindings)
    assert mismatch is not None
    assert mismatch.kind == "mismatch"


def _class(name: str, bases: tuple[ClassType, ...] = ()) -> ClassType:
    return ClassType("main.ort", name, bases=bases)


def test_class_subtyping_and_join():
    base = _class("Base")
    derived = _class("Derived", (base,))
    assert derived.is_subclass_of(base)
    assert not base.is_subclass_of(derived)
    assert is_assignable(base, derived)
    assert not is_assignable(derived, base)
    assert join_types(base, derived) is base
    assert join_types(derived, base) is base
    assert join_types(derived, _class("Other")) is None


def test_inherited_slot_and_method_lookup():
    base = _class("Base")
    base.slots = (SlotInfo("id", INT, False, True),)
    base.methods = (("describe", FunctionType((), STRING)),)
    derived = _class("Derived", (base,))
    derived.slots = (SlotInfo("extra", BOOL, True, False),)
    derived.methods = (("describe", FunctionType((), BOOL)),)
    assert derived.slot("id") == base.slots[0]
    assert derived.slot("extra") == derived.slots[0]
    assert derived.method("describe") == derived.methods[0][1]
    assert derived.all_slots() == (base.slots[0], derived.slots[0])


def test_function_parameters_are_contravariant():
    base = _class("Base")
    derived = _class("Derived", (base,))
    assert is_assignable(FunctionType((derived,), INT), FunctionType((base,), INT))
    assert not is_assignable(FunctionType((base,), INT), FunctionType((derived,), INT))
    assert is_assignable(FunctionType((base,), base), FunctionType((base,), derived))


def _interface(
    name: str,
    interfaces: tuple[InterfaceType, ...] = (),
    methods: tuple[tuple[str, FunctionType], ...] = (),
) -> InterfaceType:
    return InterfaceType("main.ort", name, interfaces=interfaces, methods=methods)


def test_interface_inheritance_and_method_lookup():
    named = _interface("Named", methods=(("name", FunctionType((), STRING)),))
    sized = _interface("Sized", methods=(("size", FunctionType((), INT)),))
    both = _interface("NamedSized", (named, sized))
    assert both.extends_interface(named)
    assert both.extends_interface(sized)
    assert not named.extends_interface(both)
    assert both.method("name") == named.method("name")
    assert both.all_methods() == (
        ("name", FunctionType((), STRING)),
        ("size", FunctionType((), INT)),
    )


def test_class_implements_interface_through_base_classes():
    named = _interface("Named")
    base = _class("Base")
    base.interfaces = (named,)
    derived = _class("Derived", (base,))
    direct = _class("Direct")
    direct.interfaces = (named,)
    assert base.implements_interface(named)
    assert derived.implements_interface(named)
    assert direct.implements_interface(named)
    assert not _class("Other").implements_interface(named)
    assert is_assignable(named, base)
    assert is_assignable(named, derived)
    assert is_assignable(named, direct)
    assert not is_assignable(base, direct)
