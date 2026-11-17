#! /usr/bin/env python

"""Builtin function and type tests."""


def test_print(run_source):
    assert run_source('print("a", 1, true, null)\n').stdout == "a 1 true null\n"


def test_len(run_source):
    out = run_source('print(len([1, 2]), len("abc"), len({: "a": 1 :}), len((1, 2)))\n').stdout
    assert out == "2 3 1 2\n"


def test_range(run_source):
    out = run_source("print(range(3), range(1, 4), range(0, 6, 2))\n").stdout
    assert out == "[0, 1, 2] [1, 2, 3] [0, 2, 4]\n"


def test_conversions(run_source):
    out = run_source(
        """\
print(int("42"), float("1.5"), str(7), bool(0), bool(1))
"""
    ).stdout
    assert out == "42 1.5 7 false true\n"


def test_type(run_source):
    out = run_source('print(type(1), type("a"), type([1]), type({. 1 .}))\n').stdout
    assert out == "<Type 'Int'> <Type 'String'> <Type 'List'> <Type 'Set'>\n"


def test_clock_returns_float(run_source):
    result = run_source("clock()\n")
    assert isinstance(result.value, float)
