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


def test_core_float_arithmetic_executes(run_source):
    result = run_source(core("1.5 + 2.5\n"))
    assert result.value == 4.0


def test_core_division_produces_float(run_source):
    result = run_source(core("7 / 2\n"))
    assert result.value == 3.5


def test_core_string_concatenation_executes(run_source):
    result = run_source(core('"oo" + "rt"\n'))
    assert result.value == "oort"


def test_core_collection_values_execute(run_source):
    result = run_source(
        core(
            "val xs = [3, 1, 2]\n"
            "val pair = (7, true)\n"
            'val d: Dict[String, Int] = {: "a": 1 :}\n'
            'print(xs[1], len(xs), pair[1], d["a"])\n'
        )
    )
    assert result.stdout == "1 3 true 1\n"


def test_core_loops_execute(run_source):
    result = run_source(
        core("var total = 0\nfor x in [1, 2, 3] { total = total + x }\nprint(total)\n")
    )
    assert result.stdout == "6\n"
