#! /usr/bin/env python

"""Extension methods defined outside the target class (OP 0014)."""

import pytest

from oort_lang.driver.compiler import CompilerError

COUNTER = """\
class Counter {
    def __init__(n) { this.n = n }
    def inc { this.n = this.n + 1 }
}
def Counter.bump {
    this.inc()
    this.inc()
    this.n
}
"""


def test_basic_extension_method(run_source):
    out = run_source(COUNTER + "var c = Counter(1)\nprint(c.bump(), c.n)\n").stdout
    assert out == "3 3\n"


def test_extension_parameters_defaults_and_block(run_source):
    out = run_source(
        """\
def Int.scale(factor = 2): this * factor
print(3.scale(), 3.scale(4))
def Int.apply(&block): block(this)
print(3.apply() do(x): x + 1)
"""
    ).stdout
    assert out == "6 12\n4\n"


def test_extension_on_builtin_types(run_source):
    out = run_source(
        """\
def List.total {
    var sum = 0
    for x in this { sum = sum + x }
    sum
}
def String.shout: this + "!"
def Int.twice: this * 2
print([1, 2, 3].total())
print("hi".shout())
print(5.twice())
"""
    ).stdout
    assert out == "6\nhi!\n10\n"


def test_member_field_and_class_method_take_priority(run_source):
    out = run_source(
        """\
class Greeter { def greet: "member" }
def Greeter.greet: "extension"
print(Greeter().greet())

class Box {}
def Box.value: "extension"
var box = Box()
box.value = "field"
print(box.value)

class Maker { def class.make: "class method" }
def Maker.make: "extension"
print(Maker().make())
"""
    ).stdout
    assert out == "member\nfield\nclass method\n"


def test_inherited_member_takes_priority(run_source):
    out = run_source(
        """\
class Base { def greet: "base member" }
class Child < Base {}
def Child.greet: "extension"
print(Child().greet())
"""
    ).stdout
    assert out == "base member\n"


def test_extension_inheritance_and_specificity(run_source):
    out = run_source(
        """\
class Base {}
class Child < Base {}
def Base.kind: "base"
print(Child().kind(), Base().kind())
def Child.kind: "child"
print(Child().kind())
"""
    ).stdout
    assert out == "base base\nchild\n"


def test_extension_scope_inner_shadows_outer(run_source):
    out = run_source(
        """\
def Int.tag: "outer"
def scoped() {
    def Int.tag: "inner"
    1.tag()
}
print(1.tag(), scoped(), 1.tag())
"""
    ).stdout
    assert out == "outer inner outer\n"


def test_inner_scope_wins_over_more_specific_outer_extension(run_source):
    out = run_source(
        """\
class Base {}
class Child < Base {}
def Child.pick: "outer-child"
def scoped() {
    def Base.pick: "inner-base"
    Child().pick()
}
print(scoped(), Child().pick())
"""
    ).stdout
    assert out == "inner-base outer-child\n"


def test_block_scoped_extension_is_not_visible_after_block(run_source, capsys, caplog):
    with pytest.raises(CompilerError):
        run_source(
            """\
def scoped() {
    if true {
        def Int.tag: "block"
        print(1.tag())
    }
}
scoped()
var x = 1
print(x.tag())
"""
        )
    assert capsys.readouterr().out == "block\n"
    assert "has no attribute 'tag'" in caplog.text


def test_extension_is_captured_by_closures(run_source):
    out = run_source(
        """\
def make() {
    def Int.tag: "inner"
    do: 1.tag()
}
val f = make()
print(f())
"""
    ).stdout
    assert out == "inner\n"


def test_super_in_extension_searches_class_members(run_source):
    out = run_source(
        """\
class Base { def name: "base" }
class Child < Base {}
def Child.describe: super.name() + "+ext"
print(Child().describe())
"""
    ).stdout
    assert out == "base+ext\n"


def test_super_never_falls_back_to_extensions(run_source, caplog):
    with pytest.raises(CompilerError):
        run_source(
            """\
class Base {}
class Child < Base {}
def Base.probe: "extension"
def Child.call_probe: super.probe()
Child().call_probe()
"""
        )
    assert "has no super attribute 'probe'" in caplog.text


def test_super_on_object_extension_fails_cleanly(run_source, caplog):
    with pytest.raises(CompilerError):
        run_source(
            """\
def Object.probe: super.probe()
class C {}
C().probe()
"""
        )
    assert "has no super attribute 'probe'" in caplog.text


def test_class_object_extensions_use_type_receiver(run_source, caplog):
    out = run_source(
        """\
class C {}
def Type.tag: "type"
print(C.tag())
"""
    ).stdout
    assert out == "type\n"

    with pytest.raises(CompilerError):
        run_source(
            """\
class C {}
def C.tag: "instance"
print(C.tag())
"""
        )
    assert "has no attribute 'tag'" in caplog.text


def test_redefinition_between_compilers_is_isolated(run_source, caplog):
    run_source("def Int.zed: 7\n")
    with pytest.raises(CompilerError):
        run_source("var x = 1\nprint(x.zed())\n")
    assert "has no attribute 'zed'" in caplog.text


def test_module_level_redefinition_replaces_extension(run_source):
    out = run_source(
        """\
class C {}
def C.value: 1
def C.value: 2
print(C().value())
"""
    ).stdout
    assert out == "2\n"


@pytest.mark.parametrize(
    ("source", "message"),
    [
        ("def A.B.f: 1\n", "must name exactly one receiver type"),
        ("def class.A.f: 1\n", "Class method names must use 'def class.name'."),
        ("class C { def C.f: 1 }\n", "Cannot define extension method in class scope."),
        ("class C {}\ndef C.__init__: 1\n", "cannot define special method '__init__'"),
        ("class C {}\ndef C.__op_add__: 1\n", "cannot define special method '__op_add__'"),
        ("def Missing.f: 1\n", "Extension receiver 'Missing' is not defined."),
        ("var not_a_type = 1\ndef not_a_type.f: 1\n", "is not a type."),
        ("def C.f: 1\nclass C {}\n", "Extension receiver 'C' is not defined."),
        ('class C {}\ndef C.operator "+"(x): 1\n', "not supported yet"),
        ("class C {}\ndef g() { def C.f: 1\n def C.f: 2 }\ng()\n", "already defined"),
        ("class C {}\ndef C.f: 1\ndef g() { print(f) }\ng()\n", "Name 'f' is not defined"),
    ],
)
def test_extension_errors(source: str, message: str, run_source, caplog):
    # Compile-time diagnostics exit, runtime diagnostics raise CompilerError.
    with pytest.raises((CompilerError, SystemExit)):
        run_source(source)
    assert message in caplog.text


def test_extension_named_like_a_type_is_allowed(run_source):
    out = run_source(
        """\
class A {}
def A.B: "extension"
print(A().B())
"""
    ).stdout
    assert out == "extension\n"
