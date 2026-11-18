#! /usr/bin/env python

"""Macro benchmarks: recursion, loops and class dispatch."""

from benchmarks.bench_utils import compile_program, run_compiled

_FIB = """\
def fib(n) {
    if n <= 1: return n
    fib(n - 1) + fib(n - 2)
}
fib(10)
"""
_LOOP = """\
var total = 0
for i in range(1000) {
    total = total + i
}
total
"""
_METHODS = """\
class Counter {
    def __init__() { this.value = 0 }
    def bump() { this.value = this.value + 1 }
}
var counter = Counter()
for i in range(1000) {
    counter.bump()
}
counter.value
"""


def _bench(benchmark, source: str):
    interpreter, ast = compile_program(source)
    benchmark(run_compiled, interpreter, ast)


def test_macro_fibonacci(benchmark):
    _bench(benchmark, _FIB)


def test_macro_loop(benchmark):
    _bench(benchmark, _LOOP)


def test_macro_method_dispatch(benchmark):
    _bench(benchmark, _METHODS)
