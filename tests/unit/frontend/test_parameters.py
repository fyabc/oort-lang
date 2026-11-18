#! /usr/bin/env python

"""Parameter-list layout validation (before semantic rejection)."""

import pytest

from tests.helpers import get_compiler


def _parse(code: str):
    compiler = get_compiler("NOT_EXIST -t ast")
    return compiler.run_string(code)


@pytest.mark.parametrize(
    "code",
    [
        "def f(**kw) {}",
        "def f(a, **kw) {}",
        "def f(a, **kw, &blk) {}",
        "def f(**kw, &blk) {}",
        "def f(&blk) {}",
        "def f(a, /, b) {}",
        "def f(a, *, b) {}",
        "def f(*args, **kw) {}",
    ],
)
def test_valid_parameter_layouts(code: str):
    _parse(code)


@pytest.mark.parametrize(
    ("code", "message"),
    [
        ("def f(**a, **b) {}", "Variadic keyword parameter redefinition"),
        ("def f(a, **kw, b) {}", "Variadic keyword parameter must come after"),
        (
            "def f(a, **kw, b, &blk) {}",
            "Variadic keyword parameter must come after",
        ),
        ("def f(&a, &b) {}", "Trailing-block parameter redefinition"),
        ("def f(&blk, a) {}", "Trailing block parameter must be the last parameter"),
        ("def f(*, /) {}", "Positional-only parameter flag must come before"),
        ("def f(**kw, *) {}", "Keyword-only parameter flag must come before"),
        ("def f(**kw, *args) {}", "Variadic positional parameter must come before"),
    ],
)
def test_invalid_parameter_layouts(code: str, message: str, caplog: pytest.LogCaptureFixture):
    with pytest.raises(SystemExit):
        _parse(code)
    assert message in caplog.text
