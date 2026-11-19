#! /usr/bin/env python

"""User-defined iterator protocol and streaming for loops."""

import pytest

from oort_lang.driver.compiler import CompilerError
from oort_lang.runtime import OortInt, OortIterator, Runtime

COUNTDOWN = """\
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
"""


def test_user_iterator_yields_values(run_source):
    out = run_source(COUNTDOWN + "for value in Countdown(3) { print(value) }\n").stdout
    assert out == "3\n2\n1\n"


def test_empty_iterator(run_source):
    out = run_source(
        """\
class Empty {
    def __iter__() { do: (null, false) }
}
for value in Empty() { print(value) }
print("done")
"""
    ).stdout
    assert out == "done\n"


def test_null_is_a_valid_value(run_source):
    out = run_source(
        """\
class OneNull {
    def __iter__() {
        var done = false
        do {
            if done {
                (null, false)
            } else {
                done = true
                (null, true)
            }
        }
    }
}
var count = 0
for value in OneNull() { count = count + 1 }
print(count)
"""
    ).stdout
    assert out == "1\n"


def test_manual_builtin_iterator_and_exhaustion(run_source):
    out = run_source(
        """\
val it = [1, 2].__iter__()
print(type(it))
print(it(), it(), it(), it())
print(it.__iter__() is it)
"""
    ).stdout
    assert out == ("<Type 'Iterator'>\n(1, true) (2, true) (null, false) (null, false)\ntrue\n")


def test_manual_user_iterator(run_source):
    out = run_source(
        COUNTDOWN + "val it = Countdown(2).__iter__()\nprint(it(), it(), it())\n"
    ).stdout
    assert out == "(2, true) (1, true) (null, false)\n"


def test_nested_and_repeated_iteration_are_independent(run_source):
    out = run_source(
        COUNTDOWN
        + """\
val counter = Countdown(2)
for a in counter {
    for b in counter {
        print(a, b)
    }
}
print("--")
for x in counter { print(x) }
"""
    ).stdout
    assert out == "2 2\n2 1\n1 2\n1 1\n--\n2\n1\n"


def test_inherited_and_overridden_iter(run_source):
    out = run_source(
        """\
class Base {
    def __iter__() { [1].__iter__() }
}
class Child < Base {
    def __iter__() { [2].__iter__() }
}
for x in Base() { print(x) }
for x in Child() { print(x) }
"""
    ).stdout
    assert out == "1\n2\n"


def test_destructuring_from_user_iterator(run_source):
    out = run_source(
        """\
class Pairs {
    def __iter__() { [(1, 2), (3, 4)].__iter__() }
}
for k, v in Pairs() { print(k + v) }
"""
    ).stdout
    assert out == "3\n7\n"


def test_break_continue_and_break_value(run_source):
    out = run_source(
        COUNTDOWN
        + """\
for x in Countdown(5) {
    if x == 4: continue
    if x == 2: break
    print(x)
}
val result = for x in Countdown(3) {
    if x == 2 { break x * 10 }
}
print(result)
"""
    ).stdout
    assert out == "5\n3\n20\n"


def test_infinite_iterator_can_be_broken(run_source):
    out = run_source(
        """\
class Forever {
    def __iter__() { do: (1, true) }
}
var count = 0
for x in Forever() {
    count = count + 1
    if count == 3 { break }
}
print(count)
"""
    ).stdout
    assert out == "3\n"


def test_for_is_streaming(run_source):
    out = run_source(
        """\
class Probe {
    def __iter__() {
        var i = 0
        do {
            if i < 2 {
                print("next", i)
                i = i + 1
                (i, true)
            } else {
                (null, false)
            }
        }
    }
}
for x in Probe() { print("body", x) }
"""
    ).stdout
    assert out == "next 0\nbody 1\nnext 1\nbody 2\n"


def test_per_iteration_bindings_are_captured(run_source):
    out = run_source(
        COUNTDOWN
        + """\
var functions = []
for x in Countdown(2) {
    functions = functions + [do: x]
}
print(functions[0](), functions[1]())
"""
    ).stdout
    assert out == "2 1\n"


def test_builtin_container_iteration_is_a_snapshot(run_source):
    out = run_source(
        """\
var xs = [1, 2]
for x in xs {
    xs[0] = 9
    print(x)
}
print(xs)
"""
    ).stdout
    assert out == "1\n2\n[9, 2]\n"


def test_helpers_accept_user_iterables(run_source):
    out = run_source(
        COUNTDOWN
        + """\
print(map(Countdown(3)) do(x): x * 2)
print(filter(Countdown(3)) do(x): x > 1)
print(zip(Countdown(2), ["a", "b"]))
print(enumerate(Countdown(2)))
print(sorted(Countdown(3)))
"""
    ).stdout
    assert out == ("[6, 4, 2]\n[3, 2]\n[(2, a), (1, b)]\n[(0, 2), (1, 1)]\n[1, 2, 3]\n")


@pytest.mark.parametrize(
    ("source", "message"),
    [
        ("for x in 1 {}\n", "Type 'Int' is not iterable"),
        (
            "class C {}\nfor x in C() {}\n",
            "Type 'C' is not iterable",
        ),
        (
            "class C {}\nfor x in C {}\n",
            "Class 'C' is not iterable",
        ),
        (
            'import "math"\nfor x in math {}\n',
            "Module 'math' is not iterable",
        ),
        (
            "class C {}\nvar c = C()\nc.__iter__ = 1\nfor x in c {}\n",
            "non-callable '__iter__'",
        ),
        (
            "class C { def __iter__() { 1 } }\nfor x in C() {}\n",
            "must return a callable iterator",
        ),
        (
            "class C { def __iter__() { do: 1 } }\nfor x in C() {}\n",
            "Iterator must return a Tuple",
        ),
        (
            "class C { def __iter__() { do: (1, true, 2) } }\nfor x in C() {}\n",
            "2-element Tuple",
        ),
        (
            "class C { def __iter__() { do: (1, 1) } }\nfor x in C() {}\n",
            "'valid' flag must be a Bool",
        ),
        (
            "class C { def __iter__() { do: (1, null) } }\nfor x in C() {}\n",
            "'valid' flag must be a Bool",
        ),
        (
            "class C { def __iter__(x) { do: (1, true) } }\nfor x in C() {}\n",
            "missing required argument 'x'",
        ),
        (
            "class C {\n    def __iter__() { do: (1, 1 / 0) }\n}\nfor x in C() {}\n",
            "division by zero",
        ),
    ],
)
def test_iterator_errors(source: str, message: str, run_source, caplog):
    with pytest.raises(CompilerError):
        run_source(source)
    assert message in caplog.text


def test_iterator_type_is_per_runtime():
    runtime_a = Runtime()
    runtime_b = Runtime()

    with runtime_a.activate():
        iterator_a = OortIterator([OortInt(1)])
    with runtime_b.activate():
        iterator_b = OortIterator([OortInt(1)])

    assert runtime_a.types.iterator_type is not runtime_b.types.iterator_type
    assert iterator_a.type is runtime_a.types.iterator_type
    assert iterator_b.type is runtime_b.types.iterator_type
    assert runtime_a.types.int_type is not runtime_a.types.iterator_type
