#! /usr/bin/env python

"""Typed top-level declarations: val/var bindings at module scope (B5)."""

import pytest

from oort_lang.driver.compiler import CompilerError
from tests.helpers import get_compiler

TOP_LEVEL = """#lang oort-core

def apply(f: (Int) -> Int, x: Int) -> Int { f(x) }

val name: String = "Oort"
val double: (Int) -> Int = do(x: Int) -> Int { x * 2 }
var count: Int = 0

def bump() -> Int {
    count = count + 1
    count
}

count = 10
val xs: List[Int] = [1, 2, 3]
xs[0] = 9

print(name, count)
print(apply(double, 3))
print(bump(), bump(), count)
print(xs, len(xs))
"""

TOP_LEVEL_OUTPUT = "Oort 10\n6\n11 12 12\n[9, 2, 3] 3\n"


@pytest.mark.parametrize("target", ["eval", "vm", "tvm"])
def test_top_level_declarations_match_across_targets(capsys, target):
    compiler = get_compiler(["-t", target, "NOT_EXIST"])
    compiler.run_string(TOP_LEVEL)
    assert capsys.readouterr().out == TOP_LEVEL_OUTPUT


CURRYING = """#lang oort-core

val add: Int -> Int -> Int = do(a: Int) -> Int -> Int {
    do(b: Int) -> Int { a + b }
}

print(add(2)(3))
"""

CURRYING_OUTPUT = "5\n"


@pytest.mark.parametrize("target", ["eval", "vm", "tvm"])
def test_chained_calls_on_top_level_function_values(capsys, target):
    # `add(2)(3)` calls the result of a call; top-level vals hold closures.
    compiler = get_compiler(["-t", target, "NOT_EXIST"])
    compiler.run_string(CURRYING)
    assert capsys.readouterr().out == CURRYING_OUTPUT


@pytest.mark.parametrize(
    ("source", "message"),
    [
        # Immutable globals are rejected by the checker, mirroring the dynamic path.
        (
            "val x: Int = 1\nx = 2\nprint(x)",
            "Cannot assign to immutable binding 'x'",
        ),
        # Unit has no runtime value; the checker keeps globals on the local rule.
        (
            "val u: Unit = print(1)",
            "Unit is only allowed as a function return type",
        ),
    ],
)
def test_top_level_errors(caplog, source, message):
    compiler = get_compiler("NOT_EXIST -t tvm")
    with pytest.raises((SystemExit, CompilerError)):
        compiler.run_string("#lang oort-core\n" + source)
    assert message in caplog.text


def test_dependency_modules_reject_top_level_declarations(tmp_path, caplog):
    # A linked program executes only the entry module's main, so top-level
    # bindings in a dependency would never initialize; they are rejected.
    (tmp_path / "lib.ort").write_text(
        "#lang oort-core\nval base: Int = 10\ndef add(a: Int, b: Int) -> Int { a + b }\n",
        encoding="utf-8",
    )
    main = tmp_path / "main.ort"
    main.write_text(
        '#lang oort-core\nfrom "./lib" import add\nprint(add(1, 2))\n',
        encoding="utf-8",
    )

    compiler = get_compiler(["-t", "tvm", "NOT_EXIST", str(main)])
    with pytest.raises((SystemExit, CompilerError)):
        compiler.run_file(main)
    assert "top-level declarations in dependency modules" in caplog.text


def test_top_level_block_expressions_run(capsys):
    compiler = get_compiler("NOT_EXIST -t tvm")
    compiler.run_string(
        "#lang oort-core\n"
        "{\n"
        "    var total: Int = 0\n"
        "    for i in [1, 2, 3] { total = total + i }\n"
        "    print(total)\n"
        "}\n"
    )
    assert capsys.readouterr().out == "6\n"
