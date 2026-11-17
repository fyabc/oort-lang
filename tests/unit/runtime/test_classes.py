#! /usr/bin/env python

import pytest

from tests.helpers import get_compiler


def test_class_repr(capsys: pytest.CaptureFixture):
    test_string = """\
class C {}
var c = C()
print(C)
"""
    compiler = get_compiler("NOT_EXIST -t eval")
    compiler.run_string(test_string)
    captured = capsys.readouterr()
    assert captured.out == "<Type 'C'>\n"


def test_class_obj_repr(capsys: pytest.CaptureFixture):
    test_string = """\
class C {}
var c = C()
print(c)
"""
    compiler = get_compiler("NOT_EXIST -t eval")
    compiler.run_string(test_string)
    captured = capsys.readouterr()
    assert captured.out.startswith("<C object at 0x")


def test_method(capsys: pytest.CaptureFixture):
    test_string = """\
class C {
    def f: 1
}
print(C.f)
print(C().f)
"""
    compiler = get_compiler("NOT_EXIST -t eval")
    compiler.run_string(test_string)
    captured = capsys.readouterr()
    out_lines = captured.out.split("\n")
    assert out_lines[0].startswith("<Function f at 0x")
    assert out_lines[1].startswith("<Bound method C.f of <C object at 0x")


def test_class_this(capsys: pytest.CaptureFixture):
    test_string = """\
class C {
    def f: this
}
var c = C()
print(c.f() == c)
"""
    compiler = get_compiler("NOT_EXIST -t eval")
    compiler.run_string(test_string)
    captured = capsys.readouterr()
    assert captured.out == "true\n"


def test_class_initializer(capsys: pytest.CaptureFixture):
    test_string = """\
class Rect {
    def __init__(x, y) {
        this.x = x
        this.y = y
    }

    def area: this.x * this.y
}
Rect(3, 4).area()
"""
    compiler = get_compiler("NOT_EXIST -t eval")
    result = compiler.run_string(test_string)
    assert result == 12


def test_class_method(capsys: pytest.CaptureFixture):
    test_string = """\
class C {
    def class.f: this
}
print(C.f())
print(C().f())
"""
    compiler = get_compiler("NOT_EXIST -t eval")
    compiler.run_string(test_string)
    captured = capsys.readouterr()
    assert captured.out == "<Type 'C'>\n<Type 'C'>\n"


def test_class_inheritance(capsys: pytest.CaptureFixture):
    test_string = """\
class B {
    def f: 42
    def g: 10
}
class D < B {
    def f: super.f() + this.g()
}
print(B().f())
print(D().f())
"""
    compiler = get_compiler("NOT_EXIST -t eval")
    compiler.run_string(test_string)
    captured = capsys.readouterr()
    assert captured.out == "42\n52\n"


if __name__ == "__main__":
    pytest.main([__file__])
