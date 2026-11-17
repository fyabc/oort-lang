#! /usr/bin/env python

"""Tests for the `oort-object` dynamic object model (OP 0007)."""

import pytest

from tests.helpers import get_compiler


@pytest.mark.parametrize("keyword", ["var", "val"])
def test_class_body_variable_is_rejected(keyword: str, caplog: pytest.LogCaptureFixture):
    source = f"""\
class C {{
    {keyword} x = 1
}}
"""
    compiler = get_compiler("NOT_EXIST -t eval")
    with pytest.raises(SystemExit):
        compiler.run_string(source)
    assert "Class-body variable declarations are not supported" in caplog.text
    assert "assign instance fields in `__init__`" in caplog.text


def test_instance_fields_are_created_in_init(capsys: pytest.CaptureFixture):
    source = """\
class Counter {
    def __init__ {
        this.n = 0
    }

    def increment {
        this.n = this.n + 1
        this
    }
}

val c = Counter()
c.increment()
print(c.n)
"""
    compiler = get_compiler("NOT_EXIST -t eval")
    compiler.run_string(source)
    assert capsys.readouterr().out == "1\n"
