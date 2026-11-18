#! /usr/bin/env python

"""Tests for loops and conditional control flow."""

import pytest

from tests.helpers import get_compiler


def test_for_loop(run_source):
    out = run_source("for i in [1, 2, 3]: print(i)\n").stdout
    assert out == "1\n2\n3\n"


def test_for_range(run_source):
    out = run_source("for i in range(3): print(i)\n").stdout
    assert out == "0\n1\n2\n"


def test_for_break_continue(run_source):
    out = run_source(
        """\
for i in [1, 2, 3, 4, 5] {
    if i == 2: continue
    if i == 4: break
    print(i)
}
"""
    ).stdout
    assert out == "1\n3\n"


def test_for_destructuring(run_source):
    out = run_source("for k, v in [(1, 2), (3, 4)]: print(k + v)\n").stdout
    assert out == "3\n7\n"


def test_for_closure_captures_each_iteration(run_source):
    out = run_source(
        """\
var fs = []
for i in [1, 2] {
    fs = fs + [do: i]
}
print(fs[0](), fs[1]())
"""
    ).stdout
    assert out == "1 2\n"


def test_for_over_dict_and_string(run_source):
    out = run_source(
        """\
for k in {: "a": 1, "b": 2 :}: print(k)
for c in "ab": print(c)
"""
    ).stdout
    assert out == "a\nb\na\nb\n"


def test_elif(run_source):
    out = run_source(
        """\
for i in [0, 1, 2, 3] {
    if i == 0: print("zero")
    elif i == 1: print("one")
    elif i == 2: print("two")
    else: print("many")
}
"""
    ).stdout
    assert out == "zero\none\ntwo\nmany\n"


def test_elif_same_line(run_source):
    out = run_source(
        "if false { print(0) } elif false { print(1) } elif true { print(2) } else { print(3) }\n"
    ).stdout
    assert out == "2\n"


def test_break_outside_loop_is_rejected(caplog):
    compiler = get_compiler("NOT_EXIST -t eval")
    with pytest.raises(SystemExit):
        compiler.run_string("break\n")
    assert "Break outside loop." in caplog.text


def test_break_value(run_source):
    out = run_source(
        """\
val a = while true { break 42 }
val b = for i in [1, 2, 3] {
    if i == 2: break i * 10
}
val c = for i in [1] { i }
print(a, b, c)
"""
    ).stdout
    assert out == "42 20 null\n"


def test_break_without_value_returns_null(run_source):
    out = run_source("val a = while true { break }\nprint(a)\n").stdout
    assert out == "null\n"
