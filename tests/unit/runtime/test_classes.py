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


def test_inherited_initializer(run_source):
    out = run_source(
        """\
class B {
    def __init__(x) { this.x = x }
    def f: this.x
}
class D < B {}
print(D(5).f())
"""
    ).stdout
    assert out == "5\n"


def test_super_in_inherited_method(run_source):
    out = run_source(
        """\
class A { def f: 1 }
class B < A {
    def g: super.f() + 10
}
class C < B {}
print(C().g())
"""
    ).stdout
    assert out == "11\n"


def test_super_chain(run_source):
    out = run_source(
        """\
class A { def f: 0 }
class B < A { def f: super.f() + 1 }
class C < B { def f: super.f() + 10 }
print(C().f())
"""
    ).stdout
    assert out == "11\n"


def test_diamond_inheritance(run_source):
    out = run_source(
        """\
class A { def f: 1 }
class B < A {}
class C < A {}
class D < B, C {}
print(B().f(), C().f(), D().f())
"""
    ).stdout
    assert out == "1 1 1\n"


if __name__ == "__main__":
    pytest.main([__file__])
