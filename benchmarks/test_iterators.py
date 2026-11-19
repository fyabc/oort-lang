#! /usr/bin/env python

"""Iterator protocol benchmarks: builtin snapshot and user closures."""

from benchmarks.bench_utils import compile_program, run_compiled

_BUILTIN_LOOP = """\
var total = 0
for x in range(1000) {
    total = total + x
}
total
"""
_USER_ITERATOR = """\
class Countdown {
    def __init__(n) { this.n = n }
    def __iter__() {
        var current = this.n
        do {
            if current > 0 {
                val value = current
                current = current - 1
                (value, true)
            } else {
                (null, false)
            }
        }
    }
}
var total = 0
for x in Countdown(1000) {
    total = total + x
}
total
"""
_USER_INFINITE_BREAK = """\
class Forever {
    def __iter__() { do: (1, true) }
}
var total = 0
for x in Forever() {
    total = total + 1
    if total == 1000 { break }
}
total
"""


def _bench(benchmark, source: str):
    interpreter, ast = compile_program(source)
    benchmark(run_compiled, interpreter, ast)


def test_iterator_builtin_loop(benchmark):
    _bench(benchmark, _BUILTIN_LOOP)


def test_iterator_user_closure(benchmark):
    _bench(benchmark, _USER_ITERATOR)


def test_iterator_infinite_break(benchmark):
    _bench(benchmark, _USER_INFINITE_BREAK)
