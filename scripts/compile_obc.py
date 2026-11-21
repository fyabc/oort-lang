#! /usr/bin/env python

"""Compile an Oort source file to a type-erased bytecode ``.obc`` file.

Usage:
    uv run --frozen python scripts/compile_obc.py input.ort [-o output.obc]

The frontend (parse / semantic analysis) and lowering are shared with the
Python VM; only the final bytecode is serialized (spec 13). The resulting
``.obc`` can be executed by the Rust VM spike or read back via
``oort_lang.bytecode.serialize.read_obc``.
"""

import argparse
import sys
from pathlib import Path

from oort_lang.bytecode import compile_module
from oort_lang.bytecode.serialize import write_obc
from oort_lang.driver.arguments import get_main_parser, parse_main_args
from oort_lang.driver.compiler import Compiler
from oort_lang.hir import lower_module
from oort_lang.source.input_info import FileInputInfo


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("input", help="Oort source file (.ort)")
    parser.add_argument("-o", "--output", help="output .obc path (default: input with .obc)")
    options = parser.parse_args()

    source_path = Path(options.input)
    output_path = Path(options.output) if options.output else source_path.with_suffix(".obc")

    compiler = Compiler(parse_main_args(get_main_parser(), ["NOT_EXIST", "-t", "vm"]))
    input_info = FileInputInfo(source_path)
    compiler.error_handler.register_input(input_info)
    dialect = compiler._resolve_dialect(input_info)
    assert dialect is not None
    ast_parser = compiler._build_parser(input_info)
    ast = compiler.build_ast(ast_parser, input_info, dialect=dialect)
    if ast is None:
        return 1
    analyzer = compiler.make_semantic_analyzer(input_info, dialect)
    ast = compiler.semantic_analyze(ast, analyzer)
    if ast is None:
        return 1

    program = compile_module(lower_module(ast))
    write_obc(program, output_path)
    print(f"wrote {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
