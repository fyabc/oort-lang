#! /usr/bin/env python

"""Unified value/key equality protocol (OP 0016)."""


def test_bool_and_int_are_distinct_at_every_depth(run_source):
    out = run_source(
        """\
print([true] == [1], [1] == [true])
print(true in [1], 1 in [true])
print([true] in [[1]], [[true]] == [[1]])
print((true,) == (1,))
print({: "k": [true] :} == {: "k": [1] :})
print({. (true,) .} == {. (1,) .})
"""
    ).stdout
    assert out == "false false\nfalse false\nfalse false\nfalse\nfalse\nfalse\n"


def test_int_and_float_compare_as_numbers(run_source):
    out = run_source(
        """\
print([1] == [1.0], 1 in [1.0])
print({: "k": 1 :} == {: "k": 1.0 :})
"""
    ).stdout
    assert out == "true true\ntrue\n"


def test_dict_keys_and_membership_use_key_equality(run_source):
    out = run_source(
        """\
print({: true: "x" :} == {: 1: "x" :})
print(1 in {: true: "x" :})
print({: true: "x" :}[true])
print({: "a": [1] :} == {: "a": [1.0] :})
print({: "a": [true] :} == {: "a": [1] :})
"""
    ).stdout
    assert out == "false\nfalse\nx\ntrue\nfalse\n"


def test_set_equality_and_algebra_use_key_equality(run_source):
    out = run_source(
        """\
print({. true .} == {. 1 .})
print(true in {. 1 .})
print({. true .} & {. 1 .})
val union = {. true .} | {. 1 .}
print(len(union), true in union, 1 in union)
print(len({. true .} ^ {. 1 .}))
print(len({. true .} - {. 1 .}))
"""
    ).stdout
    assert out == "false\nfalse\n{.}\n2 true true\n2\n1\n"


def test_user_equality_applies_to_values_but_not_keys(run_source):
    out = run_source(
        """\
class Point {
    def __init__(x) { this.x = x }
    def operator "=="(other): this.x == other.x
}
print([Point(1)] == [Point(1)])
print(Point(1) in [Point(1)])
print({: "a": Point(1) :} == {: "a": Point(1) :})
print({. Point(1) .} == {. Point(1) .})
"""
    ).stdout
    assert out == "true\ntrue\ntrue\nfalse\n"


def test_sequence_equality_is_type_sensitive(run_source):
    out = run_source(
        """\
print([1] == (1,))
print((1,) == [1])
print(1 != 1.0, 1 != true)
"""
    ).stdout
    assert out == "false\nfalse\nfalse true\n"


def test_cyclic_containers_compare_with_pair_memo(run_source):
    out = run_source(
        """\
var a = [null]
a[0] = a
var b = [null]
b[0] = b
var c = [null]
c[0] = [c]
print(a == b)
print(a == c)
print(a == a)
"""
    ).stdout
    assert out == "true\ntrue\ntrue\n"
