#! /usr/bin/env python

"""Single inheritance for `oort-core` (OP 0025 increment B)."""

import pytest

from tests.helpers import get_compiler


def core(source: str) -> str:
    return "#lang oort-core\n" + source


def check_error(caplog: pytest.LogCaptureFixture, source: str, message: str) -> None:
    compiler = get_compiler("NOT_EXIST -t eval")
    with pytest.raises(SystemExit):
        compiler.run_string(core(source))
    assert message in caplog.text


class TestCoreInheritance:
    def test_slots_super_and_subtype_assignment(self, run_source):
        result = run_source(
            core(
                "class Base {\n"
                "    val id: Int\n"
                '    var tag: String = "base"\n'
                "    def __init__(id: Int) { this.id = id }\n"
                '    def describe() -> String { "base" }\n'
                "}\n"
                "class Derived < Base {\n"
                "    val extra: Int\n"
                "    def __init__(id: Int, extra: Int) {\n"
                "        super.__init__(id)\n"
                "        this.extra = extra\n"
                "    }\n"
                '    def describe() -> String { super.describe() + "+derived" }\n'
                "    def total() -> Int { this.id + this.extra }\n"
                "}\n"
                "val d = Derived(2, 3)\n"
                "val b: Base = d\n"
                "print(d.describe())\n"
                "print(b.describe())\n"
                "print(d.total(), d.id, d.tag)\n"
            )
        )
        assert result.stdout == "base+derived\nbase+derived\n5 2 base\n"

    def test_inheritance_runs_on_vm(self, run_source):
        result = run_source(
            core(
                "class Base {\n"
                "    val id: Int\n"
                "    def __init__(id: Int) { this.id = id }\n"
                "}\n"
                "class Derived < Base {\n"
                "    def __init__(id: Int) { super.__init__(id) }\n"
                "    def twice() -> Int { this.id * 2 }\n"
                "}\n"
                "val d = Derived(4)\n"
                "print(d.twice())\n"
            ),
            target="vm",
        )
        assert result.stdout == "8\n"

    def test_base_slot_initializers_run_before_derived(self, run_source):
        result = run_source(
            core(
                "def mark(label: String) -> String {\n"
                "    print(label)\n"
                "    label\n"
                "}\n"
                'class Base { var a: String = mark("base") }\n'
                'class Derived < Base { var b: String = mark("derived") }\n'
                "val d = Derived()\n"
                "print(d.a, d.b)\n"
            )
        )
        assert result.stdout == "base\nderived\nbase derived\n"

    def test_no_init_derived_with_initialized_base_slots(self, run_source):
        result = run_source(
            core(
                "class Base { val id: Int = 7 }\n"
                "class Derived < Base { val extra: Int = 2 }\n"
                "val d = Derived()\n"
                "print(d.id, d.extra)\n"
            )
        )
        assert result.stdout == "7 2\n"

    def test_no_init_derived_may_inherit_zero_argument_initializer(self, run_source):
        result = run_source(
            core(
                "class Base {\n"
                "    val id: Int = 7\n"
                '    def __init__() { print("base-init") }\n'
                "}\n"
                "class Derived < Base {}\n"
                "print(Derived().id)\n"
            )
        )
        assert result.stdout == "base-init\n7\n"

    def test_derived_init_can_assign_base_slot_directly(self, run_source):
        result = run_source(
            core(
                "class Base {\n"
                "    val id: Int\n"
                "    def __init__(id: Int) { this.id = id }\n"
                "}\n"
                "class Derived < Base {\n"
                "    val extra: Int\n"
                "    def __init__(id: Int, extra: Int) {\n"
                "        this.id = id\n"
                "        this.extra = extra\n"
                "    }\n"
                "}\n"
                "print(Derived(1, 2).id, Derived(1, 2).extra)\n"
            )
        )
        assert result.stdout == "1 2\n"

    def test_branch_join_uses_nearest_base_class(self, run_source):
        result = run_source(
            core(
                "class Base { val id: Int = 1 }\n"
                "class Derived < Base { val extra: Int = 2 }\n"
                "def choose(flag: Bool, base: Base, derived: Derived) -> Base {\n"
                "    if flag { derived } else { base }\n"
                "}\n"
                "print(choose(true, Base(), Derived()).id)\n"
            )
        )
        assert result.stdout == "1\n"

    def test_function_parameters_are_contravariant(self, run_source):
        result = run_source(
            core(
                "class Base {}\n"
                "class Derived < Base {}\n"
                "def useBase(value: Base) -> Int { 1 }\n"
                "val f: (Derived) -> Int = useBase\n"
                "print(f(Derived()))\n"
            )
        )
        assert result.stdout == "1\n"

    def test_override_return_may_be_covariant(self, run_source):
        result = run_source(
            core(
                "class A {}\n"
                "class B < A {}\n"
                "class Maker { def make() -> A { A() } }\n"
                "class SubMaker < Maker { def make() -> B { B() } }\n"
                "val m: Maker = SubMaker()\n"
                "val a: A = m.make()\n"
                "print(a == a)\n"
            )
        )
        assert result.stdout == "true\n"


class TestCoreInheritanceRejections:
    def test_base_must_be_a_class(self, caplog):
        check_error(
            caplog,
            "enum E { A }\nclass D < E {}\n",
            "Base entry must be a class or interface, got E.",
        )

    def test_self_and_forward_base_are_unknown(self, caplog):
        check_error(caplog, "class D < D {}\n", "Unknown type 'D'")
        check_error(caplog, "class D < E {}\nclass E {}\n", "Unknown type 'E'")

    def test_base_slot_cannot_be_redeclared(self, caplog):
        check_error(
            caplog,
            "class B { val x: Int = 1 }\nclass D < B { val x: Int = 2 }\n",
            "Slot 'x' is already declared in base class 'B'.",
        )

    def test_method_cannot_conflict_with_inherited_slot(self, caplog):
        check_error(
            caplog,
            "class B { val x: Int = 1 }\nclass D < B { def x() -> Int { 1 } }\n",
            "Method 'x' conflicts with inherited slot 'B.x'.",
        )

    def test_slot_cannot_conflict_with_inherited_method(self, caplog):
        check_error(
            caplog,
            "class B { def x() -> Int { 1 } }\nclass D < B { val x: Int = 1 }\n",
            "Slot 'x' conflicts with inherited method 'B.x'.",
        )

    def test_function_parameter_widening_is_rejected(self, caplog):
        check_error(
            caplog,
            "class Base {}\nclass Derived < Base {}\n"
            "def useDerived(value: Derived) -> Int { 1 }\n"
            "val f: (Base) -> Int = useDerived\n",
            "Expected (Base) -> Int, got (Derived) -> Int.",
        )

    def test_override_parameters_must_match(self, caplog):
        check_error(
            caplog,
            "class A {}\nclass B < A {}\n"
            "class Base { def f(x: A) -> Int { 1 } }\n"
            "class Derived < Base { def f(x: B) -> Int { 2 } }\n",
            "Overriding method 'Derived.f' must use the base parameter types (A); got (B).",
        )

    def test_override_return_must_be_covariant(self, caplog):
        check_error(
            caplog,
            "class A {}\nclass B < A {}\n"
            "class Base { def f() -> B { B() } }\n"
            "class Derived < Base { def f() -> A { A() } }\n",
            "Overriding method 'Derived.f' must return B or a subtype, got A.",
        )

    def test_derived_init_must_initialize_inherited_slot(self, caplog):
        check_error(
            caplog,
            "class Base {\n"
            "    val id: Int\n"
            "    def __init__(id: Int) { this.id = id }\n"
            "}\n"
            "class Derived < Base { def __init__() {} }\n",
            "Constructor must initialize slot(s): id.",
        )

    def test_super_init_initializes_inherited_slot(self, run_source):
        result = run_source(
            core(
                "class Base {\n"
                "    val id: Int\n"
                "    def __init__(id: Int) { this.id = id }\n"
                "}\n"
                "class Derived < Base {\n"
                "    def __init__(id: Int) { super.__init__(id) }\n"
                "}\n"
                "print(Derived(9).id)\n"
            )
        )
        assert result.stdout == "9\n"

    def test_super_init_cannot_assign_read_only_base_slot_twice(self, caplog):
        check_error(
            caplog,
            "class Base {\n"
            "    val id: Int\n"
            "    def __init__() { this.id = 1 }\n"
            "}\n"
            "class Derived < Base {\n"
            "    def __init__() {\n"
            "        super.__init__()\n"
            "        super.__init__()\n"
            "    }\n"
            "}\n",
            "Read-only slot 'id' may already be assigned; it can be assigned only once.",
        )

    def test_super_init_checks_arguments(self, caplog):
        check_error(
            caplog,
            "class Base { def __init__(id: Int) {} }\n"
            "class Derived < Base { def __init__() { super.__init__() } }\n",
            "Function '__init__' expects 1 arguments, got 0.",
        )

    def test_no_init_derived_requires_initialized_base_slots(self, caplog):
        check_error(
            caplog,
            "class Base {\n"
            "    val id: Int\n"
            "    def __init__(id: Int) { this.id = id }\n"
            "}\n"
            "class Derived < Base {}\n",
            "Class 'Derived' has slots without initializers but no __init__: id.",
        )

    def test_no_init_derived_rejects_inherited_init_parameters(self, caplog):
        check_error(
            caplog,
            "class Base {\n"
            "    val id: Int = 1\n"
            "    def __init__(x: Int) {}\n"
            "}\n"
            "class Derived < Base {}\n",
            "Class 'Derived' has no __init__ but inherits an initializer requiring 1 argument(s)",
        )

    def test_super_outside_class_is_rejected(self, caplog):
        check_error(
            caplog,
            "class Base { def f() -> Int { 1 } }\nval x = super.f()\n",
            "Can't use implicit 'super' outside method.",
        )

    def test_super_in_base_class_is_rejected(self, caplog):
        check_error(
            caplog,
            "class Base { def f() -> Int { super.f() } }\n",
            "Class 'Base' has no base class; super is not available.",
        )

    def test_super_init_outside_initializer_is_rejected(self, caplog):
        check_error(
            caplog,
            "class Base { def __init__() {} }\n"
            "class Derived < Base { def f() { super.__init__() } }\n",
            "super.__init__() is only allowed inside a subclass __init__.",
        )

    def test_super_missing_method_is_rejected(self, caplog):
        check_error(
            caplog,
            "class Base {}\nclass Derived < Base { def f() { super.nope() } }\n",
            "Base class 'Base' has no method 'nope'.",
        )

    def test_super_slot_access_is_rejected(self, caplog):
        check_error(
            caplog,
            "class Base { val x: Int = 1 }\nclass Derived < Base { def f() -> Int { super.x } }\n",
            "Cannot access inherited slot 'x' through super",
        )

    def test_super_init_without_base_initializer_is_rejected(self, caplog):
        check_error(
            caplog,
            "class Base { val x: Int = 1 }\n"
            "class Derived < Base { def __init__() { super.__init__() } }\n",
            "Base class 'Base' has no __init__ method to call.",
        )

    def test_bare_super_is_rejected(self, caplog):
        check_error(
            caplog,
            "class Base {}\nclass Derived < Base { def f() { super } }\n",
            "super must be followed by a base method",
        )
