#! /usr/bin/env python

"""Generic functions: type parameters with inference and monomorphization (OP 0033)."""

import pytest

from oort_lang.driver.compiler import CompilerError
from tests.helpers import get_compiler

GENERIC_FUNCTIONS = """#lang oort-core

def id[T](x: T) -> T { x }
def wrap[T](x: T) -> List[T] { [x, x] }
def depth[T](xs: List[List[T]]) -> T { xs[0][0] }
def pair[A, B](a: A, b: B) -> Tuple[A, B] { (a, b) }
def count_all[T](xs: List[T]) -> Int {
    if len(xs) == 0 { 0 } else { 1 + count_all(xs[1:]) }
}

print(id(true), wrap(7), wrap("a"))
print(depth([[1, 2], [3]]), depth([["x"]]))
print(pair(1, "x"), pair(false, 2.5))
print(count_all([1, 2, 3]), count_all(["a", "b"]))
val opt: Option[Int] = Some(id(9))
print(opt)
"""

GENERIC_FUNCTIONS_OUTPUT = "true [7, 7] [a, a]\n1 x\n(1, x) (false, 2.5)\n3 2\nSome(9)\n"


@pytest.mark.parametrize("target", ["eval", "vm", "tvm"])
def test_generic_functions_match_across_targets(capsys, target):
    compiler = get_compiler(["-t", target, "NOT_EXIST"])
    compiler.run_string(GENERIC_FUNCTIONS)
    assert capsys.readouterr().out == GENERIC_FUNCTIONS_OUTPUT


@pytest.mark.parametrize(
    ("source", "message"),
    [
        # Unsolvable type argument (mirrors `val x = None` for ADTs).
        (
            "def empty[T]() -> List[T] { [] }\nprint(len(empty()))",
            "Cannot infer type argument 'T'",
        ),
        # No bounds: operators on the rigid parameter are rejected.
        (
            "def inc[T](x: T) -> T { x + 1 }\nprint(inc(1))",
            "got T and Int",
        ),
        # Body must match the declared (generic) return type.
        (
            "def bad[T](x: Int) -> T { x }\nprint(1)",
            "Expected T, got Int",
        ),
        # Bounds and variance are explicit rejections.
        (
            "def f[T: Bound](x: T) -> T { x }\nprint(1)",
            "Type parameter bounds are not supported in oort-core yet",
        ),
        (
            "def f[out T](x: T) -> T { x }\nprint(1)",
            "Type parameter variance is not supported on functions",
        ),
        # Generic functions require an explicit return annotation.
        (
            "def f[T](x: T) { x }\nprint(1)",
            "requires a return type annotation",
        ),
        # A generic without arguments cannot bind its parameters as a value.
        (
            "def id[T](x: T) -> T { x }\nval f = id\nprint(1)",
            "Cannot infer type argument 'T'",
        ),
    ],
)
def test_generic_function_errors(caplog, source, message):
    compiler = get_compiler("NOT_EXIST -t tvm")
    with pytest.raises((SystemExit, CompilerError)):
        compiler.run_string("#lang oort-core\n" + source)
    assert message in caplog.text


def test_expected_type_drives_instantiation(capsys):
    compiler = get_compiler("NOT_EXIST -t tvm")
    compiler.run_string(
        "#lang oort-core\n"
        "def wrap[T](x: T) -> Option[T] { Some(x) }\n"
        "val a: Option[Int] = wrap(3)\n"
        'val b: Option[String] = wrap("s")\n'
        "print(a, b)\n"
    )
    assert capsys.readouterr().out == "Some(3) Some('s')\n"


def test_generic_value_with_expected_function_type(capsys):
    # `val f: (Int) -> Int = id` unifies the scheme against the annotation.
    compiler = get_compiler("NOT_EXIST -t vm")
    compiler.run_string(
        "#lang oort-core\ndef id[T](x: T) -> T { x }\nval f: (Int) -> Int = id\nprint(f(5))\n"
    )
    assert capsys.readouterr().out == "5\n"


def test_same_named_generics_in_linked_modules_do_not_collide(tmp_path, capsys):
    # Regression: instantiations are called by name through the merged
    # globals table, so two modules' private `describe[T]` must not both
    # lower to `<generic:describe:1>` (the second would silently shadow the
    # first and cross-dispatch arguments to the wrong instantiation).
    (tmp_path / "lib.ort").write_text(
        "#lang oort-core\n"
        'def describe[T](x: T) -> String { "lib" }\n'
        'def lib_run() -> String { describe("seed") }\n',
        encoding="utf-8",
    )
    main = tmp_path / "main.ort"
    main.write_text(
        "#lang oort-core\n"
        'from "./lib" import lib_run\n'
        'def describe[T](x: T) -> String { "main" }\n'
        "print(lib_run())\n"
        "print(describe(1))\n",
        encoding="utf-8",
    )
    compiler = get_compiler(["-t", "tvm", "NOT_EXIST", str(main)])
    compiler.run_file(main)
    assert capsys.readouterr().out == "lib\nmain\n"


def test_shared_instantiations_are_deduplicated():
    from oort_lang.ast import nodes as ast_nodes
    from oort_lang.hir.typed import is_generic_function_name, lower_typed_module
    from oort_lang.semantics.core.prelude import inject_core_prelude
    from oort_lang.source.input_info import StringInputInfo
    from tests.helpers import get_compiler

    # Parse, inject the prelude, then check — the CLI order (helpers.build_ast
    # checks without the prelude, so Option[Int] would not resolve).
    compiler = get_compiler("NOT_EXIST -t eval")
    info = StringInputInfo(GENERIC_FUNCTIONS)
    compiler.error_handler.register_input(info)
    dialect = compiler._resolve_dialect(info)
    parser, tokenized = compiler.prepare_parser(info)
    ast = compiler.build_ast(parser, info, dialect=dialect, tokenized=tokenized)
    assert isinstance(ast, ast_nodes.ModuleNode)
    inject_core_prelude(ast)
    analyzer = compiler.make_semantic_analyzer(info, dialect)
    ast = compiler.semantic_analyze(ast, analyzer)
    assert isinstance(ast, ast_nodes.ModuleNode)

    typed = lower_typed_module(ast)
    instantiations = {
        function.hir.name
        for function in typed.functions
        if is_generic_function_name(function.hir.name)
    }
    # id (Bool, Int via Some(id(9))), wrap/depth/count_all (Int, String) and
    # pair (Int+String, Bool+Float): 5 generics x 2 instantiations each.
    assert len(instantiations) == 10
    assert not any(function.hir.name == "id" for function in typed.functions), (
        "the generic declaration itself must not lower"
    )
