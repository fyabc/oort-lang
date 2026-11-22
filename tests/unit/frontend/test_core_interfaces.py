#! /usr/bin/env python

"""Static interfaces for `oort-core` (OP 0026)."""

import pytest

from tests.helpers import get_compiler


def core(source: str) -> str:
    return "#lang oort-core\n" + source


def check_error(caplog: pytest.LogCaptureFixture, source: str, message: str) -> None:
    compiler = get_compiler("NOT_EXIST -t eval")
    with pytest.raises(SystemExit):
        compiler.run_string(source)
    assert message in caplog.text


class TestCoreInterfaces:
    def test_multiple_interfaces_and_method_dispatch(self, run_source):
        result = run_source(
            core(
                "interface Named { def name() -> String }\n"
                "interface Sized { def size() -> Int }\n"
                "interface NamedSized < Named, Sized { def label() -> String }\n"
                "class Point {\n"
                "    val x: Int\n"
                "    def __init__(x: Int) { this.x = x }\n"
                '    def name() -> String { "point" }\n'
                "    def size() -> Int { this.x }\n"
                "    def label() -> String { this.name() }\n"
                "}\n"
                "class Ranked < Point, NamedSized {\n"
                "    def __init__(x: Int) { super.__init__(x) }\n"
                "}\n"
                "def show(item: Named) -> String { item.name() }\n"
                "val r: Ranked = Ranked(4)\n"
                "val ns: NamedSized = r\n"
                "print(show(r), ns.size(), ns.label(), r.name())\n"
            )
        )
        assert result.stdout == "point 4 point point\n"

    def test_interface_implementation_through_base_class(self, run_source):
        result = run_source(
            core(
                "interface HasValue { def value() -> Int }\n"
                "class Base < HasValue {\n"
                "    def value() -> Int { 2 }\n"
                "}\n"
                "class Derived < Base {}\n"
                "val a: HasValue = Base()\n"
                "val b: HasValue = Derived()\n"
                "print(a.value(), b.value())\n"
            )
        )
        assert result.stdout == "2 2\n"

    def test_interface_method_parameters_and_equality(self, run_source):
        result = run_source(
            core(
                "interface Named { def name() -> String }\n"
                "class Point < Named {\n"
                "    val x: Int\n"
                "    def __init__(x: Int) { this.x = x }\n"
                '    def name() -> String { "point" }\n'
                "}\n"
                "val a: Named = Point(1)\n"
                "val b: Named = Point(2)\n"
                "val p = Point(1)\n"
                "print(a == a, a == b, a == p)\n"
            )
        )
        assert result.stdout == "true false false\n"

    def test_identical_methods_across_interfaces_merge(self, run_source):
        result = run_source(
            core(
                "interface A { def f() -> Int }\n"
                "interface B { def f() -> Int }\n"
                "interface C < A, B {}\n"
                "class D < C { def f() -> Int { 3 } }\n"
                "val c: C = D()\n"
                "print(c.f())\n"
            )
        )
        assert result.stdout == "3\n"

    def test_interface_types_in_slots_and_collections(self, run_source):
        result = run_source(
            core(
                "interface Named { def name() -> String }\n"
                "class Point < Named {\n"
                '    def name() -> String { "point" }\n'
                "}\n"
                "class Box {\n"
                "    val item: Named\n"
                "    def __init__(item: Named) { this.item = item }\n"
                "    def name() -> String { this.item.name() }\n"
                "}\n"
                "val items: List[Named] = [Point()]\n"
                "val box = Box(Point())\n"
                "print(box.name(), items[0].name())\n"
            )
        )
        assert result.stdout == "point point\n"

    def test_interfaces_run_on_vm(self, run_source):
        result = run_source(
            core(
                "interface Named { def name() -> String }\n"
                "class Point {\n"
                '    def name() -> String { "vm" }\n'
                "}\n"
                "class Ranked < Point, Named {}\n"
                "val n: Named = Ranked()\n"
                "print(n.name())\n"
            ),
            target="vm",
        )
        assert result.stdout == "vm\n"

    def test_interface_only_class_and_covariant_implementation(self, run_source):
        result = run_source(
            core(
                "class A {}\n"
                "class B < A {}\n"
                "interface Maker { def make() -> A }\n"
                "class SubMaker < Maker { def make() -> B { B() } }\n"
                "val m: Maker = SubMaker()\n"
                "val a: A = m.make()\n"
                "print(a == a)\n"
            )
        )
        assert result.stdout == "true\n"


class TestCoreInterfaceRejections:
    def test_interface_is_core_only(self, caplog):
        check_error(
            caplog,
            "#lang oort-object\ninterface I { def m() -> Int }\n",
            "Interfaces are only supported in oort-core yet.",
        )

    def test_interface_must_be_top_level(self, caplog):
        check_error(
            caplog,
            core("def f() { interface I { def m() -> Int } }\n"),
            "Interface declarations are only allowed at module top level in oort-core.",
        )

    def test_interface_cannot_be_an_expression(self, caplog):
        check_error(
            caplog,
            core("val x = interface I { def m() -> Int }\n"),
            "Interface declarations are only allowed at module top level in oort-core.",
        )

    def test_generic_interface_is_rejected(self, caplog):
        check_error(
            caplog,
            core("interface I[T] { def m() -> Int }\n"),
            "Generic interfaces are not supported in oort-core yet.",
        )

    def test_generic_interface_method_is_rejected(self, caplog):
        check_error(
            caplog,
            core("interface I { def m[T](x: Int) -> Int }\n"),
            "Generic interface methods are not supported in oort-core yet.",
        )

    def test_interface_method_requires_return_annotation(self, caplog):
        check_error(
            caplog,
            core("interface I { def m() }\n"),
            "Interface method 'I.m' requires a return type annotation.",
        )

    def test_default_interface_method_is_rejected(self, caplog):
        # Signature-only interfaces are enforced by the grammar; a body is a
        # syntax error in this slice.
        check_error(
            caplog,
            core("interface I { def m() -> Int { 1 } }\n"),
            "OortSyntaxError",
        )

    def test_interface_init_is_rejected(self, caplog):
        check_error(
            caplog,
            core("interface I { def __init__() -> Int }\n"),
            "Interface method 'I.__init__' cannot be named '__init__'.",
        )

    def test_duplicate_interface_method_is_rejected(self, caplog):
        check_error(
            caplog,
            core("interface I { def m() -> Int\n def m() -> Bool }\n"),
            "Duplicate member 'm' in interface 'I'.",
        )

    def test_interface_base_must_be_an_interface(self, caplog):
        check_error(
            caplog,
            core("class C {}\ninterface I < C {}\n"),
            "Interface base must be an interface, got C.",
        )

    def test_duplicate_parent_interface_is_rejected(self, caplog):
        check_error(
            caplog,
            core("interface A {}\ninterface I < A, A {}\n"),
            "Interface 'I' inherits interface 'A' more than once.",
        )

    def test_inherited_interface_signature_conflict(self, caplog):
        check_error(
            caplog,
            core(
                "interface A { def m(x: Int) -> Int }\n"
                "interface B { def m(x: Bool) -> Int }\n"
                "interface C < A, B {}\n"
            ),
            "Interface 'C' inherits conflicting signatures for method 'm'.",
        )

    def test_redeclared_inherited_method_must_match(self, caplog):
        check_error(
            caplog,
            core(
                "interface A { def m(x: Int) -> Int }\ninterface I < A { def m(x: Bool) -> Int }\n"
            ),
            "Interface 'I' redeclares inherited method 'm' with a different signature.",
        )

    def test_class_must_implement_interface_methods(self, caplog):
        check_error(
            caplog,
            core("interface I { def m() -> Int }\nclass C < I {}\n"),
            "Class 'C' does not implement interface 'I' method 'm'.",
        )

    def test_class_method_parameters_must_match_interface(self, caplog):
        check_error(
            caplog,
            core(
                "interface I { def m(x: Int) -> Int }\n"
                "class C < I { def m(x: Bool) -> Int { 1 } }\n"
            ),
            "Method 'C.m' does not match interface 'I.m'; expected (Int) -> Int.",
        )

    def test_class_method_return_must_match_interface(self, caplog):
        check_error(
            caplog,
            core("interface I { def m() -> Int }\nclass C < I { def m() -> Bool { true } }\n"),
            "Method 'C.m' does not match interface 'I.m'; expected () -> Int.",
        )

    def test_duplicate_interface_implementation_is_rejected(self, caplog):
        check_error(
            caplog,
            core("interface I { def m() -> Int }\nclass C < I, I { def m() -> Int { 1 } }\n"),
            "Class 'C' implements interface 'I' more than once.",
        )

    def test_class_base_must_appear_first(self, caplog):
        check_error(
            caplog,
            core(
                "interface I { def m() -> Int }\n"
                "class B { def m() -> Int { 1 } }\n"
                "class C < I, B {}\n"
            ),
            "Class base must appear first in the base list; other entries must be interfaces.",
        )

    def test_interface_cannot_be_instantiated(self, caplog):
        check_error(
            caplog,
            core("interface I { def m() -> Int }\nval x = I()\n"),
            "Interface 'I' cannot be instantiated.",
        )

    def test_interface_has_no_runtime_value(self, caplog):
        check_error(
            caplog,
            core("interface I { def m() -> Int }\nprint(I)\n"),
            "Interface 'I' has no runtime value; use it only in type positions.",
        )

    def test_interface_takes_no_type_arguments(self, caplog):
        check_error(
            caplog,
            core("interface I { def m() -> Int }\ndef f(x: I[Int]) -> Int { 1 }\n"),
            "Type 'I' does not take type arguments.",
        )

    def test_interface_method_lookup_reports_missing_method(self, caplog):
        check_error(
            caplog,
            core("interface I { def m() -> Int }\ndef f(x: I) -> Int { x.nope() }\n"),
            "Interface 'I' has no method 'nope'.",
        )
