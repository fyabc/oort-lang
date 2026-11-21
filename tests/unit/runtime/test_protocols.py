#! /usr/bin/env python

"""User-defined subscript and missing-attribute protocols."""

import pytest

from oort_lang.driver.compiler import CompilerError
from tests.helpers import get_compiler


def test_subscript_get_set_and_augmented_assignment(run_source):
    out = run_source(
        """\
class Bag {
    def __init__() {
        this.items = {: "a": 1, "b": 2 :}
    }
    def operator "[]"(key) { this.items[key] }
    def operator "[]="(key, value) { this.items[key] = value }
}
val b = Bag()
print(b["a"])
b["c"] = 3
b["a"] += 10
print(b["a"], b["c"])
"""
    ).stdout
    assert out == "1\n11 3\n"


def test_subscript_receives_tuple_and_slice_objects(run_source):
    out = run_source(
        """\
class Echo {
    def operator "[]"(key) { type(key) }
}
val e = Echo()
print(e[1, 2])
print(e[1:3])
"""
    ).stdout
    assert out == "<Type 'Tuple'>\n<Type 'Slice'>\n"


def test_user_class_without_subscript_operator_is_rejected():
    compiler = get_compiler("NOT_EXIST -t eval")
    with pytest.raises(CompilerError):
        compiler.run_string("class C {}\nprint(C()[0])\n")


def test_getter_without_setter_is_rejected(caplog):
    compiler = get_compiler("NOT_EXIST -t eval")
    with pytest.raises(CompilerError):
        compiler.run_string(
            """\
class C {
    def operator "[]"(key) { key }
}
C()[0] = 1
"""
        )
    assert "does not support subscript assignment" in caplog.text


def test_extension_subscript_operator(run_source):
    out = run_source(
        """\
class C { def __init__ { this.v = 5 } }
def C.operator "[]"(i) { this.v + i }
print(C()[2])
"""
    ).stdout
    assert out == "7\n"


def test_missing_attribute_falls_back_to_on_missing(run_source):
    out = run_source(
        """\
class C {
    def __init__ { this.x = 1 }
    def f() { 2 }
    def on_missing(name) { "missing:" + name }
}
val c = C()
print(c.x, c.f(), c.unknown)
"""
    ).stdout
    assert out == "1 2 missing:unknown\n"


def test_missing_hook_does_not_reenter_for_the_same_receiver(caplog):
    compiler = get_compiler("NOT_EXIST -t eval")
    with pytest.raises(CompilerError):
        compiler.run_string(
            """\
class C {
    def on_missing(name) { this.other }
}
print(C().x)
"""
        )
    assert "has no attribute 'other'" in caplog.text


def test_builtin_subscripts_are_unchanged(run_source):
    out = run_source(
        """\
print([1, 2][1], "abc"[0], {: "k": 3 :}["k"], (4, 5)[1])
"""
    ).stdout
    assert out == "2 a 3 5\n"
