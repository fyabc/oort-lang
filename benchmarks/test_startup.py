#! /usr/bin/env python

"""Startup benchmarks: compiler construction, empty programs and the
per-module HIR/bytecode compilation cost of the VM pipeline."""

from benchmarks.bench_utils import analyzed_ast, compile_and_run, compile_and_run_vm, get_compiler
from oort_lang.bytecode import compile_module
from oort_lang.hir import lower_module
from oort_lang.runtime import Runtime

FIB_SOURCE = """\
def fib(n) {
    if n <= 1 { return n }
    fib(n - 1) + fib(n - 2)
}
fib(18)
"""


def test_compiler_construction(benchmark):
    benchmark(get_compiler)


def test_empty_program(benchmark):
    benchmark(compile_and_run, "")


def test_empty_program_vm(benchmark):
    benchmark(compile_and_run_vm, "")


def test_runtime_construction(benchmark):
    benchmark(Runtime)


def test_hir_lowering_empty(benchmark):
    ast = analyzed_ast("")
    benchmark(lower_module, ast)


def test_hir_lowering_fib(benchmark):
    ast = analyzed_ast(FIB_SOURCE)
    benchmark(lower_module, ast)


def test_bytecode_compile_empty(benchmark):
    hir = lower_module(analyzed_ast(""))
    benchmark(compile_module, hir)


def test_bytecode_compile_fib(benchmark):
    hir = lower_module(analyzed_ast(FIB_SOURCE))
    benchmark(compile_module, hir)
