#! /usr/bin/env python

"""Pytest fixtures shared by all tests."""

from collections.abc import Callable

import pytest

from tests.helpers import get_compiler


class RunResult:
    """Result of running an Oort source snippet."""

    def __init__(self, stdout: str, value):
        self.stdout = stdout
        self.value = value


@pytest.fixture
def run_source(capsys: pytest.CaptureFixture) -> Callable[..., RunResult]:
    """Run an Oort source string and return its output and value."""

    def _run(code: str, target: str = "eval") -> RunResult:
        compiler = get_compiler(f"NOT_EXIST -t {target}")
        value = compiler.run_string(code)
        return RunResult(capsys.readouterr().out, value)

    return _run


@pytest.fixture
def compiler_factory() -> Callable[[str], object]:
    return get_compiler
