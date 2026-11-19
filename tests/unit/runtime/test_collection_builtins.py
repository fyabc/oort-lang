#! /usr/bin/env python

"""Eager collection helpers: map, filter, zip, enumerate and sorted."""

import pytest

from oort_lang.driver.compiler import CompilerError


def test_map_with_trailing_lambda(run_source):
    out = run_source("print(map([3, 1, 2]) do(x): x * 2)\n").stdout
    assert out == "[6, 2, 4]\n"


def test_map_with_named_function_and_native_callback(run_source):
    out = run_source(
        """\
def inc(x) { x + 1 }
print(map(range(3), inc))
print(map(["a", "b"], str))
"""
    ).stdout
    assert out == "[1, 2, 3]\n[a, b]\n"


def test_filter_and_null_predicate(run_source):
    out = run_source(
        """\
print(filter([3, 1, 2]) do(x): x > 1)
print(filter([0, 1, "", "x", null, 2], null))
"""
    ).stdout
    assert out == "[3, 2]\n[1, x, 2]\n"


def test_zip_stops_at_shortest_and_handles_empty(run_source):
    out = run_source(
        """\
print(zip([1, 2, 3], [10, 20]))
print(zip([1], [2], [3]))
print(zip())
"""
    ).stdout
    assert out == "[(1, 10), (2, 20)]\n[(1, 2, 3)]\n[]\n"


def test_enumerate_start(run_source):
    out = run_source(
        """\
print(enumerate(["a", "b"]))
print(enumerate(["a", "b"], 1))
print(enumerate(["a"], -1))
"""
    ).stdout
    assert out == "[(0, a), (1, b)]\n[(1, a), (2, b)]\n[(-1, a)]\n"


def test_sorted_returns_a_new_list(run_source):
    out = run_source(
        """\
val xs = [3, 1, 2]
val ys = sorted(xs)
print(xs)
print(ys)
"""
    ).stdout
    assert out == "[3, 1, 2]\n[1, 2, 3]\n"


def test_sorted_key_and_reverse(run_source):
    out = run_source(
        """\
print(sorted([3, 1, 2]) do(x): -x)
print(sorted([3, 1, 2], null, true))
print(sorted([3, 1, 2], do(x): -x, true))
"""
    ).stdout
    assert out == "[3, 2, 1]\n[3, 2, 1]\n[1, 2, 3]\n"


def test_sorted_is_stable_and_uses_user_less_than(run_source):
    out = run_source(
        """\
class Item {
    def __init__(key, name) {
        this.key = key
        this.name = name
    }
    def operator "<"(other) { this.key < other.key }
}
val items = [Item(1, "a"), Item(1, "b"), Item(0, "c")]
print(map(sorted(items)) do(item): item.name)
"""
    ).stdout
    assert out == "[c, a, b]\n"


def test_collection_helpers_iterate_strings_and_dict_keys(run_source):
    out = run_source(
        """\
print(map("ab") do(c): c)
print(map({: "a": 1, "b": 2 :}) do(k): k)
print(enumerate("xy"))
"""
    ).stdout
    assert out == "[a, b]\n[a, b]\n[(0, x), (1, y)]\n"


def test_empty_inputs(run_source):
    out = run_source(
        """\
print(map([], do(x): x))
print(filter([], null))
print(zip([], [1]))
print(enumerate([]))
print(sorted([]))
"""
    ).stdout
    assert out == "[]\n[]\n[]\n[]\n[]\n"


@pytest.mark.parametrize(
    ("source", "message"),
    [
        ("map(1, do(x): x)\n", "not iterable"),
        ("map([1], 2)\n", "not callable"),
        ("filter([1], 2)\n", "not callable"),
        ("zip([1], 2)\n", "not iterable"),
        ('enumerate([1], "x")\n', "start must be an Int"),
        ('sorted([1, "a"])\n', "Operator '<' is not supported"),
    ],
)
def test_collection_helper_errors(source: str, message: str, run_source, caplog):
    with pytest.raises(CompilerError):
        run_source(source)
    assert message in caplog.text
