#! /usr/bin/env python

"""Positive and rejection tests for the `oort-core` type checker."""

import pytest

from tests.helpers import get_compiler


def core(source: str) -> str:
    return "#lang oort-core\n" + source


def check_error(caplog: pytest.LogCaptureFixture, source: str, message: str) -> None:
    compiler = get_compiler("NOT_EXIST -t eval")
    with pytest.raises(SystemExit):
        compiler.run_string(core(source))
    assert message in caplog.text


class TestCorePositive:
    def test_literals_and_print(self, run_source):
        result = run_source(core("print(1)\nprint(true)\nprint()\n"))
        assert result.stdout == "1\ntrue\n\n"

    def test_local_inference_and_mutation(self, run_source):
        result = run_source(core("var x = 1\nx = x + 2\nprint(x)\n"))
        assert result.stdout == "3\n"

    def test_annotated_declarations(self, run_source):
        result = run_source(
            core("var count: Int = 1\nval enabled: Bool = true\nprint(count)\nprint(enabled)\n")
        )
        assert result.stdout == "1\ntrue\n"

    def test_operators(self, run_source):
        result = run_source(
            core(
                "print((1 + 2) * 3 // 2 % 5)\n"
                "print(1 < 2)\n"
                "print(1 == 1)\n"
                "print(true != false)\n"
                "print(true and false)\n"
                "print(true or false)\n"
                "print(not false)\n"
                "print(-1)\n"
            )
        )
        assert result.stdout == "4\ntrue\ntrue\ntrue\nfalse\ntrue\ntrue\n-1\n"

    def test_float_arithmetic_and_division(self, run_source):
        result = run_source(
            core(
                "val half = 5 / 2\n"
                "val mixed = 1 + 2.5\n"
                "print(half)\n"
                "print(mixed * 2.0)\n"
                "print(5 // 2.0, 5 % 2.0)\n"
                "print(-1.5)\n"
            )
        )
        assert result.stdout == "2.5\n7.0\n2.0 1.0\n-1.5\n"

    def test_numeric_comparisons_allow_mixed_int_and_float(self, run_source):
        result = run_source(core("print(1 == 1.0, 1 < 1.5, 2.5 >= 2, 1 != 2.5)\n"))
        assert result.stdout == "true true true true\n"

    def test_string_concatenation_and_comparison(self, run_source):
        result = run_source(
            core(
                'val name: String = "oort"\n'
                'print(name + "!")\n'
                'print("a" < "b", "a" == "a", "a" != "b")\n'
                'print("a" <= "a", "b" > "a")\n'
            )
        )
        assert result.stdout == "oort!\ntrue true true\ntrue true\n"

    def test_float_and_string_annotations_in_functions(self, run_source):
        result = run_source(
            core(
                "def average(a: Float, b: Float) -> Float {\n"
                "    (a + b) / 2.0\n"
                "}\n"
                "def greet(who: String) -> String {\n"
                '    "Hello, " + who\n'
                "}\n"
                "print(average(1.0, 2.0))\n"
                'print(greet("Oort"))\n'
            )
        )
        assert result.stdout == "1.5\nHello, Oort\n"

    def test_functions_and_recursion(self, run_source):
        result = run_source(
            core(
                "def fact(n: Int) -> Int {\n"
                "    if n <= 1 { 1 } else { n * fact(n - 1) }\n"
                "}\n"
                "print(fact(5))\n"
            )
        )
        assert result.stdout == "120\n"

    def test_unit_function(self, run_source):
        result = run_source(core("def show(n: Int) -> Unit {\n    print(n)\n}\nshow(7)\n"))
        assert result.stdout == "7\n"

    def test_if_as_expression(self, run_source):
        result = run_source(core("val x = if true { 1 } else { 2 }\nprint(x)\n"))
        assert result.stdout == "1\n"

    def test_block_scoping(self, run_source):
        result = run_source(core("var x = 1\n{ var x = 2\n  print(x) }\nprint(x)\n"))
        assert result.stdout == "2\n1\n"

    def test_return_on_all_paths(self, run_source):
        result = run_source(
            core(
                "def sign(n: Int) -> Bool {\n"
                "    if n < 0 { return false } else { return true }\n"
                "}\n"
                "print(sign(1))\n"
            )
        )
        assert result.stdout == "true\n"

    def test_infer_return_from_tail_expression(self, run_source):
        result = run_source(core("def add(a: Int, b: Int) { a + b }\nprint(add(1, 2))\n"))
        assert result.stdout == "3\n"

    def test_infer_return_from_single_return(self, run_source):
        result = run_source(core("def inc(n: Int) { return n + 1 }\nprint(inc(4))\n"))
        assert result.stdout == "5\n"

    def test_infer_return_all_paths_return(self, run_source):
        result = run_source(
            core(
                "def sign(n: Int) {\n"
                "    if n < 0 { return -1 }\n"
                "    if n > 0 { return 1 }\n"
                "    return 0\n"
                "}\n"
                "print(sign(-3), sign(0), sign(2))\n"
            )
        )
        assert result.stdout == "-1 0 1\n"

    def test_infer_return_mixed_return_and_tail(self, run_source):
        result = run_source(
            core("def f(x: Bool) {\n    if x { return 1 }\n    2\n}\nprint(f(true), f(false))\n")
        )
        assert result.stdout == "1 2\n"

    def test_infer_unit_return(self, run_source):
        result = run_source(core("def show(n: Int) { print(n) }\nshow(7)\n"))
        assert result.stdout == "7\n"

    def test_infer_return_if_expression(self, run_source):
        result = run_source(
            core("def pick(x: Bool) { if x { 1 } else { 2 } }\nprint(pick(true))\n")
        )
        assert result.stdout == "1\n"

    def test_infer_return_float_and_string(self, run_source):
        result = run_source(
            core(
                "def half(x: Float) { x / 2.0 }\n"
                'def greet(name: String) { "hi " + name }\n'
                'print(half(5.0), greet("oort"))\n'
            )
        )
        assert result.stdout == "2.5 hi oort\n"

    def test_annotated_recursion_still_works(self, run_source):
        result = run_source(
            core(
                "def fact(n: Int) -> Int { if n <= 1 { 1 } else { n * fact(n - 1) } }\n"
                "print(fact(5))\n"
            )
        )
        assert result.stdout == "120\n"

    def test_inferred_function_used_by_later_function(self, run_source):
        result = run_source(
            core(
                "def double(n: Int) { n * 2 }\n"
                "def quad(n: Int) { double(double(n)) }\n"
                "print(quad(3))\n"
            )
        )
        assert result.stdout == "12\n"


class TestCoreRejections:
    def test_annotation_mismatch(self, caplog):
        check_error(caplog, "var x: Bool = 1\n", "Expected Bool, got Int.")

    def test_assignment_mismatch(self, caplog):
        check_error(
            caplog,
            "var x = 1\nx = true\n",
            "Expected Int, got Bool.",
        )

    def test_assignment_to_val(self, caplog):
        check_error(
            caplog,
            "val x = 1\nx = 2\n",
            "Cannot assign to immutable binding 'x'",
        )

    def test_assignment_to_parameter(self, caplog):
        check_error(
            caplog,
            "def f(x: Int) -> Int { x = 2\nx }\n",
            "Cannot assign to immutable binding 'x'",
        )

    def test_unknown_name(self, caplog):
        check_error(caplog, "def f() -> Int { missing }\n", "Unknown name 'missing'.")

    def test_duplicate_declaration(self, caplog):
        check_error(
            caplog,
            "val x = 1\nval x = 2\n",
            "Duplicate declaration of 'x'",
        )

    def test_missing_parameter_annotation(self, caplog):
        check_error(
            caplog,
            "def f(x) -> Int { x }\n",
            "Parameter 'x' requires a type annotation",
        )

    def test_recursive_function_requires_return_annotation(self, caplog):
        # Return types are inferred for non-recursive functions, but a
        # self-recursive call cannot pin down the placeholder return type, so
        # an explicit annotation is still required (as in Kotlin/Scala).
        check_error(
            caplog,
            "def fact(n: Int) { if n <= 1 { 1 } else { n * fact(n - 1) } }\n",
            "Recursive function 'fact' requires a return type annotation",
        )

    def test_incompatible_return_types(self, caplog):
        check_error(
            caplog,
            'def f(x: Bool) {\n  if x { return 1 }\n  return "s"\n}\n',
            "The return types of function 'f' are incompatible: Int and String.",
        )

    def test_recursive_method_requires_return_annotation(self, caplog):
        # Method returns are inferred in dependency order, but a method on a
        # recursive call cycle cannot be inferred and needs an annotation.
        check_error(
            caplog,
            "class C { def m(n: Int) { if n <= 0 { 0 } else { this.m(n - 1) } } }\n",
            "Recursive method 'C.m' requires a return type annotation",
        )

    def test_mutually_recursive_methods_require_return_annotation(self, caplog):
        check_error(
            caplog,
            "class C {\n"
            "  def a(n: Int) { if n <= 0 { 0 } else { this.b(n - 1) } }\n"
            "  def b(n: Int) { if n <= 0 { 1 } else { this.a(n - 1) } }\n"
            "}\n",
            "Recursive method 'C.a' requires a return type annotation",
        )

    def test_unit_in_variable_annotation(self, caplog):
        check_error(
            caplog,
            "var x: Unit = print(1)\n",
            "Unit is only allowed as a function return type",
        )

    def test_unknown_type_name(self, caplog):
        check_error(
            caplog,
            "var x: Nope = 1\n",
            "Unknown type 'Nope' in oort-core",
        )

    def test_numeric_annotations_do_not_coerce(self, caplog):
        check_error(
            caplog,
            "var x: Float = 1\n",
            "Expected Float, got Int.",
        )

    def test_non_name_annotation(self, caplog):
        check_error(
            caplog,
            "var x: Foo[Int] = 1\n",
            "Generic type applications are only supported for List, Set, Dict, "
            "Tuple and generic enums.",
        )

    def test_if_condition_must_be_bool(self, caplog):
        check_error(
            caplog,
            "if 1 { print(1) }\n",
            "if condition must be Bool",
        )

    def test_function_body_type(self, caplog):
        check_error(
            caplog,
            "def f() -> Int { true }\n",
            "Expected Int, got Bool.",
        )

    def test_function_missing_return_on_some_path(self, caplog):
        check_error(
            caplog,
            "def f(n: Int) -> Int { if n < 0 { return 0 } }\n",
            "An if without else has type Unit, expected Int.",
        )

    def test_bare_return_in_non_unit_function(self, caplog):
        check_error(
            caplog,
            "def f() -> Int { return }\n",
            "a bare return is only allowed for Unit functions",
        )

    def test_value_return_in_unit_function(self, caplog):
        check_error(
            caplog,
            "def f() -> Unit { return 1 }\n",
            "Expected Unit, got Int.",
        )

    def test_call_arity(self, caplog):
        check_error(
            caplog,
            "def f(a: Int, b: Int) -> Int { a + b }\nf(1)\n",
            "Function 'f' expects 2 arguments, got 1.",
        )

    def test_call_argument_type(self, caplog):
        check_error(
            caplog,
            "def f(a: Int) -> Int { a }\nf(true)\n",
            "Expected Int, got Bool.",
        )

    def test_call_non_function(self, caplog):
        check_error(
            caplog,
            "val x = 1\nx(1)\n",
            "'x' is not callable.",
        )

    def test_branch_types_must_match(self, caplog):
        check_error(
            caplog,
            "val x = if true { 1 } else { true }\n",
            "branches of this if have incompatible types",
        )

    def test_branches_do_not_promote_int_to_float(self, caplog):
        check_error(
            caplog,
            "val x = if true { 1 } else { 1.5 }\n",
            "branches of this if have incompatible types",
        )

    def test_arithmetic_requires_numbers_or_strings(self, caplog):
        check_error(
            caplog,
            "def f(x: Int) -> Int { x + true }\n",
            "Operator '+' requires two numbers or two String operands",
        )
        check_error(
            caplog,
            'print(1 - "x")\n',
            "Operator '-' requires two numbers",
        )

    def test_comparison_requires_numbers_or_strings(self, caplog):
        check_error(
            caplog,
            "print(1 < true)\n",
            "requires two numbers or two String operands",
        )

    def test_equality_requires_comparable_types(self, caplog):
        check_error(
            caplog,
            "print(1 == true)\n",
            "requires two numbers, two Bool or two String operands",
        )

    def test_boolean_operators_require_bool(self, caplog):
        check_error(
            caplog,
            "print(true and 1)\n",
            "Expected Bool, got Int.",
        )

    def test_not_requires_bool(self, caplog):
        check_error(
            caplog,
            "print(not 1)\n",
            "Expected Bool, got Int.",
        )

    def test_power_is_rejected(self, caplog):
        check_error(
            caplog,
            "print(2 ** -1)\n",
            "The '**' operator is not supported in oort-core yet",
        )

    def test_unary_bitwise_is_rejected(self, caplog):
        check_error(
            caplog,
            "print(~1)\n",
            "Unary operator '~' is not supported",
        )

    def test_cannot_infer_unit_variable(self, caplog):
        check_error(
            caplog,
            "val x = print(1)\n",
            "Cannot infer a usable type for 'x'",
        )

    def test_augmented_assignment_is_rejected(self, caplog):
        check_error(
            caplog,
            "var x = 1\nx += 1\n",
            "Augmented assignment is not supported in oort-core yet.",
        )

    def test_multi_target_declaration_is_rejected(self, caplog):
        check_error(
            caplog,
            "val x, y = 1, 2\n",
            "Multi-target declarations are not supported in oort-core yet.",
        )

    def test_native_import_is_rejected(self, caplog):
        check_error(
            caplog,
            'import "math"\n',
            "Native modules are not supported in oort-core imports yet.",
        )

    @pytest.mark.parametrize(
        ("source", "message"),
        [
            ("print(null)\n", "null is not supported"),
            (
                "val f = do: 1\n",
                "Lambdas without an explicit parameter list are not supported",
            ),
            ("print([1][0:1])\n", "Slices are not supported"),
            ("print([1].length)\n", "Attribute access is only supported on imported modules"),
        ],
    )
    def test_unsupported_constructs(self, caplog, source: str, message: str):
        check_error(caplog, source, message)

    def test_defaults_are_rejected(self, caplog):
        check_error(
            caplog,
            "def f(x: Int = 1) -> Int { x }\n",
            "Defaults, keyword-only/positional-only markers",
        )

    def test_keyword_arguments_are_rejected(self, caplog):
        check_error(
            caplog,
            "def f(x: Int) -> Int { x }\nf(x = 1)\n",
            "Keyword, variadic and block arguments are not supported",
        )

    def test_error_recovery_reports_independent_errors(self, caplog):
        compiler = get_compiler("NOT_EXIST -t eval")
        with pytest.raises(SystemExit):
            compiler.run_string(core("var a: Bool = 1\nvar b: Int = true\n"))
        assert "Expected Bool, got Int." in caplog.text
        assert "Expected Int, got Bool." in caplog.text

    def test_unsupported_initializer_does_not_cascade(self, caplog):
        compiler = get_compiler("NOT_EXIST -t eval")
        with pytest.raises(SystemExit):
            compiler.run_string(core("var x = null\nprint(x)\n"))
        assert "null is not supported" in caplog.text
        assert "Cannot infer a usable type" not in caplog.text


if __name__ == "__main__":
    pytest.main([__file__])


class TestCoreAdt:
    def test_enum_construction_and_match(self, run_source):
        result = run_source(
            core(
                "enum Shape { Circle(r: Int), Rect(w: Int, h: Int), Empty }\n"
                "val s = Circle(3)\n"
                "print(match s { Circle(r) => r, Rect(w, h) => w * h, Empty => 0 })\n"
            )
        )
        assert result.stdout == "3\n"

    def test_nullary_constructor_and_wildcard(self, run_source):
        result = run_source(
            core(
                "enum Color { Red, Green }\n"
                "print(match Green { Red => 1, Green => 2 })\n"
                "print(match Red { _ => 9 })\n"
            )
        )
        assert result.stdout == "2\n9\n"

    def test_recursive_enum(self, run_source):
        result = run_source(
            core(
                "enum IntList { Cons(head: Int, tail: IntList), Nil }\n"
                "val xs = Cons(1, Cons(2, Nil))\n"
                "def total(xs: IntList) -> Int { "
                "match xs { Cons(h, t) => h + total(t), Nil => 0 } }\n"
                "print(total(xs))\n"
            )
        )
        assert result.stdout == "3\n"

    def test_nested_match(self, run_source):
        result = run_source(
            core(
                "enum Inner { A(x: Int), B }\n"
                "enum Outer { Wrap(inner: Inner), Empty }\n"
                "val o = Wrap(A(7))\n"
                "print(match o { Wrap(inner) => match inner { A(v) => v, B => 0 }, "
                "Empty => -1 })\n"
            )
        )
        assert result.stdout == "7\n"

    def test_print_enum_value(self, run_source):
        result = run_source(core("enum E { A, B(x: Int) }\nprint(A)\nprint(B(2))\n"))
        assert result.stdout == "A\nB(2)\n"

    def test_return_from_match_arm(self, run_source):
        result = run_source(
            core(
                "enum E { A, B }\n"
                "def f(x: E) -> Int { match x { A => return 1, B => 2 } }\n"
                "print(f(A))\nprint(f(B))\n"
            )
        )
        assert result.stdout == "1\n2\n"


class TestCoreAdtRejections:
    def test_non_exhaustive_match(self, caplog):
        check_error(
            caplog,
            "enum E { A, B }\nval x = A\nprint(match x { A => 1 })\n",
            "Match is not exhaustive; missing: B.",
        )

    def test_unknown_constructor_pattern(self, caplog):
        check_error(
            caplog,
            "enum E { A, B }\nval x = A\nprint(match x { A => 1, C() => 2 })\n",
            "Enum 'E' has no constructor 'C'.",
        )

    def test_constructor_pattern_arity(self, caplog):
        check_error(
            caplog,
            "enum E { A(x: Int), B }\nval x = A(1)\nprint(match x { A() => 1, B => 0 })\n",
            "Constructor 'A' expects 1 argument(s), got 0.",
        )

    def test_constructor_payload_type(self, caplog):
        check_error(
            caplog,
            "enum E { A(x: Int, y: Int) }\nprint(A(true))\n",
            "Expected Int, got Bool.",
        )

    def test_duplicate_pattern_binding(self, caplog):
        check_error(
            caplog,
            "enum E { A(x: Int) }\nprint(match A(1, 2) { A(v, v) => v })\n",
            "Duplicate declaration of 'v' in oort-core.",
        )

    def test_incompatible_arm_types(self, caplog):
        check_error(
            caplog,
            "enum E { A, B }\nprint(match A { A => 1, B => true })\n",
            "arms of this match have incompatible types",
        )

    def test_generic_enum_bounds_are_rejected(self, caplog):
        check_error(
            caplog,
            "enum E[T: Int] { A }\n",
            "Type parameter bounds are not supported in oort-core yet",
        )

    def test_generic_enum_defaults_are_rejected(self, caplog):
        check_error(
            caplog,
            "enum E[T = Int] { A }\n",
            "Type parameter defaults are not supported in oort-core yet.",
        )

    def test_empty_enum_is_rejected(self, caplog):
        check_error(
            caplog,
            "enum E { }\n",
            "An enum must declare at least one constructor.",
        )

    def test_reserved_enum_name(self, caplog):
        check_error(
            caplog,
            "enum Int { A }\n",
            "Enum name 'Int' is reserved in oort-core.",
        )

    def test_match_on_non_enum(self, caplog):
        check_error(
            caplog,
            "print(match [1] { _ => 1 })\n",
            "The scrutinee of match must have an enum, Bool, Int, Float, String "
            "or Tuple type in oort-core, got List[Int].",
        )

    def test_nested_enum_is_rejected(self, caplog):
        check_error(
            caplog,
            "def f() -> Unit { enum E { A } }\n",
            "Enum declarations are only allowed at module top level",
        )

    def test_unknown_field_type(self, caplog):
        check_error(
            caplog,
            "enum E { A(x: Missing) }\n",
            "Unknown type 'Missing' in oort-core.",
        )

    def test_duplicate_constructor(self, caplog):
        check_error(
            caplog,
            "enum E { A, A }\n",
            "Constructor 'A' is already declared",
        )

    def test_payload_constructor_bare_pattern(self, caplog):
        check_error(
            caplog,
            "enum E { A(x: Int) }\nprint(match A(1) { A => 1 })\n",
            "Constructor 'A' expects 1 argument(s).",
        )


class TestCoreGenericAdt:
    def test_generic_enum_construction_and_match(self, run_source):
        result = run_source(
            core(
                "enum Maybe[T] { Just(value: T), Nothing }\n"
                "def unwrap(o: Maybe[Int]) -> Int {\n"
                "    match o { Just(v) => v, Nothing => 0 }\n"
                "}\n"
                "val a: Maybe[Int] = Just(3)\n"
                "print(unwrap(a))\n"
                "print(unwrap(Nothing))\n"
            )
        )
        assert result.stdout == "3\n0\n"

    def test_generic_enum_infers_from_arguments(self, run_source):
        result = run_source(
            core(
                "enum Maybe[T] { Just(value: T), Nothing }\n"
                "val a = Just(5)\n"
                "print(match a { Just(v) => v, Nothing => 0 })\n"
                'val b = Just("text")\n'
                'print(match b { Just(v) => v, Nothing => "" })\n'
            )
        )
        assert result.stdout == "5\ntext\n"

    def test_generic_enum_expected_type_propagates_to_payload(self, run_source):
        result = run_source(
            core(
                "enum Maybe[T] { Just(value: T), Nothing }\n"
                "val a: Maybe[List[Int]] = Just([])\n"
                "print(match a { Just(v) => len(v), Nothing => -1 })\n"
            )
        )
        assert result.stdout == "0\n"

    def test_generic_enum_multiple_parameters(self, run_source):
        result = run_source(
            core(
                "enum Pair[A, B] { Pair(first: A, second: B) }\n"
                'val p: Pair[Int, String] = Pair(1, "x")\n'
                "print(match p { Pair(a, b) => b })\n"
            )
        )
        assert result.stdout == "x\n"

    def test_generic_enum_function_payload(self, run_source):
        result = run_source(
            core(
                "enum E[T] { F(f: (T) -> Int) }\n"
                "val e: E[Int] = F(do(x: Int) { x + 1 })\n"
                "print(match e { F(f) => f(2) })\n"
            )
        )
        assert result.stdout == "3\n"

    def test_generic_enum_in_class_slot(self, run_source):
        result = run_source(
            core(
                "enum Maybe[T] { Just(value: T), Nothing }\n"
                "class Holder {\n"
                "    val o: Maybe[Int]\n"
                "    def __init__(o: Maybe[Int]) {\n"
                "        this.o = o\n"
                "    }\n"
                "    def get() -> Int {\n"
                "        match this.o { Just(v) => v, Nothing => 0 }\n"
                "    }\n"
                "}\n"
                "print(Holder(Just(5)).get())\n"
                "print(Holder(Nothing).get())\n"
            )
        )
        assert result.stdout == "5\n0\n"

    def test_generic_enum_recursive_payload(self, run_source):
        result = run_source(
            core(
                "enum MyList[T] { Cons(head: T, tail: MyList[T]), Nil }\n"
                "def total(xs: MyList[Int]) -> Int {\n"
                "    match xs { Cons(h, t) => h + total(t), Nil => 0 }\n"
                "}\n"
                "val xs: MyList[Int] = Cons(1, Cons(2, Nil))\n"
                "print(total(xs))\n"
            )
        )
        assert result.stdout == "3\n"

    def test_generic_constructor_as_value_with_expected_function(self, run_source):
        result = run_source(
            core(
                "enum Maybe[T] { Just(value: T), Nothing }\n"
                "val f: (Int) -> Maybe[Int] = Just\n"
                "print(match f(2) { Just(v) => v, Nothing => 0 })\n"
            )
        )
        assert result.stdout == "2\n"

    def test_nested_generic_construction(self, run_source):
        result = run_source(
            core(
                "enum Maybe[T] { Just(value: T), Nothing }\n"
                "val nested = Just(Just(1))\n"
                "print(match nested {\n"
                "    Just(inner) => match inner { Just(v) => v, Nothing => 0 },\n"
                "    Nothing => -1\n"
                "})\n"
            )
        )
        assert result.stdout == "1\n"

    def test_nullary_generic_constructor_requires_expectation(self, caplog):
        check_error(
            caplog,
            "enum Maybe[T] { Just(value: T), Nothing }\nval x = Nothing\n",
            "Cannot infer type argument 'T' of constructor 'Nothing'",
        )

    def test_partial_generic_constructor_requires_expectation(self, caplog):
        check_error(
            caplog,
            "enum MyOutcome[T, E] { Good(value: T), Bad(error: E) }\nval r = Good(1)\n",
            "Cannot infer type argument 'E' of constructor 'Good'",
        )

    def test_conflicting_type_argument_inference(self, caplog):
        check_error(
            caplog,
            'enum Same[T] { Same(a: T, b: T) }\nval x = Same(1, "s")\n',
            "Type parameter 'T' of constructor 'Same' is inferred as both Int and String.",
        )

    def test_expected_payload_mismatch(self, caplog):
        check_error(
            caplog,
            "enum Maybe[T] { Just(value: T), Nothing }\nval x: Maybe[String] = Just(1)\n",
            "Expected String, got Int.",
        )

    def test_bare_generic_type_requires_arguments(self, caplog):
        check_error(
            caplog,
            "enum Maybe[T] { Just(value: T), Nothing }\nval x: Maybe = Nothing\n",
            "Type 'Maybe' requires 1 type argument(s); write Maybe[...].",
        )

    def test_monomorphic_enum_rejects_type_arguments(self, caplog):
        check_error(
            caplog,
            "enum Shape { Circle }\nval x: Shape[Int] = Circle\n",
            "Enum 'Shape' does not take type arguments.",
        )

    def test_generic_type_argument_arity(self, caplog):
        check_error(
            caplog,
            "enum Maybe[T] { Just(value: T), Nothing }\nval x: Maybe[Int, String] = Nothing\n",
            "Type 'Maybe' expects 1 type argument(s), got 2.",
        )

    def test_type_parameter_cannot_shadow_type(self, caplog):
        check_error(
            caplog,
            "enum E[Int] { A }\n",
            "Type parameter 'Int' is already declared or reserved.",
        )

    def test_duplicate_type_parameter(self, caplog):
        check_error(
            caplog,
            "enum E[T, T] { A(x: T) }\n",
            "Duplicate type parameter 'T'.",
        )

    def test_type_parameter_cannot_shadow_enum_name(self, caplog):
        check_error(
            caplog,
            "enum E[E] { A }\n",
            "Type parameter 'E' shadows the enum name.",
        )

    def test_match_payload_binding_uses_scrutinee_arguments(self, caplog):
        check_error(
            caplog,
            "enum Pair[A, B] { Pair(first: A, second: B) }\n"
            "def f(p: Pair[Int, String]) -> Int {\n"
            "    match p { Pair(a, b) => b }\n"
            "}\n",
            "Expected Int, got String.",
        )


class TestCoreVariance:
    def test_covariant_enum(self, run_source):
        result = run_source(
            core(
                "enum Producer[out T] { Get(value: T), Empty }\n"
                "val p: Producer[Int] = Get(3)\n"
                "print(match p { Get(v) => v, Empty => 0 })\n"
            )
        )
        assert result.stdout == "3\n"

    def test_contravariant_enum(self, run_source):
        result = run_source(
            core(
                "enum Consumer[in T] { Use(f: (T) -> Int) }\n"
                "val c: Consumer[Int] = Use(do(x: Int) { x + 1 })\n"
                "print(match c { Use(f) => f(2) })\n"
            )
        )
        assert result.stdout == "3\n"

    def test_covariant_recursive_enum(self, run_source):
        result = run_source(
            core(
                "enum MyList[out T] { Cons(head: T, tail: MyList[T]), Nil }\n"
                "val xs: MyList[Int] = Cons(1, Cons(2, Nil))\n"
                "print(match xs { Cons(h, _) => h, Nil => 0 })\n"
            )
        )
        assert result.stdout == "1\n"

    def test_collections_are_covariant(self, run_source):
        result = run_source(
            core(
                "enum E[out T] {\n"
                "    D(d: Dict[String, T]),\n"
                "    L(xs: List[T]),\n"
                "    P(pair: Tuple[T, Int])\n"
                "}\n"
                'val e: E[Int] = D({: "a": 1 :})\n'
                'print(match e { D(d) => d["a"], _ => 0 })\n'
            )
        )
        assert result.stdout == "1\n"

    def test_covariant_rejects_consumed_position(self, caplog):
        check_error(
            caplog,
            "enum Bad[out T] { B(f: (T) -> Int) }\n",
            "Type parameter 'T' is declared covariant ('out') but appears in a "
            "contravariant position in constructor 'B'.",
        )

    def test_contravariant_rejects_produced_position(self, caplog):
        check_error(
            caplog,
            "enum Bad[in T] { B(value: T) }\n",
            "Type parameter 'T' is declared contravariant ('in') but appears in a "
            "covariant position in constructor 'B'.",
        )

    def test_nested_invariant_parameter_breaks_covariance(self, caplog):
        check_error(
            caplog,
            "enum Inner[T] { I(v: T) }\nenum Outer[out T] { O(x: Inner[T]) }\n",
            "Type parameter 'T' is declared covariant ('out') but appears in an "
            "invariant position in constructor 'O'.",
        )

    def test_nested_contravariance_composes(self, caplog):
        check_error(
            caplog,
            "enum Consumer[in T] { C(f: (T) -> Int) }\n"
            "enum BadWrap[out T] { BW(c: Consumer[T]) }\n",
            "Type parameter 'T' is declared covariant ('out') but appears in a "
            "contravariant position in constructor 'BW'.",
        )

    def test_out_remains_a_valid_identifier(self, run_source):
        result = run_source(core("val out = 1\nprint(out)\n"))
        assert result.stdout == "1\n"

    def test_unknown_variance_annotation_is_rejected(self, caplog):
        check_error(
            caplog,
            "enum E[foo T] { A }\n",
            "Expected 'in' or 'out' before type parameter 'T', got 'foo'.",
        )

    def test_type_parameter_named_out_is_reserved(self, caplog):
        check_error(
            caplog,
            "enum E[out] { A }\n",
            "Type parameter 'out' is already declared or reserved.",
        )


class TestCorePrelude:
    def test_option_and_result_are_always_available(self, run_source):
        result = run_source(
            core(
                "def unwrap(o: Option[Int]) -> Int {\n"
                "    match o { Some(v) => v, None => 0 }\n"
                "}\n"
                "val r: Result[Int, String] = Ok(3)\n"
                "print(unwrap(Some(1)))\n"
                "print(unwrap(None))\n"
                "print(match r { Ok(v) => v, Err(e) => 0 })\n"
            )
        )
        assert result.stdout == "1\n0\n3\n"

    def test_prelude_constructor_inference_and_expectation(self, run_source):
        result = run_source(
            core(
                "val a = Some(5)\n"
                "val xs: Option[List[Int]] = Some([])\n"
                "print(match a { Some(v) => v, None => 0 })\n"
                "print(match xs { Some(v) => len(v), None => -1 })\n"
                "val f: (Int) -> Option[Int] = Some\n"
                "print(match f(2) { Some(v) => v, None => 0 })\n"
            )
        )
        assert result.stdout == "5\n0\n2\n"

    def test_local_binding_can_shadow_prelude_constructor(self, run_source):
        result = run_source(core("def f() -> Int {\n    val Some = 7\n    Some\n}\nprint(f())\n"))
        assert result.stdout == "7\n"

    def test_prelude_type_cannot_be_redeclared(self, caplog):
        check_error(
            caplog,
            "enum Option[T] { O(x: T) }\n",
            "Type 'Option' is declared in the core prelude.",
        )

    def test_prelude_type_cannot_be_redeclared_as_class(self, caplog):
        check_error(
            caplog,
            "class Result { val x: Int = 1 }\n",
            "Type 'Result' is declared in the core prelude.",
        )

    def test_prelude_constructor_cannot_be_redeclared(self, caplog):
        check_error(
            caplog,
            "enum Foo { Some(x: Int) }\n",
            "Constructor 'Some' is declared in the core prelude.",
        )

    def test_prelude_name_cannot_be_redeclared(self, caplog):
        check_error(
            caplog,
            "val Some = 1\n",
            "Name 'Some' is declared in the core prelude.",
        )


class TestCorePatterns:
    def test_literal_patterns(self, run_source):
        result = run_source(
            core(
                "def f(n: Int) -> String {\n"
                "    match n {\n"
                '        0 => "zero",\n'
                '        1 | 2 | 3 => "small",\n'
                '        -1 => "neg",\n'
                '        _ => "other"\n'
                "    }\n"
                "}\n"
                "print(f(0), f(2), f(-1), f(9))\n"
            )
        )
        assert result.stdout == "zero small neg other\n"

    def test_bool_and_string_and_float_literals(self, run_source):
        result = run_source(
            core(
                "def b(v: Bool) -> Int { match v { true => 1, false => 0 } }\n"
                "def s(v: String) -> Int {\n"
                '    match v { "a" => 1, "b" | "c" => 2, _ => 0 }\n'
                "}\n"
                "def f(v: Float) -> Int { match v { 1.5 => 1, -0.5 => 2, _ => 0 } }\n"
                'print(b(true), b(false), s("b"), s("x"), f(1.5), f(-0.5), f(2.0))\n'
            )
        )
        assert result.stdout == "1 0 2 0 1 2 0\n"

    def test_tuple_patterns(self, run_source):
        result = run_source(
            core(
                "def f(p: Tuple[Int, Bool]) -> String {\n"
                "    match p {\n"
                '        (0, true) => "zero-true",\n'
                '        (0, false) => "zero-false",\n'
                '        (n, true) => "true-other",\n'
                '        (n, false) => "false-other"\n'
                "    }\n"
                "}\n"
                "print(f((0, true)), f((0, false)), f((5, true)), f((5, false)))\n"
            )
        )
        assert result.stdout == "zero-true zero-false true-other false-other\n"

    def test_nested_constructor_patterns_are_exhaustive(self, run_source):
        result = run_source(
            core(
                "def f(o: Option[Option[Int]]) -> Int {\n"
                "    match o {\n"
                "        Some(Some(v)) => v,\n"
                "        Some(None) => -1,\n"
                "        None => -2\n"
                "    }\n"
                "}\n"
                "print(f(Some(Some(7))), f(Some(None)), f(None))\n"
            )
        )
        assert result.stdout == "7 -1 -2\n"

    def test_or_pattern_with_bindings(self, run_source):
        result = run_source(
            core(
                "enum Pair { P(a: Int, b: Int) }\n"
                "def f(p: Pair) -> Int {\n"
                "    match p {\n"
                "        P(x, 0) | P(0, x) => x,\n"
                "        P(x, y) => x + y\n"
                "    }\n"
                "}\n"
                "print(f(P(5, 0)), f(P(0, 6)), f(P(2, 3)))\n"
            )
        )
        assert result.stdout == "5 6 5\n"

    def test_guard_can_use_bindings(self, run_source):
        result = run_source(
            core(
                "def f(n: Int) -> String {\n"
                "    match n {\n"
                '        x if x > 0 => "pos",\n'
                '        x if x < 0 => "neg",\n'
                '        _ => "zero"\n'
                "    }\n"
                "}\n"
                "print(f(3), f(-2), f(0))\n"
            )
        )
        assert result.stdout == "pos neg zero\n"

    def test_guards_do_not_establish_coverage(self, caplog):
        check_error(
            caplog,
            "def f(n: Int) -> Int { match n { x if x > 0 => 1 } }\n",
            "Match is not exhaustive; missing: _.",
        )

    def test_int_match_requires_wildcard(self, caplog):
        check_error(
            caplog,
            "def f(n: Int) -> Int { match n { 1 => 1, 2 => 2 } }\n",
            "Match is not exhaustive; missing: _.",
        )

    def test_nested_exhaustiveness_witness(self, caplog):
        check_error(
            caplog,
            "def f(o: Option[Bool]) -> Int {\n    match o { Some(true) => 1, None => -1 }\n}\n",
            "Match is not exhaustive; missing: Some(false).",
        )

    def test_literal_type_mismatch(self, caplog):
        check_error(
            caplog,
            "def f(n: Float) -> Int { match n { 1 => 1, _ => 0 } }\n",
            "Literal pattern of type Int cannot match Float.",
        )

    def test_tuple_pattern_requires_tuple_type(self, caplog):
        check_error(
            caplog,
            "def f(n: Int) -> Int { match n { (x, y) => x, _ => 0 } }\n",
            "Tuple patterns require a tuple type, got Int.",
        )

    def test_tuple_arity_mismatch(self, caplog):
        check_error(
            caplog,
            "def f(p: Tuple[Int, Bool]) -> Int { match p { (a, b, c) => a, _ => 0 } }\n",
            "Tuple pattern has 3 element(s), expected 2.",
        )

    def test_or_pattern_binding_mismatch(self, caplog):
        check_error(
            caplog,
            "enum E { A(x: Int), B(y: Int, z: Int) }\n"
            "print(match A(1) { A(x) | B(x, z) => x, _ => 0 })\n",
            "All alternatives of an or-pattern must bind the same names; mismatch: 'z'.",
        )

    def test_or_pattern_binding_type_mismatch(self, caplog):
        check_error(
            caplog,
            "enum E { A(x: Int), B(x: String) }\nprint(match A(1) { A(x) | B(x) => 0, _ => 1 })\n",
            "Binding 'x' has incompatible types Int and String in an or-pattern.",
        )


class TestCoreEquality:
    def test_adt_equality(self, run_source):
        result = run_source(
            core(
                """enum E { A(x: Int), B }
val a = A(1)
val b = A(1)
val c = A(2)
val d = B
print(a == b, a == c, a == d, a != b)
"""
            )
        )
        assert result.stdout.splitlines() == ["true false false false"]

    def test_nested_and_container_equality(self, run_source):
        result = run_source(
            core(
                """val a: Option[Option[Int]] = Some(Some(1))
val b: Option[Option[Int]] = Some(Some(1))
val c: Option[Option[Int]] = Some(Some(2))
val xs: List[Option[Int]] = [Some(1), None]
val ys: List[Option[Int]] = [Some(1), None]
print(a == b, a == c, xs == ys)
"""
            )
        )
        assert result.stdout.splitlines() == ["true false true"]

    def test_adt_equality_requires_same_type(self, caplog):
        check_error(
            caplog,
            """print(Some(1) == Some("x"))
""",
            "Operator '==' requires both operands to have the same type, "
            "got Option[Int] and Option[String].",
        )

    def test_adt_equality_rejects_function_payloads(self, caplog):
        check_error(
            caplog,
            """enum F { F(f: (Int) -> Int) }
val a: F = F(do(x: Int) { x })
print(a == a)
""",
            "Equality is not supported for enums containing functions in oort-core yet.",
        )

    def test_adt_keys(self, run_source):
        result = run_source(
            core(
                """enum Color { Red, Green }
val d: Dict[Color, Int] = {: Red: 1, Green: 2 :}
val s: Set[Color] = {. Red, Green .}
print(d[Red], s == {. Green, Red .})
"""
            )
        )
        assert result.stdout.splitlines() == ["1 true"]

    def test_adt_with_list_payload_cannot_be_key(self, caplog):
        check_error(
            caplog,
            """enum L { L(xs: List[Int]) }
val s: Set[L] = {. L([]) .}
""",
            "Set elements must be Int, Float, Bool, String, an enum or a "
            "Tuple of key types, got L.",
        )

    def test_class_identity_equality(self, run_source):
        result = run_source(
            core(
                """class C {
    val x: Int

    def __init__(x: Int) {
        this.x = x
    }
}
val a = C(1)
val b = C(1)
print(a == a, a == b, a != b)
"""
            )
        )
        assert result.stdout.splitlines() == ["true false true"]

    def test_class_containers_and_keys(self, run_source):
        result = run_source(
            core(
                """class C {
    val x: Int

    def __init__(x: Int) {
        this.x = x
    }
}
val a = C(1)
val d: Dict[C, Int] = {: a: 7 :}
print(d[a], [a] == [a], [a] == [C(1)])
"""
            )
        )
        assert result.stdout.splitlines() == ["7 true false"]


class TestCoreFunctionValues:
    def test_annotated_lambda_and_call(self, run_source):
        result = run_source(
            core("val inc: (Int) -> Int = do(x: Int) -> Int { x + 1 }\nprint(inc(2))\n")
        )
        assert result.stdout == "3\n"

    def test_inferred_lambda(self, run_source):
        result = run_source(core("val twice = do(x: Int) -> Int { x * 2 }\nprint(twice(4))\n"))
        assert result.stdout == "8\n"

    def test_higher_order_function_and_lambda_argument(self, run_source):
        result = run_source(
            core(
                "def apply(f: (Int) -> Int, x: Int) -> Int { f(x) }\n"
                "print(apply(do(x: Int) -> Int { x * 3 }, 4))\n"
            )
        )
        assert result.stdout == "12\n"

    def test_zero_argument_and_unit_function_values(self, run_source):
        result = run_source(
            core(
                "val zero: () -> Int = do() -> Int { 42 }\n"
                "val show: (Int) -> Unit = do(x: Int) -> Unit { print(x) }\n"
                "print(zero())\nshow(7)\n"
            )
        )
        assert result.stdout == "42\n7\n"

    def test_nested_function_type(self, run_source):
        result = run_source(
            core(
                "val apply: ((Int) -> Int) -> Int = "
                "do(g: (Int) -> Int) -> Int { g(1) }\n"
                "print(apply(do(x: Int) -> Int { x + 1 }))\n"
            )
        )
        assert result.stdout == "2\n"

    def test_closure_over_outer_local(self, run_source):
        result = run_source(
            core(
                "def make(n: Int) -> (Int) -> Int {\n"
                "    do(x: Int) -> Int { x + n }\n"
                "}\n"
                "val add10 = make(10)\nprint(add10(5))\n"
            )
        )
        assert result.stdout == "15\n"

    def test_lambda_return_inferred_without_annotation(self, run_source):
        result = run_source(core("val inc = do(x: Int) { x + 1 }\nprint(inc(2))\n"))
        assert result.stdout == "3\n"

    def test_lambda_return_from_expected_type(self, run_source):
        result = run_source(core("val f: (Int) -> Int = do(x: Int) { x * 2 }\nprint(f(4))\n"))
        assert result.stdout == "8\n"

    def test_lambda_return_inferred_as_argument(self, run_source):
        result = run_source(
            core(
                "def apply(f: (Int) -> Int, x: Int) { f(x) }\n"
                "print(apply(do(x: Int) { x * 3 }, 4))\n"
            )
        )
        assert result.stdout == "12\n"

    def test_lambda_unit_return_inferred(self, run_source):
        result = run_source(core("val show = do(x: Int) { print(x) }\nshow(7)\n"))
        assert result.stdout == "7\n"

    def test_currying_with_inferred_returns(self, run_source):
        result = run_source(
            core("def make(n: Int) { do(x: Int) { x + n } }\nval add5 = make(5)\nprint(add5(3))\n")
        )
        assert result.stdout == "8\n"


class TestCoreFunctionValueRejections:
    def test_anonymous_lambda_is_rejected(self, caplog):
        check_error(
            caplog,
            "val f = do: 1\n",
            "Lambdas without an explicit parameter list are not supported",
        )

    def test_lambda_parameter_annotation_required(self, caplog):
        check_error(
            caplog,
            "val f: (Int) -> Int = do(x) -> Int { x }\n",
            "Parameter 'x' requires a type annotation",
        )

    def test_lambda_uninferrable_return_needs_annotation(self, caplog):
        # Without an expected return type, a lambda body that cannot infer
        # (an empty collection) still requires an annotation.
        check_error(
            caplog,
            "val f = do(x: Int) { [] }\n",
            "Cannot infer the element type of an empty List",
        )

    def test_function_type_mismatch(self, caplog):
        check_error(
            caplog,
            "val f: (Int) -> Bool = do(x: Int) -> Int { x }\n",
            "Expected (Int) -> Bool, got (Int) -> Int.",
        )

    def test_unit_parameter_is_rejected(self, caplog):
        check_error(
            caplog,
            "val f: (Unit) -> Int = do(x: Unit) -> Int { 1 }\n",
            "Unit is only allowed as a function return type",
        )

    def test_generic_lambda_is_rejected(self, caplog):
        check_error(
            caplog,
            "val f = do[T](x: Int) -> Int { x }\n",
            "Generic functions are not implemented yet.",
        )

    def test_default_parameter_in_lambda_is_rejected(self, caplog):
        check_error(
            caplog,
            "val f: (Int) -> Int = do(x: Int = 1) -> Int { x }\n",
            "Defaults, keyword-only/positional-only markers",
        )

    def test_function_value_is_not_printable(self, caplog):
        check_error(
            caplog,
            "val f = do(x: Int) -> Int { x }\nprint(f)\n",
            "only accepts Int, Float, Bool, String, Unit, enum or collection",
        )


class TestCoreCurriedFunctions:
    def test_right_associative_function_types_and_chained_calls(self, run_source):
        result = run_source(
            core(
                "val add: Int -> Int -> Int = "
                "do(x: Int) -> Int -> Int { do(y: Int) -> Int { x + y } }\n"
                "print(add(1)(2))\n"
                "val same: Int -> (Int -> Int) = add\n"
                "print(same(3)(4))\n"
            )
        )
        assert result.stdout == "3\n7\n"

    def test_parenthesized_function_parameter_type(self, run_source):
        result = run_source(
            core(
                "val apply: (Int -> Int) -> Int = "
                "do(f: Int -> Int) -> Int { f(1) }\n"
                "print(apply(do(x: Int) -> Int { x + 1 }))\n"
            )
        )
        assert result.stdout == "2\n"

    def test_non_callable_expression(self, caplog):
        check_error(
            caplog,
            "print((1)(2))\n",
            "Expression is not callable.",
        )


class TestCoreExpectedTypes:
    def test_annotation_propagates_into_if_and_block(self, run_source):
        result = run_source(
            core("val a: Int = if true { 1 } else { 2 }\nval b: Int = { 3 }\nprint(a)\nprint(b)\n")
        )
        assert result.stdout == "1\n3\n"

    def test_function_body_expected_type_reaches_branches(self, run_source):
        result = run_source(
            core(
                "def pick(flag: Bool) -> Int { if flag { 1 } else { 2 } }\n"
                "print(pick(true))\nprint(pick(false))\n"
            )
        )
        assert result.stdout == "1\n2\n"

    def test_assignment_and_return_propagate_expected_types(self, run_source):
        result = run_source(
            core(
                "var x = 0\nx = if true { 4 } else { 5 }\n"
                "def f(flag: Bool) -> Int { return if flag { 6 } else { 7 } }\n"
                "print(x)\nprint(f(false))\n"
            )
        )
        assert result.stdout == "4\n7\n"

    def test_match_arms_receive_expected_type(self, run_source):
        result = run_source(
            core("enum E { A, B }\nval x: Int = match A { A => 1, B => 2 }\nprint(x)\n")
        )
        assert result.stdout == "1\n"

    def test_if_without_else_needs_unit(self, caplog):
        check_error(
            caplog,
            "val x: Int = if true { 1 }\n",
            "An if without else has type Unit, expected Int.",
        )

    def test_block_last_expression_expected_type(self, caplog):
        check_error(
            caplog,
            "val x: Int = { 1\ntrue }\n",
            "Expected Int, got Bool.",
        )

    def test_match_arm_expected_type_error(self, caplog):
        check_error(
            caplog,
            "enum E { A, B }\nval x: Int = match A { A => 1, B => true }\n",
            "Expected Int, got Bool.",
        )

    def test_return_expected_type_reaches_branches(self, caplog):
        check_error(
            caplog,
            "def f(flag: Bool) -> Int { return if flag { 1 } else { true } }\n",
            "Expected Int, got Bool.",
        )


def test_call_argument_receives_expected_type(caplog):
    check_error(
        caplog,
        "def f(x: Int) -> Int { x }\nval y = f(if true { 1 } else { true })\n",
        "Expected Int, got Bool.",
    )


class TestCoreCollections:
    def test_list_inference_index_and_length(self, run_source):
        result = run_source(core("val xs = [3, 1, 2]\nprint(xs[1], len(xs))\nprint(xs)\n"))
        assert result.stdout == "1 3\n[3, 1, 2]\n"

    def test_empty_collections_use_annotations(self, run_source):
        result = run_source(
            core(
                "val xs: List[Int] = []\n"
                "val s: Set[String] = {. .}\n"
                "val d: Dict[String, Int] = {: :}\n"
                "print(xs, len(s), len(d))\n"
            )
        )
        assert result.stdout == "[] 0 0\n"

    def test_empty_literal_expected_type_reaches_call_and_return(self, run_source):
        result = run_source(
            core(
                "def count(xs: List[Int]) -> Int { len(xs) }\n"
                "def none() -> List[Int] { [] }\n"
                "print(count([]), none())\n"
            )
        )
        assert result.stdout == "0 []\n"

    def test_tuple_literal_and_literal_index(self, run_source):
        result = run_source(
            core(
                "val pair: Tuple[Int, Bool] = (7, true)\n"
                "print(pair[0], pair[1], len(pair))\n"
                "print((1, 2)[-1])\n"
            )
        )
        assert result.stdout == "7 true 2\n2\n"

    def test_uniform_tuple_allows_dynamic_index(self, run_source):
        result = run_source(core("val xs = (1, 2)\nvar i = 1\nprint(xs[i])\n"))
        assert result.stdout == "2\n"

    def test_dict_index_and_length(self, run_source):
        result = run_source(
            core(
                'val scores: Dict[String, Int] = {: "a": 1, "b": 2 :}\n'
                'print(scores["b"], len(scores))\n'
                "print(scores)\n"
            )
        )
        assert result.stdout == "2 2\n{: a: 1, b: 2 :}\n"

    def test_nested_collection_types(self, run_source):
        result = run_source(
            core(
                'val table: Dict[String, List[Int]] = {: "a": [1, 2] :}\n'
                "val rows: List[Tuple[Int, Bool]] = [(1, true)]\n"
                'print(table["a"][1], rows[0][1], len(table))\n'
            )
        )
        assert result.stdout == "2 true 1\n"

    def test_string_index_and_length(self, run_source):
        result = run_source(core('print("abc"[1], len("abc"))\n'))
        assert result.stdout == "b 3\n"

    def test_empty_tuple_is_inferred(self, run_source):
        result = run_source(core("val t = ()\nprint(t, len(t))\n"))
        assert result.stdout == "() 0\n"

    def test_collection_equality(self, run_source):
        result = run_source(
            core(
                "print([1] == [1], [1] == [2])\n"
                "print((1, true) == (1, true), [1] != [2])\n"
                'print({: "a": 1 :} == {: "a": 1 :})\n'
            )
        )
        assert result.stdout == "true false\ntrue true\ntrue\n"

    def test_empty_list_without_annotation_is_rejected(self, caplog):
        check_error(
            caplog,
            "val xs = []\n",
            "Cannot infer the element type of an empty List",
        )

    def test_empty_dict_without_annotation_is_rejected(self, caplog):
        check_error(
            caplog,
            "val d = {: :}\n",
            "Cannot infer the key/value types of an empty Dict",
        )

    def test_heterogeneous_list_is_rejected(self, caplog):
        check_error(
            caplog,
            "val xs = [1, true]\n",
            "List elements have incompatible types: Int and Bool.",
        )

    def test_unit_element_is_rejected(self, caplog):
        check_error(
            caplog,
            "val xs = [print(1)]\n",
            "Unit cannot be stored in a List",
        )

    def test_set_elements_must_be_key_types(self, caplog):
        check_error(
            caplog,
            "val s = {. [1] .}\n",
            "Set elements must be Int, Float, Bool, String, an enum or a Tuple",
        )

    def test_dict_keys_must_be_key_types(self, caplog):
        check_error(
            caplog,
            "val d = {: [1]: 2 :}\n",
            "Dict keys must be Int, Float, Bool, String, an enum or a Tuple",
        )

    def test_container_annotations_validate_key_types(self, caplog):
        check_error(
            caplog,
            "val s: Set[List[Int]] = {. .}\n",
            "Set elements must be Int, Float, Bool, String, an enum or a Tuple",
        )

    def test_tuple_arity_mismatch(self, caplog):
        check_error(
            caplog,
            "val pair: Tuple[Int, Bool] = (1,)\n",
            "Tuple has 1 elements, expected 2.",
        )

    def test_tuple_literal_out_of_range(self, caplog):
        check_error(
            caplog,
            "print((1, 2)[5])\n",
            "Index 5 is out of range for Tuple[Int, Int].",
        )

    def test_heterogeneous_tuple_needs_literal_index(self, caplog):
        check_error(
            caplog,
            'val pair = (1, "a")\nvar i = 1\nprint(pair[i])\n',
            "Tuple subscripts with a non-literal index require all elements",
        )

    def test_list_index_must_be_int(self, caplog):
        check_error(
            caplog,
            "val xs = [1]\nprint(xs[true])\n",
            "Expected Int, got Bool.",
        )

    def test_dict_index_must_match_key_type(self, caplog):
        check_error(
            caplog,
            'val d: Dict[String, Int] = {: "a": 1 :}\nprint(d[1])\n',
            "Expected String, got Int.",
        )

    def test_set_is_not_subscriptable(self, caplog):
        check_error(
            caplog,
            "val s = {. 1 .}\nprint(s[0])\n",
            "Type Set[Int] is not subscriptable",
        )

    def test_cross_kind_collection_equality_is_rejected(self, caplog):
        check_error(
            caplog,
            "print([1] == (1,))\n",
            "requires both operands to have the same collection type",
        )

    def test_bare_container_type_requires_arguments(self, caplog):
        check_error(
            caplog,
            "val xs: List = []\n",
            "Type 'List' requires type arguments",
        )

    def test_container_type_arity(self, caplog):
        check_error(
            caplog,
            "val xs: List[Int, Bool] = []\n",
            "Type 'List' expects 1 type argument(s), got 2.",
        )

    def test_len_requires_a_collection_or_string(self, caplog):
        check_error(
            caplog,
            "print(len(1))\n",
            "The built-in 'len' only accepts String or collection arguments",
        )


class TestCoreLoops:
    def test_for_over_collections_and_string(self, run_source):
        result = run_source(
            core(
                "val xs = [1, 2, 3]\n"
                "var total = 0\n"
                "for x in xs { total = total + x }\n"
                "print(total)\n"
                'for key in {: "a": 1, "b": 2 :} { print(key) }\n'
                'for ch in "ab" { print(ch) }\n'
            )
        )
        assert result.stdout == "6\na\nb\na\nb\n"

    def test_for_over_uniform_tuple_and_single_element_set(self, run_source):
        result = run_source(core("for n in (5, 6) { print(n) }\nfor x in {. 4 .} { print(x) }\n"))
        assert result.stdout == "5\n6\n4\n"

    def test_while_continue_and_break(self, run_source):
        result = run_source(
            core(
                "var i = 0\n"
                "while i < 5 {\n"
                "    i = i + 1\n"
                "    if i == 2: continue\n"
                "    if i == 4: break\n"
                "    print(i)\n"
                "}\n"
            )
        )
        assert result.stdout == "1\n3\n"

    def test_return_from_inside_for(self, run_source):
        result = run_source(
            core(
                "def first_positive(xs: List[Int]) -> Int {\n"
                "    for x in xs {\n"
                "        if x > 0 { return x }\n"
                "    }\n"
                "    0\n"
                "}\n"
                "print(first_positive([-2, 3, 4]))\n"
            )
        )
        assert result.stdout == "3\n"

    def test_loop_variable_annotation_is_checked(self, run_source):
        result = run_source(core("for x: Int in [1, 2] { print(x) }\n"))
        assert result.stdout == "1\n2\n"

    def test_loop_variable_shadows_outer_binding(self, run_source):
        result = run_source(core("var x = 9\nfor x in [1] { print(x) }\nprint(x)\n"))
        assert result.stdout == "1\n9\n"

    def test_while_condition_must_be_bool(self, caplog):
        check_error(
            caplog,
            "while 1 { print(1) }\n",
            "while condition must be Bool",
        )

    def test_loop_variable_annotation_mismatch(self, caplog):
        check_error(
            caplog,
            "for x: Bool in [1] { print(x) }\n",
            "Expected Bool, got Int.",
        )

    def test_multiple_loop_variables_are_rejected(self, caplog):
        check_error(
            caplog,
            "for a, b in [1] { print(a) }\n",
            "Multiple loop variables are not supported",
        )

    def test_iterating_a_non_iterable_is_rejected(self, caplog):
        check_error(
            caplog,
            "for x in 1 { print(x) }\n",
            "Cannot iterate over values of type Int",
        )

    def test_iterating_a_heterogeneous_tuple_is_rejected(self, caplog):
        check_error(
            caplog,
            "val pair = (1, true)\nfor x in pair { print(x) }\n",
            "Cannot iterate a Tuple with heterogeneous element types",
        )

    def test_break_value_is_rejected(self, caplog):
        check_error(
            caplog,
            "while true { break 1 }\n",
            "break values are not supported",
        )


class TestCoreClasses:
    def test_slots_constructor_and_methods(self, run_source):
        result = run_source(
            core(
                "class Counter {\n"
                "    val start: Int = 10\n"
                "    var count: Int\n"
                "    def __init__(step: Int) {\n"
                "        this.count = this.start\n"
                "        this.count = this.count + step\n"
                "    }\n"
                "    def get() -> Int { this.count }\n"
                "    def bump() -> Unit { this.count = this.count + 1 }\n"
                "}\n"
                "val c = Counter(5)\n"
                "print(c.get())\n"
                "c.bump()\n"
                "print(c.get(), c.start)\n"
            )
        )
        assert result.stdout == "15\n16 10\n"

    def test_val_slots_assigned_from_parameters(self, run_source):
        result = run_source(
            core(
                "class Point {\n"
                "    val x: Int\n"
                "    val y: Int\n"
                "    def __init__(x: Int, y: Int) {\n"
                "        this.x = x\n"
                "        this.y = y\n"
                "    }\n"
                "    def sum() -> Int { this.x + this.y }\n"
                "}\n"
                "print(Point(2, 3).sum())\n"
            )
        )
        assert result.stdout == "5\n"

    def test_infer_method_return_from_tail_expression(self, run_source):
        result = run_source(
            core(
                "class Point {\n"
                "    val x: Int\n"
                "    val y: Int\n"
                "    def __init__(x: Int, y: Int) { this.x = x\n this.y = y }\n"
                "    def sum() { this.x + this.y }\n"
                "}\n"
                "print(Point(2, 3).sum())\n"
            )
        )
        assert result.stdout == "5\n"

    def test_infer_method_return_backward_call(self, run_source):
        result = run_source(
            core(
                "class C {\n"
                "    val x: Int = 1\n"
                "    def get() { this.x }\n"
                "    def bump() { this.get() + 1 }\n"
                "}\n"
                "val c = C()\nprint(c.get(), c.bump())\n"
            )
        )
        assert result.stdout == "1 2\n"

    def test_infer_method_return_forward_call(self, run_source):
        # a() calls b() defined later; dependency-order inference resolves it.
        result = run_source(
            core("class C {\n    def a() { this.b() + 1 }\n    def b() { 10 }\n}\nprint(C().a())\n")
        )
        assert result.stdout == "11\n"

    def test_infer_method_unit_return(self, run_source):
        result = run_source(
            core(
                "class C {\n"
                "    var n: Int = 0\n"
                "    def bump() { this.n = this.n + 1 }\n"
                "    def get() { this.n }\n"
                "}\n"
                "val c = C()\nc.bump()\nc.bump()\nprint(c.get())\n"
            )
        )
        assert result.stdout == "2\n"

    def test_annotated_method_calls_inferred_method(self, run_source):
        result = run_source(
            core(
                "class C {\n"
                "    def base() { 5 }\n"
                "    def twice() -> Int { this.base() * 2 }\n"
                "}\n"
                "print(C().twice())\n"
            )
        )
        assert result.stdout == "10\n"

    def test_annotated_recursive_method_still_works(self, run_source):
        result = run_source(
            core(
                "class C {\n"
                "    def fact(n: Int) -> Int { if n <= 1 { 1 } else { n * this.fact(n - 1) } }\n"
                "}\n"
                "print(C().fact(5))\n"
            )
        )
        assert result.stdout == "120\n"

    def test_slot_initializers_run_before_constructor(self, run_source):
        result = run_source(
            core(
                "def mark(n: Int) -> Int {\n"
                "    print(n)\n"
                "    n\n"
                "}\n"
                "class C {\n"
                "    val a: Int = mark(1)\n"
                "    val b: Int = mark(2)\n"
                "    def __init__() { print(3) }\n"
                "}\n"
                "C()\n"
            )
        )
        assert result.stdout == "1\n2\n3\n"

    def test_class_types_in_annotations_and_methods(self, run_source):
        result = run_source(
            core(
                "class Box {\n"
                "    val value: Int\n"
                "    def __init__(value: Int) { this.value = value }\n"
                "    def next() -> Box { Box(this.value + 1) }\n"
                "    def me() -> Box { this }\n"
                "}\n"
                "def unwrap(box: Box) -> Int { box.value }\n"
                "val b = Box(1).next().next().me()\n"
                "print(unwrap(b))\n"
            )
        )
        assert result.stdout == "3\n"

    def test_empty_class_and_method_reference(self, run_source):
        result = run_source(
            core(
                "class Empty {\n"
                "    def answer() -> Int { 42 }\n"
                "}\n"
                "val e = Empty()\n"
                "val f = e.answer\n"
                "print(f())\n"
            )
        )
        assert result.stdout == "42\n"

    def test_class_without_constructor_and_initialized_slots(self, run_source):
        result = run_source(
            core(
                "class Defaults {\n"
                "    val answer: Int = 7\n"
                '    var name: String = "oort"\n'
                "}\n"
                "val d = Defaults()\n"
                "print(d.answer, d.name)\n"
            )
        )
        assert result.stdout == "7 oort\n"

    def test_slot_initializer_uses_expected_collection_type(self, run_source):
        result = run_source(
            core(
                "class Bag {\n"
                "    val xs: List[Int] = []\n"
                "    def size() -> Int { len(this.xs) }\n"
                "}\n"
                "print(Bag().size())\n"
            )
        )
        assert result.stdout == "0\n"

    def test_definite_assignment_accepts_both_branches(self, run_source):
        result = run_source(
            core(
                "class C {\n"
                "    val x: Int\n"
                "    def __init__(flag: Bool) {\n"
                "        if flag { this.x = 1 } else { this.x = 2 }\n"
                "    }\n"
                "}\n"
                "print(C(true).x, C(false).x)\n"
            )
        )
        assert result.stdout == "1 2\n"

    def test_multiple_bases_are_rejected(self, caplog):
        check_error(
            caplog,
            "class A {}\nclass B {}\nclass C < A, B {}\n",
            "Only a single base class is supported",
        )

    def test_metaclass_is_rejected(self, caplog):
        check_error(
            caplog,
            "class A {}\nclass B :: A {}\n",
            "Metaclasses are not supported",
        )

    def test_generic_class_is_rejected(self, caplog):
        check_error(
            caplog,
            "class Box[T] {}\n",
            "Generic classes are not implemented yet.",
        )

    def test_class_method_is_rejected(self, caplog):
        check_error(
            caplog,
            "class C { def class.f() -> Int { 1 } }\n",
            "Only plain instance methods are supported",
        )

    def test_operator_method_is_rejected(self, caplog):
        check_error(
            caplog,
            'class C { def operator "+"(x: Int) -> Int { x } }\n',
            "Only plain instance methods are supported",
        )

    def test_other_special_method_is_rejected(self, caplog):
        check_error(
            caplog,
            'class C { def __str__() -> String { "x" } }\n',
            "Special method '__str__' is not supported",
        )

    def test_class_body_statement_is_rejected(self, caplog):
        check_error(
            caplog,
            "class C {\n    print(1)\n}\n",
            "Only slot and method declarations are allowed",
        )

    def test_slot_requires_annotation(self, caplog):
        check_error(
            caplog,
            "class C { val x = 1 }\n",
            "Slot 'x' requires a type annotation",
        )

    def test_slot_rejects_unit(self, caplog):
        check_error(
            caplog,
            "class C { val x: Unit = print(1) }\n",
            "Unit is only allowed as a function return type",
        )

    def test_slot_rejects_special_name(self, caplog):
        check_error(
            caplog,
            "class C { val __x__: Int = 1 }\n",
            "Slot name '__x__' is reserved",
        )

    def test_missing_constructor_for_uninitialized_slots(self, caplog):
        check_error(
            caplog,
            "class C { val x: Int }\n",
            "has slots without initializers but no __init__: x",
        )

    def test_definite_assignment_requires_all_branches(self, caplog):
        check_error(
            caplog,
            "class C {\n"
            "    val x: Int\n"
            "    def __init__(flag: Bool) {\n"
            "        if flag { this.x = 1 }\n"
            "    }\n"
            "}\n",
            "Constructor must initialize slot(s): x.",
        )

    def test_read_before_assignment(self, caplog):
        check_error(
            caplog,
            "class C {\n"
            "    val x: Int\n"
            "    def __init__() {\n"
            "        print(this.x)\n"
            "        this.x = 1\n"
            "    }\n"
            "}\n",
            "Slot 'x' is read before it is definitely assigned.",
        )

    def test_early_return_before_assignment(self, caplog):
        check_error(
            caplog,
            "class C {\n    var x: Int\n    def __init__() { return }\n}\n",
            "Constructor returns before initializing slot(s): x.",
        )

    def test_val_with_initializer_is_not_reassignable(self, caplog):
        check_error(
            caplog,
            "class C {\n    val x: Int = 0\n    def __init__() { this.x = 1 }\n}\n",
            "Cannot assign to read-only slot 'x'; it has an initializer.",
        )

    def test_val_without_initializer_can_be_assigned_only_once(self, caplog):
        check_error(
            caplog,
            "class C {\n"
            "    val x: Int\n"
            "    def __init__(flag: Bool) {\n"
            "        if flag { this.x = 1 }\n"
            "        this.x = 2\n"
            "    }\n"
            "}\n",
            "Read-only slot 'x' may already be assigned; it can be assigned only once.",
        )

    def test_val_is_read_only_in_methods(self, caplog):
        check_error(
            caplog,
            "class C {\n"
            "    val x: Int\n"
            "    def __init__() { this.x = 1 }\n"
            "    def set() -> Unit { this.x = 2 }\n"
            "}\n",
            "Cannot assign to read-only slot 'x'",
        )

    def test_val_cannot_be_assigned_in_a_loop(self, caplog):
        check_error(
            caplog,
            "class C {\n"
            "    val x: Int\n"
            "    def __init__() {\n"
            "        for i in [1, 2] { this.x = i }\n"
            "    }\n"
            "}\n",
            "Read-only slot 'x' cannot be assigned inside a loop.",
        )

    def test_definite_assignment_through_loops_and_member_writes(self, run_source):
        result = run_source(
            core(
                """class D { var v: Int = 0 }
class C {
    val x: Int
    def __init__() {
        var i: Int = 0
        while i < 1 { i = i + 1 }
        for k in [1, 2] { print(k) }
        var d = D()
        d.v = 1
        this.x = d.v
    }
}
print(C().x)
"""
            )
        )
        assert result.stdout == "1\n2\n1\n"

    def test_definite_assignment_through_match(self, run_source):
        result = run_source(
            core(
                """enum E { A, B }
class C {
    val x: Int
    def __init__(e: E) {
        match e {
            A => { this.x = 1 },
            B => { this.x = 2 }
        }
    }
}
print(C(A).x, C(B).x)
"""
            )
        )
        assert result.stdout == "1 2\n"

    def test_definite_assignment_through_break_and_continue(self, run_source):
        result = run_source(
            core(
                """class C {
    val x: Int
    def __init__() {
        var i: Int = 0
        while i < 3 {
            i = i + 1
            if i == 1 { continue }
            break
        }
        this.x = 1
    }
}
print(C().x)
"""
            )
        )
        assert result.stdout == "1\n"

    def test_definite_assignment_merges_early_returns(self, run_source):
        result = run_source(
            core(
                """class A {
    val x: Int
    def __init__(flag: Bool) {
        this.x = 1
        if flag { return }
    }
}
class B {
    val x: Int
    def __init__(flag: Bool) {
        this.x = 1
        if flag { print(1) } else { return }
    }
}
print(A(false).x, B(true).x)
"""
            )
        )
        assert result.stdout == "1\n1 1\n"

    def test_definite_assignment_all_match_arms_return(self, run_source):
        result = run_source(
            core(
                """enum E { A, B }
class C {
    val x: Int
    def __init__(e: E) {
        this.x = 1
        match e {
            A => { return },
            B => { return }
        }
    }
}
print(C(A).x)
"""
            )
        )
        assert result.stdout == "1\n"

    def test_definite_assignment_skips_unreachable_statements(self, run_source):
        result = run_source(
            core(
                """class C {
    val x: Int
    def __init__() {
        { this.x = 1 }
        return
        print(2)
    }
}
print(C().x)
"""
            )
        )
        assert result.stdout == "1\n"

    def test_undeclared_slot_assignment(self, caplog):
        check_error(
            caplog,
            "class C {\n    val x: Int = 1\n    def set() -> Unit { this.y = 2 }\n}\n",
            "Class 'C' has no slot 'y'.",
        )

    def test_method_assignment_is_rejected(self, caplog):
        check_error(
            caplog,
            "class C {\n    def f() -> Int { 1 }\n    def set() -> Unit { this.f = 2 }\n}\n",
            "Cannot assign to method 'f'.",
        )

    def test_unknown_member_read(self, caplog):
        check_error(
            caplog,
            "class C {\n    val x: Int = 1\n    def f() -> Int { this.missing }\n}\n",
            "Class 'C' has no member 'missing'.",
        )

    def test_constructor_argument_types(self, caplog):
        check_error(
            caplog,
            "class C {\n    val x: Int\n    def __init__(x: Int) { this.x = x }\n}\nC(true)\n",
            "Expected Int, got Bool.",
        )

    def test_method_argument_types(self, caplog):
        check_error(
            caplog,
            "class C {\n"
            "    val x: Int = 1\n"
            "    def add(n: Int) -> Int { this.x + n }\n"
            "}\n"
            "C().add(true)\n",
            "Expected Int, got Bool.",
        )

    def test_attribute_fallback_is_rejected(self, caplog):
        check_error(
            caplog,
            """\
class C {
    val x: Int = 1
    def on_missing(name: String) -> Int { 0 }
}
""",
            "Attribute fallback hooks are only supported in oort-object.",
        )

    def test_class_instances_are_not_printable(self, caplog):
        check_error(
            caplog,
            "class C { val x: Int = 1 }\nprint(C())\n",
            "got C.",
        )

    def test_type_name_collision_with_enum_or_class(self, caplog):
        check_error(
            caplog,
            "enum Foo { A }\nclass Foo {}\n",
            "Type name 'Foo' is already declared or reserved",
        )
        check_error(
            caplog,
            "class Foo {}\nenum Foo { A }\n",
            "Type name 'Foo' is already declared.",
        )

    def test_class_must_be_top_level(self, caplog):
        check_error(
            caplog,
            "def f() -> Unit {\n    class C {}\n    print(1)\n}\n",
            "Class declarations are only allowed at module top level",
        )

    def test_constructor_return_type_must_be_unit(self, caplog):
        check_error(
            caplog,
            "class C {\n    val x: Int = 1\n    def __init__() -> Int { this.x }\n}\n",
            "must return Unit",
        )
