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

    def test_missing_return_annotation(self, caplog):
        check_error(
            caplog,
            "def f(x: Int) { x }\n",
            "requires a return type annotation",
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
            "var x: Float = 1\n",
            "Unknown type 'Float' in oort-core",
        )

    def test_non_name_annotation(self, caplog):
        check_error(
            caplog,
            "var x: List[Int] = 1\n",
            "Only Int, Bool and Unit type names are supported",
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
            "is declared to return Int, but its body has type Bool",
        )

    def test_function_missing_return_on_some_path(self, caplog):
        check_error(
            caplog,
            "def f(n: Int) -> Int { if n < 0 { return 0 } }\n",
            "is declared to return Int, but its body has type Unit",
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

    def test_arithmetic_requires_int(self, caplog):
        check_error(
            caplog,
            "def f(x: Int) -> Int { x + true }\n",
            "Expected Int, got Bool.",
        )

    def test_comparison_requires_int(self, caplog):
        check_error(
            caplog,
            "print(1 < true)\n",
            "Expected Int, got Bool.",
        )

    def test_equality_requires_same_type(self, caplog):
        check_error(
            caplog,
            "print(1 == true)\n",
            "requires two Int or two Bool operands",
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

    def test_integer_division_is_rejected(self, caplog):
        check_error(
            caplog,
            "print(1 / 2)\n",
            "The '/' operator is not supported in oort-core yet",
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
            ("class A {}\n", "Classes are not supported"),
            ("while true { print(1) }\n", "Loops are not supported"),
            ("print([1])\n", "Lists are not supported"),
            ("print((1, 2))\n", "Tuples are not supported"),
            ("print({: 1: 2 :})\n", "Dicts are not supported"),
            ("print({. 1 .})\n", "Sets are not supported"),
            ("print(1.5)\n", "Float is not supported"),
            ('print("x")\n', "String is not supported"),
            ("print(null)\n", "null is not supported"),
            ("val f = do: 1\n", "Lambdas are not supported"),
            ("var x = [1]\nprint(x[0])\n", "Lists are not supported"),
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
            compiler.run_string(core("var xs = [1]\nprint(xs)\n"))
        assert "Lists are not supported" in caplog.text
        assert "Cannot infer a usable type" not in caplog.text


if __name__ == "__main__":
    pytest.main([__file__])
