#! /usr/bin/env python

"""Parser and Pratt-parser tests (precedence, syntax regressions)."""

import pytest

from oort_lang.top_level.compiler import CompilerError
from tests.helpers import get_compiler


def test_operator_precedence(run_source):
    out = run_source(
        """\
print(1 + 2 * 3)
print((1 + 2) * 3)
print(2 ** 3 ** 2)
print(10 // 3 * 3)
print(6 & 3 | 4)
print(not 1 == 2)
print(1 < 2 and 2 < 3)
print(1 in [1, 2], 3 !in [1, 2])
""",
    ).stdout
    assert out == "7\n9\n512\n9\n6\ntrue\ntrue\ntrue true\n"


def test_multiline_expression_inside_parentheses(run_source):
    out = run_source(
        """\
print(
    1
    + 2
)
"""
    ).stdout
    assert out == "3\n"


def test_comment_only_program(run_source):
    result = run_source("# nothing here\n")
    assert result.stdout == ""
    assert result.value is None


def test_double_dot_is_not_an_operator(run_source):
    compiler = get_compiler("NOT_EXIST -t eval")
    with pytest.raises(SystemExit):
        compiler.run_string("a..b\n")


def test_formatted_string_is_rejected(run_source):
    compiler = get_compiler("NOT_EXIST -t eval")
    with pytest.raises(SystemExit):
        compiler.run_string('print(f"hi")\n')


def test_unknown_user_operator_fails_at_runtime(run_source):
    compiler = get_compiler("NOT_EXIST -t eval")
    with pytest.raises(CompilerError):
        compiler.run_string("print(2 +++ 3)\n")


def test_elif_on_separate_lines(run_source):
    out = run_source(
        """\
if false { print(0) }
elif true { print(1) }
else { print(2) }
"""
    ).stdout
    assert out == "1\n"
