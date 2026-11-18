#! /usr/bin/env python

"""Default, keyword, variadic and block parameter binding (OP 0011)."""

import pytest

from oort_lang.top_level.compiler import CompilerError
from tests.helpers import get_compiler


def test_default_arguments(run_source):
    out = run_source(
        """\
def f(a, b = 2): b
print(f(1), f(1, 3), f(1, b = 3), f(a = 1, b = 3))
"""
    ).stdout
    assert out == "2 3 3 3\n"


def test_default_can_reference_earlier_parameter(run_source):
    out = run_source(
        """\
def f(a, b = a + 1): b
print(f(3), f(3, 10))
"""
    ).stdout
    assert out == "4 10\n"


def test_default_is_evaluated_per_call(run_source):
    out = run_source(
        """\
def f(m = {:}) {
    m["x"] = 1
    len(m)
}
print(f(), f())
"""
    ).stdout
    assert out == "1 1\n"


def test_default_is_not_evaluated_when_argument_is_given(run_source):
    out = run_source(
        """\
var calls = 0
def mark {
    calls = calls + 1
    1
}
def f(x = mark()) { x }
print(f(5), calls)
print(f(), calls)
"""
    ).stdout
    assert out == "5 0\n1 1\n"


def test_keyword_only_parameters(run_source):
    out = run_source(
        """\
def f(a, *, b, c = 3): b + c
print(f(1, b = 2), f(1, b = 2, c = 5))
"""
    ).stdout
    assert out == "5 7\n"


def test_keyword_only_required_after_default(run_source):
    out = run_source(
        """\
def f(*, a = 1, b): a + b
print(f(b = 2))
"""
    ).stdout
    assert out == "3\n"


def test_positional_only_parameters(run_source):
    out = run_source(
        """\
def f(a, b = 2, /, c = 3): a + b + c
print(f(1), f(1, 5), f(1, 5, c = 4))
"""
    ).stdout
    assert out == "6 9 10\n"


def test_positional_only_keyword_can_be_captured_by_kwargs(run_source):
    out = run_source(
        """\
def f(x = 0, /, **kwargs) { print(x, kwargs) }
f(x = 2)
f(1, x = 2)
"""
    ).stdout
    assert out == "0 {: x: 2 :}\n1 {: x: 2 :}\n"


def test_varargs_and_kwargs(run_source):
    out = run_source(
        """\
def f(a, *args, **kwargs) { print(a, args, kwargs) }
f(1, 2, 3, x = 4)
f(1)
"""
    ).stdout
    assert out == "1 (2, 3) {: x: 4 :}\n1 () {:}\n"


def test_block_parameter(run_source):
    out = run_source(
        """\
def run(&block) {
    if block != null: block()
}
run do { print("block") }
run()
run(block = do { print("keyword") })
"""
    ).stdout
    assert out == "block\nkeyword\n"


def test_trailing_block_without_block_parameter_is_positional(run_source):
    out = run_source(
        """\
def apply(x, f) { f(x) }
print(apply(2) do(x): x + 1)
"""
    ).stdout
    assert out == "3\n"


def test_class_initializer_defaults_and_keywords(run_source):
    out = run_source(
        """\
class C {
    def __init__(a, b = 2) {
        this.a = a
        this.b = b
    }
}
val c = C(1, b = 3)
print(c.a, c.b)
"""
    ).stdout
    assert out == "1 3\n"


def test_super_initializer_keywords(run_source):
    out = run_source(
        """\
class A {
    def __init__(x, y = 2) {
        this.x = x
        this.y = y
    }
}
class B < A {
    def __init__ { super.__init__(5, y = 7) }
}
val b = B()
print(b.x, b.y)
"""
    ).stdout
    assert out == "5 7\n"


def test_lambda_defaults_and_keywords(run_source):
    out = run_source(
        """\
val f = do(a, b = 2): a + b
print(f(1), f(1, b = 3))
"""
    ).stdout
    assert out == "3 4\n"


@pytest.mark.parametrize(
    ("source", "message"),
    [
        ("def f(a, b) {}\nf(1)\n", "missing required argument 'b'"),
        ("def f(a) {}\nf(1, 2)\n", "takes 1 positional arguments but 2 were given"),
        ("def f(a) {}\nf(x = 1)\n", "unexpected keyword argument 'x'"),
        ("def f(a) {}\nf(1, a = 2)\n", "multiple values for argument 'a'"),
        ("def f(x = 0, /) {}\nf(x = 2)\n", "argument 'x' is positional-only"),
        ("class C {}\nC(1)\n", "takes 0 arguments but 1 were given"),
        ("val f = do: $0\nf(x = 1)\n", "does not accept keyword arguments"),
        (
            "print(x = 1)\n",
            "Built-in function 'print' does not accept keyword arguments",
        ),
        (
            "def f(&block) {}\nf(block = do {}) do {}\n",
            "multiple values for argument 'block'",
        ),
    ],
)
def test_binding_errors(source: str, message: str, caplog: pytest.LogCaptureFixture):
    compiler = get_compiler("NOT_EXIST -t eval")
    with pytest.raises(CompilerError):
        compiler.run_string(source)
    assert message in caplog.text


@pytest.mark.parametrize(
    ("source", "message"),
    [
        ("def f(a = 1, b) {}\n", "Parameter without a default"),
        ("def f(*) {}\n", "Bare '*' must be followed"),
        ("def f(a = 1, /, b) {}\n", "Parameter without a default"),
        ("def f(a = b, b = 1) {}\n", "cannot reference later parameter 'b'"),
        ("def f(a, a) {}\n", "Duplicate parameter name 'a'"),
        (
            'class C { def operator "+"(other = 1) { other } }\n',
            "Operator methods cannot use default",
        ),
    ],
)
def test_definition_errors(source: str, message: str, caplog: pytest.LogCaptureFixture):
    compiler = get_compiler("NOT_EXIST -t eval")
    with pytest.raises(SystemExit):
        compiler.run_string(source)
    assert message in caplog.text


@pytest.mark.parametrize(
    ("source", "message"),
    [
        ("def f(a) {}\nf(a = 1, a = 2)\n", "is given more than once"),
        ("def f(a) {}\nf(a = 1, 2)\n", "Positional argument follows keyword argument"),
    ],
)
def test_call_layout_errors(source: str, message: str, caplog: pytest.LogCaptureFixture):
    compiler = get_compiler("NOT_EXIST -t eval")
    with pytest.raises(SystemExit):
        compiler.run_string(source)
    assert message in caplog.text


def test_trailing_block_after_keyword_uses_next_positional(run_source):
    out = run_source(
        """\
def f(a, b) { b() }
print(f(a = 1) do { 2 })
"""
    ).stdout
    assert out == "2\n"
