#! /usr/bin/env python

"""The checked `oort-core` AST executes on the existing interpreter."""


def core(source: str) -> str:
    return "#lang oort-core\n" + source


def test_core_function_returns_value(run_source):
    result = run_source(core("def answer() -> Int { 42 }\nanswer()\n"))
    assert result.value == 42


def test_unit_function_maps_to_null(run_source):
    result = run_source(core("def show(n: Int) -> Unit { print(n) }\nshow(7)\n"))
    assert result.stdout == "7\n"
    assert result.value is None


def test_core_recursion_executes(run_source):
    result = run_source(
        core(
            "def fact(n: Int) -> Int {\n    if n <= 1 { 1 } else { n * fact(n - 1) }\n}\nfact(6)\n"
        )
    )
    assert result.value == 720
