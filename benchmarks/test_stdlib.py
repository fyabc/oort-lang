#! /usr/bin/env python

"""Standard-library and host-boundary benchmarks."""

from benchmarks.bench_utils import compile_program, run_compiled

_MAP = """\
val xs = range(1000)
map(xs) do(x): x + 1
"""
_FILTER = """\
val xs = range(1000)
filter(xs) do(x): x % 2 == 0
"""
_SORTED = """\
val xs = map(range(100)) do(x): 100 - x
sorted(xs)
"""
_ZIP_ENUMERATE = """\
zip(range(1000), range(1000))
enumerate(range(1000))
"""
_STRING_JOIN = """\
import "string"
string.join(map(range(1000)) do(x): str(x), ",")
"""
_LIST_EQUALITY = "range(1000) == range(1000)"
_NESTED_LEN = """\
val inner = [1, 2, 3]
val xs = [inner] * 1000
len(xs)
"""


def _bench(benchmark, source: str):
    interpreter, ast = compile_program(source)
    benchmark(run_compiled, interpreter, ast)


def test_stdlib_map(benchmark):
    _bench(benchmark, _MAP)


def test_stdlib_filter(benchmark):
    _bench(benchmark, _FILTER)


def test_stdlib_sorted(benchmark):
    _bench(benchmark, _SORTED)


def test_stdlib_zip_enumerate(benchmark):
    _bench(benchmark, _ZIP_ENUMERATE)


def test_stdlib_string_join(benchmark):
    _bench(benchmark, _STRING_JOIN)


def test_host_list_equality_projection(benchmark):
    _bench(benchmark, _LIST_EQUALITY)


def test_host_len_does_not_project(benchmark):
    _bench(benchmark, _NESTED_LEN)
