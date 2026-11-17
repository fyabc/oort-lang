#! /usr/bin/env python

import argparse
import logging
import os
from typing import Any

from antlr4 import CommonTokenStream

from ..ast_interpreter.ast_interpreter import ASTInterpreter
from ..exceptions import OortException
from ..frontend.ast_builder import ASTBuilder, ASTNode
from ..frontend.ast_printer import ASTPrinter
from ..frontend.error_handler import CompilerErrorHandler
from ..frontend.error_listener import OortErrorListener
from ..frontend.pass1 import Pass1Analyzer
from ..grammar.OortLexer import OortLexer
from ..grammar.OortParser import OortParser
from ..support.input_info import FileInputInfo, InputInfo, StringInputInfo


class CompilerError(Exception):
    pass


class Compiler:
    """Top-level instance of Oort compiler frontend."""

    def __init__(self, args: argparse.Namespace):
        # Compiler options. TODO: Replace raw args with better option class.
        self.args = args

        self.error_handler = CompilerErrorHandler()

    def _run_input(self, input_info: InputInfo) -> Any:
        """Run a single input."""

        parser = self._build_parser(input_info)
        ast = self.build_ast(parser, input_info)
        if not ast:
            raise CompilerError()

        # Print AST (no semantic analysis).
        if self.args.target == "ast":
            ast_printer = ASTPrinter(show_metadata=False)
            print(ast_printer.parse(ast))
            return None

        # Semantic analysis.
        pass1_analyzer = Pass1Analyzer(self.error_handler, input_info)
        ast = self.semantic_analyze(ast, pass1_analyzer)
        if not ast:
            raise CompilerError()

        # Print AST with metadata.
        if self.args.target == "astm":
            ast_printer = ASTPrinter(show_metadata=True)
            print(ast_printer.parse(ast))
            return None

        assert self.args.target == "eval", f"Invalid target {self.args.target}"

        interpreter = ASTInterpreter(self.error_handler)
        try:
            result = interpreter.run(ast)
        except OortException as e:
            self.error_handler.add(e, input_info)
            self.error_handler.report(exit_on_error=False, clear=True)
            raise CompilerError()
        return result.py_value

    def run_file(self, input_file: os.PathLike) -> Any:
        return self._run_input(FileInputInfo(input_file))

    def run_string(self, input_string: str, name: str = "<string>") -> Any:
        return self._run_input(StringInputInfo(input_string, name=name))

    def _build_parser(self, input_info: InputInfo) -> OortParser:
        """Build parser."""
        input_stream = input_info.get_input_stream()
        lexer = OortLexer(input_stream)

        token_stream = CommonTokenStream(lexer)
        parser = OortParser(token_stream)
        parser.removeErrorListeners()
        parser.addErrorListener(OortErrorListener(self.error_handler, input_info))
        return parser

    def build_ast(
        self,
        parser: OortParser,
        input_info: InputInfo,
        exit_on_error: bool = True,
        summary: bool = True,
    ) -> ASTNode | None:
        tree = parser.startRule()

        num_errors = self.error_handler.report(exit_on_error=exit_on_error, summary=summary)
        if num_errors > 0:
            return None

        # Build AST.
        builder = ASTBuilder(self.error_handler, input_info)
        ast = builder.parse(tree)
        logging.debug("AST built successfully")

        num_errors = self.error_handler.report(exit_on_error=exit_on_error, summary=summary)
        if num_errors > 0:
            return None

        return ast

    def semantic_analyze(
        self,
        ast: ASTNode,
        pass1_analyzer: Pass1Analyzer,
        exit_on_error: bool = True,
        summary: bool = True,
    ) -> ASTNode | None:
        if not ast:
            return None

        pass1_analyzer.parse(ast)
        logging.debug("Semantic analyzation pass 1 done")

        num_errors = self.error_handler.report(exit_on_error=exit_on_error, summary=summary)
        if num_errors > 0:
            return None

        return ast
