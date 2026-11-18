#! /usr/bin/env python

"""Shared helpers for the test suite."""

from pathlib import Path

from oort_lang.ast.nodes import ASTNode
from oort_lang.driver.arguments import get_main_parser, parse_main_args
from oort_lang.driver.compiler import Compiler
from oort_lang.semantics.pass1 import Pass1Analyzer
from oort_lang.source.input_info import StringInputInfo

TEST_ASSETS_DIR = Path(__file__).parent / "assets"
REPO_ROOT = Path(__file__).parent.parent
EXAMPLES_DIR = REPO_ROOT / "examples"


def get_compiler(argv: str) -> Compiler:
    """Build a compiler from command-line style arguments."""
    parser = get_main_parser()
    args = parse_main_args(parser, argv)
    return Compiler(args)


def build_ast(source: str) -> ASTNode:
    """Parse and resolve a source string, returning the checked AST."""
    compiler = get_compiler("NOT_EXIST -t eval")
    input_info = StringInputInfo(source)
    parser = compiler._build_parser(input_info)
    ast = compiler.build_ast(parser, input_info)
    assert ast is not None
    ast = compiler.semantic_analyze(ast, Pass1Analyzer(compiler.error_handler, input_info))
    assert ast is not None
    return ast
