#! /usr/bin/env python

"""Extension method benchmarks: member call vs extension fallback."""

from benchmarks.bench_utils import compile_program, run_compiled

_MEMBER_CALL = """\
class Counter {
    def __init__(n) { this.n = n }
    def next: this.n + 1
}
var counter = Counter(0)
var total = 0
var i = 0
while i < 1000 {
    total = total + counter.next()
    i = i + 1
}
total
"""

_EXTENSION_CALL = """\
class Counter {
    def __init__(n) { this.n = n }
}
def Counter.next: this.n + 1
var counter = Counter(0)
var total = 0
var i = 0
while i < 1000 {
    total = total + counter.next()
    i = i + 1
}
total
"""

_EXTENSION_OPERATOR = """\
class Counter {
    def __init__(n) { this.n = n }
}
def Counter.operator "%%"(other): this.n + other
var counter = Counter(1)
var total = 0
var i = 0
while i < 1000 {
    total = total + (counter %% i)
    i = i + 1
}
total
"""


def _bench(benchmark, source: str):
    interpreter, ast = compile_program(source)
    benchmark(run_compiled, interpreter, ast)


def test_extension_member_call(benchmark):
    _bench(benchmark, _MEMBER_CALL)


def test_extension_method_call(benchmark):
    _bench(benchmark, _EXTENSION_CALL)


def test_extension_operator_call(benchmark):
    _bench(benchmark, _EXTENSION_OPERATOR)
