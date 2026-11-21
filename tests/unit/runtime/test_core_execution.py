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


def test_core_class_slots_execute(run_source):
    result = run_source(
        core(
            "class Counter {\n"
            "    var count: Int\n"
            "    def __init__(start: Int) { this.count = start }\n"
            "    def bump() -> Unit { this.count = this.count + 1 }\n"
            "    def get() -> Int { this.count }\n"
            "}\n"
            "val c = Counter(3)\n"
            "c.bump()\n"
            "print(c.get())\n"
        )
    )
    assert result.stdout == "4\n"


def test_core_slot_initializers_run_before_constructor(run_source):
    result = run_source(
        core(
            "def mark(n: Int) -> Int { print(n)\n    n }\n"
            "class C {\n"
            "    val a: Int = mark(1)\n"
            "    val b: Int = mark(2)\n"
            "    def __init__() { print(3) }\n"
            "}\n"
            "C()\n"
        )
    )
    assert result.stdout == "1\n2\n3\n"


def test_core_slot_initializers_are_per_instance(run_source):
    result = run_source(
        core(
            "class C {\n    var n: Int = 0\n}\nval a = C()\nval b = C()\na.n = 1\nprint(a.n, b.n)\n"
        )
    )
    assert result.stdout == "1 0\n"
