#! /usr/bin/env python

"""Core List ordering: concatenation, lexicographic comparison and sorted (OP 0032)."""

import pytest

from oort_lang.bytecode import (
    TypedCodeVM,
    TypedOp,
    compile_typed_module,
    read_typed_obc,
    write_typed_obc,
)
from oort_lang.diagnostics.error_handler import CompilerErrorHandler
from oort_lang.hir import lower_typed_module
from oort_lang.runtime.interpreter import ASTInterpreter
from tests.helpers import build_ast, get_compiler

ORDERING = """#lang oort-core

def ordering() -> Unit {
    val a: List[Int] = [3, 1, 2]
    val b: List[Int] = [1, 2]
    val c: List[Int] = [1, 2, 3]
    val empty: List[Int] = []
    print(sorted(a), a)
    print(b + [3], b + empty)
    print(b < c, b <= b, b > [1], b > b)
    print(["b", "a"] < ["a"], empty < b, empty == empty)
    print([1.5, 0.5] < [0.5, 2.0])
    print(sorted(["b", "a", "c"]))
}

ordering()
"""

ORDERING_OUTPUT = (
    "[1, 2, 3] [3, 1, 2]\n"
    "[1, 2, 3] [1, 2]\n"
    "true true true false\n"
    "false true true\n"
    "false\n"
    "[a, b, c]\n"
)


@pytest.mark.parametrize("target", ["eval", "vm", "tvm"])
def test_ordering_matches_across_targets(capsys, target):
    compiler = get_compiler(["NOT_EXIST", "-t", target])
    compiler.run_string(ORDERING)
    assert capsys.readouterr().out == ORDERING_OUTPUT


def test_ordering_uses_new_opcodes():
    program = compile_typed_module(lower_typed_module(build_ast(ORDERING)))
    ops = {TypedOp(word >> 24) for word in program.main.code}
    for proto in program.functions:
        ops |= {TypedOp(word >> 24) for word in proto.code}

    assert TypedOp.CMP_LIST in ops
    assert TypedOp.LIST_CONCAT in ops


def test_ordering_serializes_and_runs(tmp_path, capsys):
    program = compile_typed_module(lower_typed_module(build_ast(ORDERING)))
    path = tmp_path / "ordering.obc"
    write_typed_obc(program, path)

    loaded = read_typed_obc(path)
    TypedCodeVM(ASTInterpreter(CompilerErrorHandler())).run(loaded)
    assert capsys.readouterr().out == ORDERING_OUTPUT


@pytest.mark.parametrize(
    ("source", "message"),
    [
        ("print(sorted([true]))", "requires a List of orderable elements"),
        ("print(sorted({. 1 .}))", "The built-in 'sorted' only accepts a List"),
        (
            "val xs: List[Int] = [1]\nprint(sorted(xs, true))",
            "The built-in 'sorted' expects 1 argument",
        ),
        ("print([true] < [false])", "List element type Bool is not orderable"),
        ("print([1] < [true])", "requires two Lists of the same orderable element type"),
        ('print([1] + ["a"])', "requires two Lists with the same element type"),
        ("print([1] + 2)", "requires two Lists with the same element type"),
        ("val f = sorted\nprint(1)", "can only be called directly"),
    ],
)
def test_ordering_type_errors(caplog, source, message):
    compiler = get_compiler("NOT_EXIST -t tvm")
    with pytest.raises(SystemExit):
        compiler.run_string("#lang oort-core\n" + source)
    assert message in caplog.text
