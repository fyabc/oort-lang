#! /usr/bin/env python

"""Helpers for benchmarks: run the real compiler pipeline once."""

from pathlib import Path

from oort_lang.ast.nodes import ASTNode
from oort_lang.driver.arguments import get_main_parser, parse_main_args
from oort_lang.driver.compiler import Compiler
from oort_lang.runtime.interpreter import ASTInterpreter
from oort_lang.semantics.pass1 import Pass1Analyzer
from oort_lang.source.input_info import StringInputInfo


def get_compiler(argv: str = "NOT_EXIST -t eval") -> Compiler:
    parser = get_main_parser()
    args = parse_main_args(parser, argv)
    return Compiler(args)


def analyzed_ast(source: str) -> ASTNode:
    """Parse and semantically analyze `source` (shared by both backends)."""
    compiler = get_compiler()
    input_info = StringInputInfo(source)
    parser = compiler._build_parser(input_info)
    ast = compiler.build_ast(parser, input_info)
    assert ast is not None
    ast = compiler.semantic_analyze(ast, Pass1Analyzer(compiler.error_handler, input_info))
    assert ast is not None
    return ast


def compile_program(source: str) -> tuple[ASTInterpreter, ASTNode]:
    """Parse, resolve and create an interpreter for `source`."""
    compiler = get_compiler()
    input_info = StringInputInfo(source)
    parser = compiler._build_parser(input_info)
    ast = compiler.build_ast(parser, input_info)
    assert ast is not None
    ast = compiler.semantic_analyze(ast, Pass1Analyzer(compiler.error_handler, input_info))
    assert ast is not None
    interpreter = ASTInterpreter(compiler.error_handler)
    interpreter.module_loader = compiler.make_module_loader(interpreter, Path.cwd())
    return interpreter, ast


def compile_and_run_vm(source: str) -> object:
    """Run `source` through the full `-t vm` pipeline (parse → bytecode → VM)."""
    compiler = get_compiler("NOT_EXIST -t vm")
    return compiler.run_string(source)


def run_compiled(interpreter: ASTInterpreter, ast: ASTNode) -> object:
    return interpreter.run(ast)


def compile_and_run(source: str) -> object:
    interpreter, ast = compile_program(source)
    return run_compiled(interpreter, ast)
