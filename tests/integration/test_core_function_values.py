#! /usr/bin/env python

"""Typed core function values: named functions as first-class values (B2)."""

import pytest

from oort_lang.driver.compiler import CompilerError
from tests.helpers import get_compiler

FUNCTION_VALUES = """#lang oort-core

def inc(x: Int) -> Int { x + 1 }
def dec(x: Int) -> Int { x - 1 }

def apply(f: (Int) -> Int, x: Int) -> Int { f(x) }
def pick(flag: Bool) -> (Int) -> Int { if flag { inc } else { dec } }
def local() -> Int { val f: (Int) -> Int = inc; f(10) }

def sum_apply(fs: List[(Int) -> Int], x: Int) -> Int {
    var total: Int = 0
    for f in fs { total = total + f(x) }
    total
}

print(apply(inc, 1), apply(dec, 1))
print(apply(pick(true), 2), apply(pick(false), 2))
print(local())
print(sum_apply([inc, dec], 10))
"""

FUNCTION_VALUES_OUTPUT = "2 0\n3 1\n11\n20\n"


@pytest.mark.parametrize("target", ["eval", "vm", "tvm"])
def test_named_function_values_match_across_targets(capsys, target):
    compiler = get_compiler(["NOT_EXIST", "-t", target])
    compiler.run_string(FUNCTION_VALUES)
    assert capsys.readouterr().out == FUNCTION_VALUES_OUTPUT


@pytest.mark.parametrize(
    ("source", "message"),
    [
        (
            "def g() -> Int { val f = do(x: Int) -> Int { x }; f(1) }\nprint(g())",
            "Typed HIR backend does not support lambdas.",
        ),
        (
            "def eq(f: (Int) -> Int, g: (Int) -> Int) -> Bool { f == g }\nprint(true)",
            "Operator '==' requires two numbers, two Bool or two String operands",
        ),
        (
            "def inc(x: Int) -> Int { x + 1 }\n"
            "def apply(f: (Int) -> Int, x: Int) -> Int { f(x) }\n"
            "print(apply(inc, true))",
            "Expected Int, got Bool.",
        ),
    ],
)
def test_function_value_errors(caplog, source, message):
    compiler = get_compiler("NOT_EXIST -t tvm")
    with pytest.raises((SystemExit, CompilerError)):
        compiler.run_string("#lang oort-core\n" + source)
    assert message in caplog.text
