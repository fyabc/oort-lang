#! /usr/bin/env python

"""Typed HIR model, subset lowering, validation and dump (design 15, M1)."""

import pytest

from oort_lang.bytecode import (
    TypedCodeVM,
    TypedOp,
    compile_module,
    compile_typed_module,
    read_typed_obc,
    write_typed_obc,
)
from oort_lang.bytecode.serialize import ObcError, read_obc, write_obc
from oort_lang.diagnostics.error_handler import CompilerErrorHandler
from oort_lang.diagnostics.syntax_errors import UnsupportedSyntax
from oort_lang.driver.compiler import CompilerError
from oort_lang.hir import IrType, lower_module, lower_typed_module
from oort_lang.hir.typed_exec import TypedInterpreter
from oort_lang.runtime.interpreter import ASTInterpreter
from tests.helpers import EXAMPLES_DIR, build_ast, get_compiler

FIB = """\
#lang oort-core

def fib(n: Int) -> Int {
    if n < 2 { n } else { fib(n - 1) + fib(n - 2) }
}

print(fib(10))
"""

EARLY_RETURN = """\
#lang oort-core

def clamp(x: Int) -> Int {
    if x < 0 { return 0 }
    return x
}

print(clamp(-1))
"""

LOOP = """\
#lang oort-core

def total(n: Int) -> Int {
    var sum: Int = 0
    var i: Int = 0
    while i < n {
        sum = sum + i
        i = i + 1
    }
    return sum
}

print(total(5))
"""


def test_typed_lowering_attaches_signatures_and_register_types():
    typed = lower_typed_module(build_ast(FIB))
    fib = next(function for function in typed.functions if function.hir.name == "fib")

    assert typed.main.param_types == ()
    assert typed.main.ret_type is IrType.UNIT
    assert fib.param_types == (IrType.INT,)
    assert fib.ret_type is IrType.INT
    assert len(fib.register_types) == fib.hir.local_count
    assert IrType.BOOL in fib.register_types
    assert IrType.FUNCTION in fib.register_types


@pytest.mark.parametrize("source", [FIB, EARLY_RETURN, LOOP])
def test_typed_lowering_accepts_scalar_subset(source: str):
    typed = lower_typed_module(build_ast(source))
    assert typed.main.ret_type is IrType.UNIT
    assert typed.functions


def test_thir_target_prints_types(capsys: pytest.CaptureFixture):
    compiler = get_compiler("NOT_EXIST -t thir")
    compiler.run_string(FIB)

    captured = capsys.readouterr()
    assert "<main>() -> Unit local_count=" in captured.out
    assert "fib(n: Int) -> Int local_count=" in captured.out
    assert "; R" in captured.out
    assert ":Bool" in captured.out
    assert ":Int" in captured.out


def test_typed_subset_example_is_accepted():
    source = (EXAMPLES_DIR / "08_core/08_15_typed_subset.ort").read_text(encoding="utf-8")
    typed = lower_typed_module(build_ast(source))

    names = {function.hir.name for function in typed.functions}
    assert {"fact", "fib", "clamp", "sum_to", "sign", "average", "mixed"} <= names


def test_tvm_matches_vm_on_example(run_file):
    typed = run_file(EXAMPLES_DIR / "08_core/08_15_typed_subset.ort", target="tvm")
    vm = run_file(EXAMPLES_DIR / "08_core/08_15_typed_subset.ort", target="vm")

    assert typed.stdout == vm.stdout
    assert typed.value == vm.value


@pytest.mark.parametrize("source", [FIB, EARLY_RETURN, LOOP])
def test_tvm_matches_vm_on_inline_programs(
    source: str,
    capsys: pytest.CaptureFixture,
):
    typed_compiler = get_compiler("NOT_EXIST -t tvm")
    typed_compiler.run_string(source)
    typed_out = capsys.readouterr().out

    vm_compiler = get_compiler("NOT_EXIST -t vm")
    vm_compiler.run_string(source)
    vm_out = capsys.readouterr().out

    assert typed_out == vm_out


def test_typed_main_value_uses_last_expression_type():
    source = """\
#lang oort-core
def add(a: Int, b: Int) -> Int { a + b }
add(2, 3)
"""
    typed = lower_typed_module(build_ast(source))
    assert typed.main.ret_type is IrType.INT

    compiler = get_compiler("NOT_EXIST -t tvm")
    assert compiler.run_string(source) == 5


def test_typed_bytecode_matches_typed_hir_interpreter(capsys: pytest.CaptureFixture):
    typed = lower_typed_module(build_ast(FIB))
    program = compile_typed_module(typed)

    hir_interpreter = ASTInterpreter(CompilerErrorHandler())
    hir_value = TypedInterpreter(hir_interpreter).run(typed)
    hir_out = capsys.readouterr().out

    code_interpreter = ASTInterpreter(CompilerErrorHandler())
    code_value = TypedCodeVM(code_interpreter).run(program)
    code_out = capsys.readouterr().out

    assert code_out == hir_out
    assert code_value.host_value == hir_value.host_value


def test_typed_bytecode_uses_typed_opcodes():
    typed = lower_typed_module(
        build_ast(
            """\
#lang oort-core
def mixed(a: Int, b: Float) -> Float { a + b }
def fib(n: Int) -> Int {
    if n < 2 { n } else { fib(n - 1) + fib(n - 2) }
}
print(mixed(1, 2.5))
"""
        )
    )
    program = compile_typed_module(typed)
    ops = {TypedOp(word >> 24) for word in program.main.code}
    for proto in program.functions:
        ops |= {TypedOp(word >> 24) for word in proto.code}

    assert TypedOp.ADD_I in ops
    assert TypedOp.ADD_F in ops
    assert TypedOp.TO_FLOAT in ops
    assert TypedOp.JMP_FALSE in ops
    assert TypedOp.CALL in ops


def test_tbc_target_prints_typed_disassembly(capsys: pytest.CaptureFixture):
    compiler = get_compiler("NOT_EXIST -t tbc")
    compiler.run_string(FIB)

    captured = capsys.readouterr()
    assert "CALL" in captured.out
    assert "JMP_FALSE" in captured.out
    assert "register types:" in captured.out


def test_typed_obc_round_trip(tmp_path):
    source = FIB.replace("print(fib(10))", "fib(10)")
    program = compile_typed_module(lower_typed_module(build_ast(source)))
    path = tmp_path / "typed.obc"
    write_typed_obc(program, path)

    loaded = read_typed_obc(path)

    assert loaded.main.code == program.main.code
    assert loaded.main.constants == program.main.constants
    assert loaded.main.register_types == program.main.register_types
    assert loaded.main.param_types == program.main.param_types
    assert loaded.main.ret_type == program.main.ret_type
    assert loaded.functions[0].code == program.functions[0].code

    result = TypedCodeVM(ASTInterpreter(CompilerErrorHandler())).run(loaded)
    assert result.host_value == 55


def test_typed_obc_rejects_dynamic_kind(tmp_path):
    erased = compile_module(lower_module(build_ast(FIB)))
    path = tmp_path / "dynamic.obc"
    write_obc(erased, path)

    with pytest.raises(ObcError, match="kind=1"):
        read_typed_obc(path)


def test_dynamic_obc_rejects_typed_kind(tmp_path):
    program = compile_typed_module(lower_typed_module(build_ast(FIB)))
    path = tmp_path / "typed.obc"
    write_typed_obc(program, path)

    with pytest.raises(ObcError):
        read_obc(path)


def test_tvm_rejects_out_of_subset():
    compiler = get_compiler("NOT_EXIST -t tvm")
    with pytest.raises(CompilerError):
        compiler.run_string('#lang oort-core\nprint("x")\n')


def test_typed_lowering_rejects_out_of_subset():
    ast = build_ast('#lang oort-core\nprint("x")\n')
    with pytest.raises(UnsupportedSyntax, match="StringConstant"):
        lower_typed_module(ast)


def test_typed_lowering_rejects_top_level_declarations():
    ast = build_ast("#lang oort-core\nval x: Int = 1\nprint(x)\n")
    with pytest.raises(UnsupportedSyntax, match="top-level declarations"):
        lower_typed_module(ast)


def test_typed_lowering_rejects_function_values():
    ast = build_ast(
        """\
#lang oort-core
def f(x: Int) -> Int { x }
val g: (Int) -> Int = f
print(g(1))
"""
    )
    with pytest.raises(UnsupportedSyntax):
        lower_typed_module(ast)
