#! /usr/bin/env python

"""Operator overloading and native operator methods."""

import pytest

from oort_lang.top_level.compiler import CompilerError
from tests.helpers import get_compiler


def test_user_defined_binary_operator(run_source):
    out = run_source(
        """\
class Vec {
    def __init__(x) { this.x = x }
    def operator "+"(other) { Vec(this.x + other.x) }
}
val result = Vec(2) + Vec(3)
print(result.x)
"""
    ).stdout
    assert out == "5\n"


def test_user_defined_unary_operator(run_source):
    out = run_source(
        """\
class Num {
    def __init__(v) { this.v = v }
    def operator "-"() { Num(0 - this.v) }
    def operator "~"() { Num(0 - this.v - 1) }
}
print((-Num(5)).v)
print((~Num(5)).v)
"""
    ).stdout
    assert out == "-5\n-6\n"


def test_unary_and_binary_operator_can_share_a_symbol(run_source):
    out = run_source(
        """\
class Num {
    def operator "-"() { 1 }
    def operator "-"(other) { 2 }
}
val n = Num()
print(-n, n - n)
"""
    ).stdout
    assert out == "1 2\n"


def test_operator_equality_and_derived_inequality(run_source):
    out = run_source(
        """\
class Point {
    def __init__(x) { this.x = x }
    def operator "=="(other) { this.x == other.x }
}
print(Point(1) == Point(1))
print(Point(1) != Point(2))
"""
    ).stdout
    assert out == "true\ntrue\n"


def test_explicit_inequality_overrides_default(run_source):
    out = run_source(
        """\
class C {
    def operator "=="(other) { false }
    def operator "!="(other) { true }
}
print(C() == C(), C() != C())
"""
    ).stdout
    assert out == "false true\n"


def test_operator_inheritance(run_source):
    out = run_source(
        """\
class Base {
    def operator "+"(other) { 42 }
}
class Derived < Base {}
print(Derived() + 1)
"""
    ).stdout
    assert out == "42\n"


def test_membership_dispatches_to_container(run_source):
    out = run_source(
        """\
class Bag {
    def __init__() { this.items = [1, 2, 3] }
    def operator "in"(item) { item in this.items }
}
val bag = Bag()
print(1 in bag)
print(9 !in bag)
"""
    ).stdout
    assert out == "true\ntrue\n"


def test_identity_is_not_overloadable(run_source):
    out = run_source(
        """\
val a = [1]
val b = a
print(a is b, a is [1])
"""
    ).stdout
    assert out == "true false\n"


def test_unsupported_operator_operands_raise_runtime_error():
    compiler = get_compiler("NOT_EXIST -t eval")
    with pytest.raises(CompilerError):
        compiler.run_string(
            """\
class C {}
C() + C()
"""
        )
