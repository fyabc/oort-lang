#! /usr/bin/env python

"""Tests that unimplemented features fail with explicit diagnostics.

The parser accepts a superset of the language. Features that are not
implemented by the dynamic core must be rejected with a clear error rather
than silently doing the wrong thing.
"""

import pytest

from tests.helpers import get_compiler

UNSUPPORTED_CASES = [
    ("macro m {}", "macro system"),
    ("@m(1)", "macro system"),
    ("def f() { yield 1 }", "Generators"),
    ("def f() { await g() }", "Async/await"),
    ("class C[T] {}", "Generic classes"),
    ("enum E { A }", "Enums are only supported in oort-core yet."),
    ("match 1 { _ => 1 }", "match is only supported in oort-core yet."),
    ("def f { $0 }", "Anonymous parameters"),
    ("@[]", "Compiler attributes"),
    ('print(f"{1}")', "Formatted string"),
    ("def class.f: 1", "Class methods must be defined inside a class."),
    ("class A.B {}", "Namespaced classes are not implemented yet."),
    (
        "class A { def __init__ { super(1) } }",
        "Explicit super(...) calls are not supported",
    ),
    ('def operator "+"(a) {}', "Operator methods must be defined inside a class"),
    ('class C { def operator "foo"(a) {} }', "Invalid operator symbol"),
    ('class C { def operator "*"() {} }', "cannot be defined as a unary operator"),
    ('class C { def operator "is"(a) {} }', "cannot be overloaded"),
    ('class C { def operator "=>"(a) {} }', "cannot be overloaded"),
    ('class C { def class.operator "+"(a) {} }', "Class operator methods"),
]


@pytest.mark.parametrize("code, message", UNSUPPORTED_CASES)
def test_unsupported_feature(code: str, message: str, caplog):
    compiler = get_compiler("NOT_EXIST -t eval")
    with pytest.raises(SystemExit):
        compiler.run_string(code)
    assert message in caplog.text


def test_break_and_continue_inside_for_are_allowed(run_source):
    out = run_source(
        """\
for i in [1, 2, 3] {
    if i == 2: continue
    if i == 3: break
    print(i)
}
"""
    ).stdout
    assert out == "1\n"


def test_break_outside_loop_is_rejected(caplog):
    compiler = get_compiler("NOT_EXIST -t eval")
    with pytest.raises(SystemExit):
        compiler.run_string("break\n")
    assert "Break outside loop." in caplog.text
