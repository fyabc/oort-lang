#! /usr/bin/env python

"""Native math and string standard-library modules."""

import pytest

from oort_lang.driver.compiler import CompilerError


def test_math_constants_and_rounding(run_source):
    out = run_source(
        """\
import "math"
print(math.pi > 3.14, math.e > 2.71, math.tau > 6.28)
print(math.floor(2.9), math.ceil(2.1), math.trunc(-2.9))
"""
    ).stdout
    assert out == "true true true\n2 3 -2\n"


def test_math_functions(run_source):
    out = run_source(
        """\
import "math"
print(math.sqrt(9), math.pow(2, 3))
print(math.log(1), math.log(100, 10))
print(math.sin(0), math.atan2(1, 1) < 0.79)
"""
    ).stdout
    assert out == "3.0 8.0\n0.0 2.0\n0.0 true\n"


@pytest.mark.parametrize(
    ("source", "message"),
    [
        ('import "math"\nmath.sqrt(-1)\n', "math domain error"),
        ('import "math"\nmath.sqrt("x")\n', "expect Int or Float"),
        ('import "math"\nmath.sqrt(true)\n', "expect Int or Float"),
    ],
)
def test_math_errors(source: str, message: str, run_source, caplog):
    with pytest.raises(CompilerError):
        run_source(source)
    assert message in caplog.text


def test_string_module_functions(run_source):
    out = run_source(
        """\
import "string"
print(string.split("a,b,c", ","))
print(string.split(" a  b "))
print(string.join(["a", "b"], "-"))
print(string.join(["a", "b"]))
print(string.upper("aä"), string.lower("AÄ"))
print(string.strip("  x  "), string.strip("xxaxx", "x"))
print(string.startswith("oort", "oo"), string.endswith("oort", "rt"))
print(string.find("abcabc", "bc"), string.find("abc", "z"))
print(string.replace("a-b-a", "a", "x"))
"""
    ).stdout
    assert out == ("[a, b, c]\n[a, b]\na-b\nab\nAÄ aä\nx a\ntrue true\n1 -1\nx-b-x\n")


@pytest.mark.parametrize(
    ("source", "message"),
    [
        ('import "string"\nstring.upper(1)\n', "expect String values"),
        ('import "string"\nstring.join([1], "-")\n', "List or Tuple of strings"),
        ('import "string"\nstring.join(["a"], 1)\n', "expect String values"),
    ],
)
def test_string_module_errors(source: str, message: str, run_source, caplog):
    with pytest.raises(CompilerError):
        run_source(source)
    assert message in caplog.text
