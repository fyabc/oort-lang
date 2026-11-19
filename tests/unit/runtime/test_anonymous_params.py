#! /usr/bin/env python

"""Tests for anonymous lambda parameters (`$0`, `$1`, ...)."""

import pytest

from oort_lang.driver.compiler import CompilerError
from tests.helpers import get_compiler


def test_unary_anonymous_lambda(run_source):
    out = run_source("val double = do: $0 * 2\nprint(double(3))\n").stdout
    assert out == "6\n"


def test_binary_anonymous_lambda(run_source):
    out = run_source("val add = do: $0 + $1\nprint(add(2, 3))\n").stdout
    assert out == "5\n"


def test_anonymous_block_lambda(run_source):
    out = run_source("val f = do { $0 + 1 }\nprint(f(4))\n").stdout
    assert out == "5\n"


def test_anonymous_trailing_lambda(run_source):
    out = run_source(
        """\
def apply(f) { f(3) }
print(apply(do: $0 * 2))
"""
    ).stdout
    assert out == "6\n"


def test_gap_in_indices_binds_all_arguments(run_source):
    out = run_source("val second = do: $1\nprint(second(10, 20))\n").stdout
    assert out == "20\n"


def test_explicit_lambda_still_captures_named_locals(run_source):
    out = run_source(
        """\
def make() {
    val offset = 3
    do(x): x + offset
}
print(make()(4))
"""
    ).stdout
    assert out == "7\n"


def test_anonymous_parameters_scope_to_nearest_lambda(run_source):
    out = run_source(
        """\
val outer = do: do: $0 * 2
val inner = outer()
print(inner(4))
"""
    ).stdout
    assert out == "8\n"


@pytest.mark.parametrize(
    ("source", "message"),
    [
        ("def f { $0 }\n", "Anonymous parameters are only allowed in lambdas."),
        ("do(x): $0\n", "cannot be combined with an explicit parameter list"),
        ("do(): $0\n", "cannot be combined with an explicit parameter list"),
        (
            "val f = do: $0 + (do(x): $0)(10)\n",
            "cannot be combined with an explicit parameter list",
        ),
        (
            "val f = do { val inner = do(x): $1\n inner }\n",
            "cannot be combined with an explicit parameter list",
        ),
        ("$0\n", "Anonymous parameters are only allowed inside a lambda."),
        ("var $0 = 1\n", "Anonymous parameter names cannot be declared explicitly."),
        ("def f($0): $0\n", "Anonymous parameter names cannot be declared explicitly."),
    ],
)
def test_anonymous_parameter_misuse(source: str, message: str, caplog: pytest.LogCaptureFixture):
    compiler = get_compiler("NOT_EXIST -t eval")
    with pytest.raises(SystemExit):
        compiler.run_string(source)
    assert message in caplog.text


def test_anonymous_lambda_arity_is_enforced():
    compiler = get_compiler("NOT_EXIST -t eval")
    with pytest.raises(CompilerError):
        compiler.run_string("val add = do: $0 + $1\nadd(1)\n")
