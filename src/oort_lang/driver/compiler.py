#! /usr/bin/env python

import argparse
import logging
import os
from pathlib import Path
from typing import Any

from antlr4 import CommonTokenStream

from ..ast import nodes
from ..ast.printer import ASTPrinter
from ..diagnostics import OortException, OortSyntaxError
from ..diagnostics.error_handler import CompilerErrorHandler
from ..diagnostics.error_listener import OortErrorListener
from ..parser.ast_builder import ASTBuilder, ASTNode
from ..parser.dialect import (
    DEFAULT_DIALECT,
    DialectConfig,
    LangDirective,
    known_dialect_names,
    lookup_dialect,
    parse_lang_directive,
)
from ..parser.grammar.OortLexer import OortLexer
from ..parser.grammar.OortParser import OortParser
from ..runtime.interpreter import ASTInterpreter
from ..runtime.modules import ModuleLoader
from ..semantics.pass1 import Pass1Analyzer
from ..source.input_info import FileInputInfo, InputInfo, StringInputInfo
from ..source.source_position import SourcePosition


class CompilerError(Exception):
    pass


class Compiler:
    """Top-level instance of Oort compiler frontend."""

    def __init__(self, args: argparse.Namespace):
        # Compiler options. TODO: Replace raw args with better option class.
        self.args = args

        self.error_handler = CompilerErrorHandler()
        self.module_paths = tuple(Path(path) for path in (getattr(args, "module_path", None) or []))

    def _run_input(self, input_info: InputInfo) -> Any:
        """Run a single input."""

        self.error_handler.register_input(input_info)
        dialect = self._resolve_dialect(input_info)
        assert dialect is not None

        parser = self._build_parser(input_info)
        ast = self.build_ast(parser, input_info, dialect=dialect)
        if not ast:
            raise CompilerError()

        # Print AST (no semantic analysis).
        if self.args.target == "ast":
            ast_printer = ASTPrinter(show_metadata=False)
            print(ast_printer.parse(ast))
            return None

        # Semantic analysis.
        pass1_analyzer: Pass1Analyzer = Pass1Analyzer(
            self.error_handler, input_info, dialect=dialect
        )
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
        loader = self.make_module_loader(interpreter, input_info.module_dir)
        interpreter.module_loader = loader
        assert isinstance(ast, nodes.ModuleNode)
        try:
            result = loader.execute_entry(ast, interpreter.entry_env, input_info.module_path)
        except OortException as e:
            matched = self.error_handler.input_info_for(e.position) or input_info
            self.error_handler.add(e, matched)
            self.error_handler.report(exit_on_error=False, clear=True)
            raise CompilerError() from None
        if self.error_handler.pending_count:
            self.error_handler.report(exit_on_error=False, clear=True)
        return result.py_value

    def compile_unit(self, input_info: InputInfo) -> nodes.ModuleNode | None:
        """Compile one module without printing or clearing diagnostics."""
        self.error_handler.register_input(input_info)
        start = self.error_handler.error_count

        dialect = self._resolve_dialect(input_info, exit_on_error=False)
        if dialect is None:
            return None

        parser = self._build_parser(input_info)
        ast = self.build_ast(
            parser,
            input_info,
            dialect=dialect,
            exit_on_error=False,
            summary=False,
            report_errors=False,
        )
        if ast is None or self.error_handler.error_count > start:
            return None

        pass1_analyzer: Pass1Analyzer = Pass1Analyzer(
            self.error_handler, input_info, dialect=dialect
        )
        ast = self.semantic_analyze(
            ast,
            pass1_analyzer,
            exit_on_error=False,
            summary=False,
            report_errors=False,
        )
        if ast is None or self.error_handler.error_count > start:
            return None
        assert isinstance(ast, nodes.ModuleNode)
        return ast

    def make_module_loader(self, interpreter: ASTInterpreter, entry_dir: Path) -> ModuleLoader:
        return ModuleLoader(
            compile_module=lambda path: self.compile_unit(FileInputInfo(path)),
            execute_module=interpreter.run_module,
            make_environment=interpreter.create_module_env,
            make_module=interpreter.new_module,
            entry_dir=entry_dir,
            search_paths=self.module_paths,
        )

    def run_file(self, input_file: os.PathLike) -> Any:
        return self._run_input(FileInputInfo(input_file))

    def run_string(self, input_string: str, name: str = "<string>") -> Any:
        return self._run_input(StringInputInfo(input_string, name=name))

    def _resolve_dialect(
        self, input_info: InputInfo, exit_on_error: bool = True
    ) -> DialectConfig | None:
        """Select the module dialect from its `#lang` directive."""
        directive = parse_lang_directive(input_info.get_source_text())

        if directive.error is not None:
            self._report_dialect_error(
                directive.error, directive, input_info, exit_on_error=exit_on_error
            )
            return None

        if directive.dialect_name is None:
            return DEFAULT_DIALECT

        config = lookup_dialect(directive.dialect_name)
        if config is None:
            known = ", ".join(known_dialect_names())
            self._report_dialect_error(
                f"Unknown dialect {directive.dialect_name!r}. Known dialects: {known}.",
                directive,
                input_info,
                exit_on_error=exit_on_error,
            )
            return None

        if not config.implemented:
            self._report_dialect_error(
                f"The {config.name!r} dialect is not implemented yet.",
                directive,
                input_info,
                exit_on_error=exit_on_error,
            )
            return None

        logging.debug("Using dialect %s", config.name)
        return config

    def _report_dialect_error(
        self,
        message: str,
        directive: LangDirective,
        input_info: InputInfo,
        exit_on_error: bool = True,
    ) -> None:
        position = SourcePosition.from_location(
            directive.line,
            directive.column,
            directive.text,
            filename=input_info.input_filename,
        )
        self.error_handler.add(OortSyntaxError(message, position), input_info)
        if exit_on_error:
            self.error_handler.report(exit_on_error=True, clear=False)

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
        dialect: DialectConfig = DEFAULT_DIALECT,
        exit_on_error: bool = True,
        summary: bool = True,
        report_errors: bool = True,
    ) -> ASTNode | None:
        start_errors = self.error_handler.error_count
        tree = parser.startRule()

        if report_errors:
            num_errors = self.error_handler.report(exit_on_error=exit_on_error, summary=summary)
        else:
            num_errors = self.error_handler.error_count - start_errors
        if num_errors > 0:
            return None

        # Build AST.
        builder = ASTBuilder(self.error_handler, input_info, dialect=dialect)
        ast = builder.parse(tree)
        logging.debug("AST built successfully")

        if report_errors:
            num_errors = self.error_handler.report(exit_on_error=exit_on_error, summary=summary)
        else:
            num_errors = self.error_handler.error_count - start_errors
        if num_errors > 0:
            return None

        return ast

    def semantic_analyze(
        self,
        ast: ASTNode,
        pass1_analyzer: Pass1Analyzer,
        exit_on_error: bool = True,
        summary: bool = True,
        report_errors: bool = True,
    ) -> ASTNode | None:
        if not ast:
            return None

        start_errors = self.error_handler.error_count
        pass1_analyzer.parse(ast)
        logging.debug("Semantic analyzation pass 1 done")

        if report_errors:
            num_errors = self.error_handler.report(exit_on_error=exit_on_error, summary=summary)
        else:
            num_errors = self.error_handler.error_count - start_errors
        if num_errors > 0:
            return None

        return ast
