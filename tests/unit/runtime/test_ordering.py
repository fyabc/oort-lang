#! /usr/bin/env python

"""Ordering protocol for built-in containers and sequence value semantics."""

import pytest

from oort_lang.driver.compiler import CompilerError
from tests.helpers import get_compiler


def test_sequences_order_lexicographically(run_source):
    out = run_source(
        """\
print([1, 2] < [1, 3], [1, 2] <= [1, 2], [1, 2] > [1])
print((1, 2) < (1, 3), (2,) > (1, 9))
print([[1, 2]] < [[1, 3]])
print([1] < [1, 0], [1, 0] > [1])
"""
    ).stdout
    assert out == "true true true\ntrue true\ntrue\ntrue true\n"


def test_sequence_ordering_uses_oort_value_equality(run_source):
    out = run_source(
        """\
print([1] < [1.0])
print([1, 2] <= [1.0, 2.0])
print(["a", "b"] < ["a", "c"])
print([null] <= [null])
"""
    ).stdout
    assert out == "false\ntrue\ntrue\ntrue\n"


def test_sequence_ordering_rejects_mismatched_container_kinds(caplog):
    compiler = get_compiler("NOT_EXIST -t eval")
    with pytest.raises(CompilerError):
        compiler.run_string("print([1] < (1,))\n")
    assert "Cannot order a List and a Tuple" in caplog.text


def test_sequence_ordering_requires_orderable_elements(caplog):
    compiler = get_compiler("NOT_EXIST -t eval")
    with pytest.raises(CompilerError):
        compiler.run_string("print([true] < [2])\n")
    assert "Type 'Bool' does not support operator '<'" in caplog.text


def test_container_error_position_is_not_builtin(caplog):
    compiler = get_compiler("NOT_EXIST -t eval")
    with pytest.raises(CompilerError):
        compiler.run_string("print([1] < [true])\n")
    assert "<builtin>" not in caplog.text
    assert "<string>:1:" in caplog.text


def test_dicts_have_no_ordering_and_sets_use_subset(run_source, caplog):
    out = run_source(
        """\
print({. 1 .} <= {. true, 1 .})
print({. true .} <= {. 1 .})
print({. 1 .} < {. 1, 2 .})
"""
    ).stdout
    assert out == "true\nfalse\ntrue\n"

    compiler = get_compiler("NOT_EXIST -t eval")
    with pytest.raises(CompilerError):
        compiler.run_string('print({: "a": 1 :} < {: "b": 2 :})\n')
    assert "Type 'Dict' does not support operator '<'" in caplog.text


def test_sequence_concat_and_repeat_are_shallow(run_source):
    out = run_source(
        """\
val inner = [1]
val copy = [inner] + []
copy[0][0] = 2
print(inner[0])
val outer = [inner] * 3
outer[0][0] = 9
print(outer[1][0], outer[2][0])
"""
    ).stdout
    assert out == "2\n9 9\n"


def test_sequence_concat_and_repeat_kinds(run_source):
    out = run_source(
        """\
print([1, 2] + [3])
print((1,) + (2,))
print([1] * 2, (1,) * 2)
"""
    ).stdout
    assert out == "[1, 2, 3]\n(1, 2)\n[1, 1] (1, 1)\n"
