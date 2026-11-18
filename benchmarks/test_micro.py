#! /usr/bin/env python

"""Micro benchmarks: single operations on a compiled program."""

from benchmarks.bench_utils import compile_program, run_compiled

_ARITHMETIC = "1 + 2 * 3 - 4 / 2 + 7 % 3"
_VARIABLES = """\
var a = 1
var b = 2
{
    var x = a + b
    {
        var y = x * 2
        a + y
    }
}
"""
_FUNCTION_CALL = """\
def inc(x) { x + 1 }
inc(41)
"""
_ATTRIBUTE = """\
class Box {
    def __init__(v) { this.v = v }
}
Box(42).v
"""
_INDEX = """\
var xs = [1, 2, 3, 4]
xs[2] = 9
xs[2]
"""
_DICT = """\
var d = {: "a": 1, "b": 2 :}
d["a"] = 3
d["a"]
"""
_CLOSURE = """\
def make(x) { do: x + 1 }
var f = make(41)
f()
"""
_INSTANCE = """\
class Point {
    def __init__(x, y) {
        this.x = x
        this.y = y
    }
}
Point(1, 2)
"""


def _bench(benchmark, source: str):
    interpreter, ast = compile_program(source)
    benchmark(run_compiled, interpreter, ast)


def test_micro_arithmetic(benchmark):
    _bench(benchmark, _ARITHMETIC)


def test_micro_variable_lookup(benchmark):
    _bench(benchmark, _VARIABLES)


def test_micro_function_call(benchmark):
    _bench(benchmark, _FUNCTION_CALL)


def test_micro_attribute(benchmark):
    _bench(benchmark, _ATTRIBUTE)


def test_micro_index(benchmark):
    _bench(benchmark, _INDEX)


def test_micro_dict(benchmark):
    _bench(benchmark, _DICT)


def test_micro_closure(benchmark):
    _bench(benchmark, _CLOSURE)


def test_micro_class_instantiation(benchmark):
    _bench(benchmark, _INSTANCE)
