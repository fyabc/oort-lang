#! /usr/bin/env python

"""Front-end tests for import statements."""

import pytest

from oort_lang.ast import nodes
from oort_lang.ast.printer import ASTPrinter
from tests.helpers import build_ast, get_compiler


def _import_nodes(ast: nodes.ModuleNode) -> list[nodes.ASTNode]:
    return [
        stmt
        for stmt in ast.body.statements
        if isinstance(stmt, (nodes.ImportStmt, nodes.ImportFromStmt))
    ]


def test_import_statements_pass_semantic_analysis():
    ast = build_ast('import "math"\nfrom "math" import sqrt, pow as power\n')
    assert isinstance(ast, nodes.ModuleNode)

    imports = _import_nodes(ast)
    assert len(imports) == 2
    assert isinstance(imports[0], nodes.ImportStmt)
    assert imports[0].module_path == "math"
    assert isinstance(imports[1], nodes.ImportFromStmt)
    assert imports[1].names == {"sqrt": None, "pow": "power"}


def test_import_ast_printer_shows_module_and_alias():
    ast = build_ast('import "math" as m\nfrom "math" import sqrt, pow as power\n')
    output = ASTPrinter().parse(ast)

    assert "ImportStmt(module_path='math', alias='m')" in output
    assert "ImportFromStmt(module_path='math', names=[sqrt, pow as power])" in output


def test_nested_import_is_rejected(caplog):
    compiler = get_compiler("NOT_EXIST -t eval")
    with pytest.raises(SystemExit):
        compiler.run_string('def load() { import "./lib" }\n')
    assert "Imports are only allowed at module top level." in caplog.text
