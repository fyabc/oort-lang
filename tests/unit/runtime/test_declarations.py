#! /usr/bin/env python

"""Tests for variable declarations, assignment and scoping."""

import pytest

from oort_lang.driver.compiler import CompilerError
from tests.helpers import get_compiler


def test_multiple_declaration_and_swap(run_source):
    out = run_source(
        """\
var a, b = 1, 2
a, b = b, a
print(a, b)
"""
    ).stdout
    assert out == "2 1\n"


def test_unpack_from_list(run_source):
    out = run_source(
        """\
var a, b = [3, 4]
print(a, b)
"""
    ).stdout
    assert out == "3 4\n"


def test_val_is_immutable(run_source):
    compiler = get_compiler("NOT_EXIST -t eval")
    with pytest.raises(CompilerError):
        compiler.run_string("val a = 1\na = 2\n")


def test_unpack_arity_mismatch(run_source):
    compiler = get_compiler("NOT_EXIST -t eval")
    with pytest.raises(CompilerError):
        compiler.run_string("var a, b = 1, 2, 3\n")
