#! /usr/bin/env python

"""Unit tests for the static type model used by `oort-core`."""

from oort_lang.semantics.core.types import (
    BOOL,
    INT,
    NEVER,
    UNIT,
    UNKNOWN,
    FunctionType,
    ModuleType,
    UnknownType,
    describe_type,
    is_assignable,
    join_types,
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
