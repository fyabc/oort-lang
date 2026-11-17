#! /usr/bin/env python

"""Tests for list / tuple / dict / set literals and subscripting."""


def test_collection_literals(run_source):
    out = run_source(
        """\
print((1, 2))
print({: "a": 1 :})
print({. 1, 2 .})
print([])
print((1,))
""",
    ).stdout
    assert out == "(1, 2)\n{a: 1}\n{1, 2}\n[]\n(1,)\n"


def test_collection_subscript(run_source):
    out = run_source(
        """\
print([1, 2, 3][1])
print((1, 2, 3)[2])
print("abc"[1])
print({: "a": 1 :}["a"])
print(2 in {. 1, 2 .})
""",
    ).stdout
    assert out == "2\n3\nb\n1\ntrue\n"


def test_slice(run_source):
    out = run_source(
        """\
print([1, 2, 3, 4][1:3])
print("hello"[1:])
print([0, 1, 2, 3, 4][::2])
print([0, 1, 2, 3, 4][1::2])
""",
    ).stdout
    assert out == "[2, 3]\nello\n[0, 2, 4]\n[1, 3]\n"


def test_nested_collections(run_source):
    out = run_source('print({: "xs": [1, 2] :}["xs"][1])\n').stdout
    assert out == "2\n"
