#! /usr/bin/env python

"""Unit tests for the static type model used by `oort-core`."""

from oort_lang.semantics.core.types import (
    BOOL,
    INT,
    NEVER,
    UNIT,
    UNKNOWN,
    AdtTemplate,
    AdtType,
    ConstructorInfo,
    FunctionType,
    ListType,
    ModuleType,
    TypeParameterType,
    UnknownType,
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
