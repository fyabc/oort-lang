#! /usr/bin/env python

"""Core collection surface: membership, writes, slices and Set algebra (OP 0031)."""

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

SURFACE = """#lang oort-core

def adjust() -> Int {
    var xs: List[Int] = [1, 2]
    var alias: List[Int] = xs
    xs[0] = 9
    alias[0]
}

def mapping() -> Int {
    var d: Dict[String, Int] = {: "a": 1 :}
    d["b"] = 2
    d["a"] + d["b"]
}

def snapshot() -> Int {
    var xs: List[Int] = [1, 2]
    var sum: Int = 0
    for x in xs { xs[0] = 99; sum = sum + x }
    sum
}

print(2 in [1, 2], 3 !in [1, 2], "bc" in "abcd", "a" in {: "a": 1 :})
print(2 in {. 1, 2 .}, 2 in (1, 2))
print(adjust(), mapping(), snapshot())
print([1, 2, 3, 4][1:3], [1, 2, 3, 4][-2:], [1, 2, 3, 4][:2], [1, 2, 3, 4][3:1])
print("abcd"[1:3], "abcd"[-2:])
print((1, "a", true)[1:])
print({. 1, 2 .} | {. 2, 3 .}, {. 1, 2 .} & {. 2, 3 .})
print({. 1, 2 .} - {. 2 .}, {. 1, 2 .} ^ {. 2, 3 .})
"""

SURFACE_OUTPUT = (
    "true true true true\n"
    "true true\n"
    "9 3 3\n"
    "[2, 3] [3, 4] [1, 2] []\n"
    "bc cd\n"
    "(a, true)\n"
    "{. 1, 2, 3 .} {. 2 .}\n"
    "{. 1 .} {. 1, 3 .}\n"
)


@pytest.mark.parametrize("target", ["eval", "vm", "tvm"])
def test_core_collection_surface_matches_across_targets(capsys, target):
    compiler = get_compiler(["NOT_EXIST", "-t", target])
    compiler.run_string(SURFACE)
    assert capsys.readouterr().out == SURFACE_OUTPUT


def test_collection_surface_uses_new_opcodes():
    program = compile_typed_module(lower_typed_module(build_ast(SURFACE)))
    ops = {TypedOp(word >> 24) for word in program.main.code}
    for proto in program.functions:
        ops |= {TypedOp(word >> 24) for word in proto.code}

    assert TypedOp.CONTAINS in ops
    assert TypedOp.SLICE in ops
    assert TypedOp.SET_UNION in ops
    assert TypedOp.SET_INTERSECT in ops
    assert TypedOp.SET_DIFFERENCE in ops
    assert TypedOp.SET_SYMMETRIC in ops
    assert TypedOp.SET_ITEM in ops


def test_collection_surface_serializes_and_runs(tmp_path, capsys):
    program = compile_typed_module(lower_typed_module(build_ast(SURFACE)))
    path = tmp_path / "surface.obc"
    write_typed_obc(program, path)

    loaded = read_typed_obc(path)
    TypedCodeVM(ASTInterpreter(CompilerErrorHandler())).run(loaded)
    assert capsys.readouterr().out == SURFACE_OUTPUT


@pytest.mark.parametrize(
    ("source", "message"),
    [
        ("print(1 in [1.0])", "Expected Float, got Int."),
        (
            "val t = (1, 2)\nt[0] = 3",
            "Only List and Dict elements can be assigned in oort-core, got Tuple[Int, Int].",
        ),
        ("print([1, 2][0:2:1])", "Slice steps are not supported in oort-core yet."),
        (
            'print({. 1 .} | {. "a" .})',
            "Operator '|' requires Sets with the same element type",
        ),
        (
            "print(1 in 2)",
            "Operator 'in' requires a List, Tuple, Set, Dict or String container",
        ),
    ],
)
def test_core_collection_type_errors(caplog, source, message):
    compiler = get_compiler("NOT_EXIST -t tvm")
    with pytest.raises(SystemExit):
        compiler.run_string("#lang oort-core\n" + source)
    assert message in caplog.text
