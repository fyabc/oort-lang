#! /usr/bin/env python

from __future__ import annotations

import dataclasses
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any

from antlr4 import CommonTokenStream, Token
from antlr4.ListTokenSource import ListTokenSource

from ..ast import nodes
from ..ast.printer import ASTPrinter
from ..diagnostics import OortException, OortSyntaxError, OortSyntaxWarning, TypeCheckError
from ..diagnostics.error_handler import CompilerErrorHandler
from ..diagnostics.error_listener import OortErrorListener
from ..diagnostics.runtime_errors import OortImportError
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
from ..parser.token_processor import _CLOSER_TEXT, _OPEN_TO_CLOSE, TokenizedInput, tokenize
from ..runtime.interpreter import ASTInterpreter
from ..runtime.modules import CompiledModule, ModuleLoader, resolve_module_path
from ..runtime.stdlib import NATIVE_MODULE_NAMES, native_module_factories
from ..semantics.analyzer import SemanticAnalyzer, create_semantic_analyzer
from ..semantics.core.prelude import inject_core_prelude
from ..semantics.core.types import AdtTemplate, CoreModuleInfo, Type
from ..source.input_info import FileInputInfo, InputInfo, StringInputInfo
from ..source.source_position import SourcePosition

if TYPE_CHECKING:
    import argparse
    import os

    from ..bytecode import TypedProgram
    from ..bytecode.typed_cache import TypedArtifactCache
    from ..hir.typed import TypedModule
    from ..runtime.bytecode_vm import BytecodeVM
    from ..runtime.environment import Environment
    from ..runtime.objects import OortObject


class CompilerError(Exception):
    pass


# Tokens that start statements inside a code block; a `{` followed by one of
# them is control flow, not a mistyped collection literal.
_STATEMENT_START_TOKENS = frozenset(
    token_type
    for name in (
        "VAR",
        "VAL",
        "DEF",
        "CLASS",
        "ENUM",
        "MATCH",
        "IF",
        "FOR",
        "WHILE",
        "RETURN",
        "BREAK",
        "CONTINUE",
        "IMPORT",
        "FROM",
    )
    if (token_type := getattr(OortLexer, name, None)) is not None
)


@dataclasses.dataclass(frozen=True)
class CompiledUnit:
    """A compiled module plus the static interface of an `oort-core` module."""

    ast: nodes.ModuleNode
    dialect: DialectConfig
    exports: tuple[tuple[str, Type], ...] = ()
    type_exports: tuple[tuple[str, Type | AdtTemplate], ...] = ()


class Compiler:
    """Top-level instance of Oort compiler frontend."""

    def __init__(self, args: argparse.Namespace):
        # Compiler options. TODO: Replace raw args with better option class.
        self.args = args

        self.error_handler = CompilerErrorHandler()
        self.module_paths = tuple(Path(path) for path in (getattr(args, "module_path", None) or []))
        self._entry_dir: Path | None = None
        self._entry_path: Path | None = None
        self._unit_cache: dict[Path, CompiledUnit] = {}
        self._core_compile_stack: list[Path] = []

    def _run_input(self, input_info: InputInfo) -> Any:
        """Run a single input."""

        self.error_handler.register_input(input_info)
        self._entry_dir = input_info.module_dir
        self._entry_path = input_info.module_path
        dialect = self._resolve_dialect(input_info)
        assert dialect is not None

        parser, tokenized = self.prepare_parser(input_info)
        ast = self.build_ast(parser, input_info, dialect=dialect, tokenized=tokenized)
        if not ast:
            raise CompilerError()

        # Print AST (no semantic analysis).
        if self.args.target == "ast":
            ast_printer = ASTPrinter(show_metadata=False)
            print(ast_printer.parse(ast))
            return None

        if dialect.features.type_checking:
            assert isinstance(ast, nodes.ModuleNode)
            inject_core_prelude(ast)

        # Semantic analysis.
        analyzer = self.make_semantic_analyzer(input_info, dialect)
        ast = self.semantic_analyze(ast, analyzer)
        if not ast:
            raise CompilerError()

        # Print AST with metadata.
        if self.args.target == "astm":
            ast_printer = ASTPrinter(show_metadata=True)
            print(ast_printer.parse(ast))
            return None

        if self.args.target == "hir":
            from ..hir import format_module, lower_module

            assert isinstance(ast, nodes.ModuleNode)
            try:
                hir_program = lower_module(ast)
            except OortException as e:
                matched = self.error_handler.input_info_for(e.position) or input_info
                self.error_handler.add(e, matched)
                self.error_handler.report(exit_on_error=False, clear=True)
                raise CompilerError() from None
            print(format_module(hir_program))
            return None

        if self.args.target == "thir":
            from ..hir import format_typed_module

            assert isinstance(ast, nodes.ModuleNode)
            try:
                typed_hir = self._link_typed_entry(ast, input_info)
            except OortException as e:
                matched = self.error_handler.input_info_for(e.position) or input_info
                self.error_handler.add(e, matched)
                self.error_handler.report(exit_on_error=False, clear=True)
                raise CompilerError() from None
            print(format_typed_module(typed_hir))
            return None

        if self.args.target == "bc":
            from ..bytecode import compile_module, disassemble_module
            from ..hir import lower_module

            assert isinstance(ast, nodes.ModuleNode)
            try:
                program = compile_module(lower_module(ast))
            except OortException as e:
                matched = self.error_handler.input_info_for(e.position) or input_info
                self.error_handler.add(e, matched)
                self.error_handler.report(exit_on_error=False, clear=True)
                raise CompilerError() from None
            print(disassemble_module(program))
            return None

        if self.args.target == "tbc":
            from ..bytecode import disassemble_typed_program

            assert isinstance(ast, nodes.ModuleNode)
            try:
                typed_bytecode = self._compile_typed_entry(ast, input_info)
            except OortException as e:
                matched = self.error_handler.input_info_for(e.position) or input_info
                self.error_handler.add(e, matched)
                self.error_handler.report(exit_on_error=False, clear=True)
                raise CompilerError() from None
            print(disassemble_typed_program(typed_bytecode))
            return None

        if self.args.target == "tvm":
            from ..bytecode import TypedCodeVM

            interpreter = ASTInterpreter(self.error_handler)
            interpreter.script_args = tuple(getattr(self.args, "script_args", ()) or ())
            interpreter.script_path = (
                str(input_info.module_path) if input_info.module_path is not None else None
            )
            assert isinstance(ast, nodes.ModuleNode)
            try:
                typed_bytecode = self._compile_typed_entry(ast, input_info)
                result = TypedCodeVM(interpreter).run(typed_bytecode)
            except OortException as e:
                matched = self.error_handler.input_info_for(e.position) or input_info
                self.error_handler.add(e, matched)
                self.error_handler.report(exit_on_error=False, clear=True)
                raise CompilerError() from None
            if self.error_handler.pending_count:
                self.error_handler.report(exit_on_error=False, clear=True)
            return result.host_value

        if self.args.target == "vm":
            from ..runtime.bytecode_vm import BytecodeVM

            interpreter = ASTInterpreter(self.error_handler)
            interpreter.script_args = tuple(getattr(self.args, "script_args", ()) or ())
            interpreter.script_path = (
                str(input_info.module_path) if input_info.module_path is not None else None
            )
            vm = BytecodeVM(interpreter)
            loader = self.make_vm_module_loader(interpreter, vm, input_info.module_dir)
            interpreter.module_loader = loader
            assert isinstance(ast, nodes.ModuleNode)
            try:
                with interpreter.runtime.activate():
                    result = loader.execute_entry(
                        ast,
                        vm.globals,
                        input_info.module_path,
                        dialect_name=dialect.name,
                    )
            except OortException as e:
                matched = self.error_handler.input_info_for(e.position) or input_info
                self.error_handler.add(e, matched)
                self.error_handler.report(exit_on_error=False, clear=True)
                raise CompilerError() from None
            if self.error_handler.pending_count:
                self.error_handler.report(exit_on_error=False, clear=True)
            return result.host_value

        assert self.args.target == "eval", f"Invalid target {self.args.target}"

        interpreter = ASTInterpreter(self.error_handler)
        interpreter.script_args = tuple(getattr(self.args, "script_args", ()) or ())
        interpreter.script_path = (
            str(input_info.module_path) if input_info.module_path is not None else None
        )
        loader = self.make_module_loader(interpreter, input_info.module_dir)
        interpreter.module_loader = loader
        assert isinstance(ast, nodes.ModuleNode)
        try:
            result = loader.execute_entry(
                ast,
                interpreter.entry_env,
                input_info.module_path,
                dialect_name=dialect.name,
            )
        except OortException as e:
            matched = self.error_handler.input_info_for(e.position) or input_info
            self.error_handler.add(e, matched)
            self.error_handler.report(exit_on_error=False, clear=True)
            raise CompilerError() from None
        if self.error_handler.pending_count:
            self.error_handler.report(exit_on_error=False, clear=True)
        return result.host_value

    def _link_typed_core(
        self,
        ast: nodes.ModuleNode,
        path: Path | None,
        entry_dir: Path,
    ) -> TypedModule:
        from ..hir.typed_link import link_typed_modules

        resolve = self._make_typed_resolver(entry_dir)
        return link_typed_modules(ast, path, resolve)

    def _make_typed_resolver(self, entry_dir: Path):
        def resolve(spec: str, importer_path: Path | None, position: SourcePosition):
            importer_dir = importer_path.parent if importer_path else entry_dir
            dep_path = resolve_module_path(
                spec,
                importer_dir=importer_dir,
                entry_dir=entry_dir,
                search_paths=self.module_paths,
                position=position,
            )
            unit = self.compile_unit_details(FileInputInfo(dep_path))
            if unit is None:
                return None
            if unit.dialect.name != "oort-core":
                raise OortImportError(
                    f"Cannot import a {unit.dialect.name!r} module from an "
                    f"'oort-core' module; cross-dialect imports require an "
                    f"explicit FFI boundary.",
                    position,
                )
            return dep_path, unit.ast

        return resolve

    def _compile_typed_entry(
        self,
        ast: nodes.ModuleNode,
        input_info: InputInfo,
    ) -> TypedProgram:
        """Lower, compile and link typed modules through v7 artifacts."""

        from ..bytecode import build_typed_program
        from ..hir.typed_link import load_typed_units

        entry_dir = self._entry_dir or input_info.module_dir
        resolve = self._make_typed_resolver(entry_dir)
        units = load_typed_units(ast, input_info.module_path, resolve)
        return build_typed_program(units, self._typed_cache())

    def _typed_cache(self) -> TypedArtifactCache | None:
        directory = getattr(self.args, "cache_dir", None)
        if not directory:
            return None
        from ..bytecode.typed_cache import TypedArtifactCache

        return TypedArtifactCache(directory, max_size=getattr(self.args, "cache_max_size", None))

    def _link_typed_entry(
        self,
        ast: nodes.ModuleNode,
        input_info: InputInfo,
    ) -> TypedModule:
        return self._link_typed_core(
            ast,
            input_info.module_path,
            self._entry_dir or input_info.module_dir,
        )

    def compile_unit_details(self, input_info: InputInfo) -> CompiledUnit | None:
        """Compile one module and return its AST, dialect and static exports."""
        self.error_handler.register_input(input_info)
        if self._entry_dir is None:
            self._entry_dir = input_info.module_dir
        if self._entry_path is None:
            self._entry_path = input_info.module_path
        path = input_info.module_path
        if path is not None:
            cached = self._unit_cache.get(path)
            if cached is not None:
                return cached

        start = self.error_handler.error_count

        dialect = self._resolve_dialect(input_info, exit_on_error=False)
        if dialect is None:
            return None

        parser, tokenized = self.prepare_parser(input_info)
        ast = self.build_ast(
            parser,
            input_info,
            dialect=dialect,
            exit_on_error=False,
            summary=False,
            report_errors=False,
            tokenized=tokenized,
        )
        if ast is None or self.error_handler.error_count > start:
            return None

        if dialect.features.type_checking:
            assert isinstance(ast, nodes.ModuleNode)
            inject_core_prelude(ast)

        analyzer = self.make_semantic_analyzer(input_info, dialect)
        ast = self.semantic_analyze(
            ast,
            analyzer,
            exit_on_error=False,
            summary=False,
            report_errors=False,
        )
        if ast is None or self.error_handler.error_count > start:
            return None
        assert isinstance(ast, nodes.ModuleNode)

        exports: tuple[tuple[str, Type], ...] = tuple(getattr(analyzer, "exports", ()))
        type_exports: tuple[tuple[str, Type | AdtTemplate], ...] = tuple(
            getattr(analyzer, "type_exports", ())
        )
        unit = CompiledUnit(ast, dialect, exports, type_exports)
        if path is not None:
            self._unit_cache[path] = unit
        return unit

    def compile_unit(self, input_info: InputInfo) -> nodes.ModuleNode | None:
        """Compile one module without printing or clearing diagnostics."""
        result = self.compile_unit_details(input_info)
        return None if result is None else result.ast

    def make_vm_module_loader(
        self,
        interpreter: ASTInterpreter,
        vm: BytecodeVM,
        entry_dir: Path,
    ) -> ModuleLoader:
        """Build a module loader whose modules execute on the bytecode VM."""
        from ..bytecode import compile_module as compile_bytecode
        from ..hir import lower_module

        self._entry_dir = entry_dir.resolve()

        def compile_module(path: Path) -> CompiledModule | None:
            result = self.compile_unit_details(FileInputInfo(path))
            if result is None:
                return None
            return CompiledModule(result.ast, result.dialect.name)

        def execute_module(ast: nodes.ModuleNode, env: Environment) -> OortObject:
            with interpreter.runtime.activate():
                return vm.run_module(compile_bytecode(lower_module(ast)), env)

        def execute_core_module(ast: nodes.ModuleNode, env: Environment, path: Path) -> None:
            from ..bytecode import build_typed_program_exports
            from ..bytecode.typed_boundary import execute_core_module as run_core
            from ..hir.typed_link import load_typed_units

            resolve = self._make_typed_resolver(path.parent if path else entry_dir)
            units = load_typed_units(ast, path, resolve)
            program, exports = build_typed_program_exports(units, self._typed_cache())
            run_core(env, interpreter, program, exports)

        return ModuleLoader(
            compile_module=compile_module,
            execute_module=execute_module,
            execute_core_module=execute_core_module,
            make_environment=interpreter.create_module_env,
            make_module=interpreter.new_module,
            entry_dir=entry_dir,
            search_paths=self.module_paths,
            native_modules=native_module_factories(interpreter),
        )

    def make_module_loader(self, interpreter: ASTInterpreter, entry_dir: Path) -> ModuleLoader:
        self._entry_dir = entry_dir.resolve()

        def compile_module(path: Path) -> CompiledModule | None:
            result = self.compile_unit_details(FileInputInfo(path))
            if result is None:
                return None
            return CompiledModule(result.ast, result.dialect.name)

        def execute_core_module(ast: nodes.ModuleNode, env: Environment, path: Path) -> None:
            from ..bytecode import build_typed_program_exports
            from ..bytecode.typed_boundary import execute_core_module as run_core
            from ..hir.typed_link import load_typed_units

            resolve = self._make_typed_resolver(path.parent if path else entry_dir)
            units = load_typed_units(ast, path, resolve)
            program, exports = build_typed_program_exports(units, self._typed_cache())
            run_core(env, interpreter, program, exports)

        return ModuleLoader(
            compile_module=compile_module,
            execute_module=interpreter.run_module,
            execute_core_module=execute_core_module,
            make_environment=interpreter.create_module_env,
            make_module=interpreter.new_module,
            entry_dir=entry_dir,
            search_paths=self.module_paths,
            native_modules=native_module_factories(interpreter),
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

    def prepare_parser(self, input_info: InputInfo) -> tuple[OortParser, TokenizedInput]:
        """Lex and post-process one input, then build its parser.

        The tokenized result carries bracket depth and completeness, which the
        REPL uses to decide whether to keep reading.
        """
        lexer = OortLexer(input_info.get_input_stream())
        lexer.removeErrorListeners()
        lexer.addErrorListener(OortErrorListener(self.error_handler, input_info))
        tokenized = tokenize(lexer)
        token_stream = CommonTokenStream(ListTokenSource(tokenized.tokens))

        parser = OortParser(token_stream)
        parser.removeErrorListeners()
        parser.addErrorListener(OortErrorListener(self.error_handler, input_info))
        return parser, tokenized

    def _build_parser(self, input_info: InputInfo) -> OortParser:
        """Build parser."""
        return self.prepare_parser(input_info)[0]

    def build_ast(
        self,
        parser: OortParser,
        input_info: InputInfo,
        dialect: DialectConfig = DEFAULT_DIALECT,
        exit_on_error: bool = True,
        summary: bool = True,
        report_errors: bool = True,
        tokenized: TokenizedInput | None = None,
    ) -> ASTNode | None:
        start_errors = self.error_handler.error_count
        start_entries = self.error_handler.pending_count
        tree = parser.startRule()
        self._report_delimiter_diagnostic(tokenized, input_info, start_entries)
        self._report_brace_literal_hint(tokenized, input_info, start_entries)
        hinted = self._report_habit_hints(tokenized, input_info, start_entries)

        if report_errors:
            num_errors = self.error_handler.report(exit_on_error=exit_on_error, summary=summary)
        else:
            num_errors = self.error_handler.error_count - start_errors
        if num_errors > 0:
            return None

        # Build AST.
        builder = ASTBuilder(self.error_handler, input_info, dialect=dialect)
        ast = builder.parse(tree)
        # Pratt-stage errors (e.g. a missing operand) only surface now, so
        # failure-gated habit hints get a second chance.
        if not hinted:
            self._report_habit_hints(tokenized, input_info, start_entries)
        logging.debug("AST built successfully")

        if report_errors:
            num_errors = self.error_handler.report(exit_on_error=exit_on_error, summary=summary)
        else:
            num_errors = self.error_handler.error_count - start_errors
        if num_errors > 0:
            return None

        return ast

    def _report_delimiter_diagnostic(
        self,
        tokenized: TokenizedInput | None,
        input_info: InputInfo,
        start_entries: int,
    ) -> None:
        """Replace cascading parse errors for broken bracket pairs.

        When a bracket is unclosed or unmatched, ANTLR fails wherever it runs
        out of input, far from the real mistake. Python-style messages point
        at the bracket instead: ``'(' was never closed`` / ``Unmatched ']'``.
        """
        if tokenized is None:
            return
        error: OortSyntaxError | None = None
        if tokenized.unmatched_closers:
            token = tokenized.unmatched_closers[0]
            message = f"Unmatched '{token.text}'"
            if tokenized.unclosed_openers:
                # A mismatched pair: name the closer the opener expects
                # (Python 3.12 pairs closing/opening objects the same way).
                opener = tokenized.unclosed_openers[0]
                expected = _CLOSER_TEXT[_OPEN_TO_CLOSE[opener.type]]
                if expected is not None:
                    message += f": expected {expected!r} to close '{opener.text}'"
            error = OortSyntaxError(message, SourcePosition.from_token(token))
        elif tokenized.unclosed_openers:
            token = tokenized.unclosed_openers[0]
            error = OortSyntaxError(
                f"'{token.text}' was never closed", SourcePosition.from_token(token)
            )
        if error is None:
            return
        if self.error_handler.pending_count <= start_entries:
            # The parse survived the delimiters; keep its own diagnostics.
            return
        self.error_handler.retract_since(start_entries)
        self.error_handler.add(error, input_info)

    def _report_brace_literal_hint(
        self,
        tokenized: TokenizedInput | None,
        input_info: InputInfo,
        start_entries: int,
    ) -> None:
        """Suggest collection delimiters when a one-line block looks like one.

        Python habits (`{1, 2}` / `{1: 2}`) parse as code blocks and fail with
        confusing parser messages. A Python-style "did you mean" warning
        points at Oort's `{. ... .}` / `{: ... :}` literals instead.
        """
        if tokenized is None or self.error_handler.pending_count <= start_entries:
            return
        tokens = tokenized.tokens
        for index, token in enumerate(tokens):
            if token.type != OortLexer.LBC:
                continue
            hint = self._brace_literal_hint(tokens[index + 1 :], token)
            if hint is not None:
                self.error_handler.add(
                    OortSyntaxWarning(hint, SourcePosition.from_token(token)),
                    input_info,
                )
                return  # one hint per input is enough

    @staticmethod
    def _brace_literal_hint(tokens: list[Token], opener: Token) -> str | None:
        """Classify a same-line block body by its first top-level separator."""
        first = tokens[0] if tokens else None
        if first is None or first.type in _STATEMENT_START_TOKENS:
            return None
        depth = 0
        for token in tokens:
            if token.type == Token.EOF or token.line != opener.line:
                return None
            token_type = token.type
            if token_type in (OortLexer.LPA, OortLexer.LBK, OortLexer.LBC):
                depth += 1
            elif token_type in (OortLexer.RPA, OortLexer.RBK):
                depth -= 1
            elif token_type == OortLexer.RBC:
                if depth == 0:
                    return None  # the block closed without a separator
                depth -= 1
            elif depth == 0 and token_type == OortLexer.COLON:
                return "Did you mean a Dict literal '{: key: value :}'? '{' opens a code block."
            elif depth == 0 and token_type == OortLexer.COMMA:
                return "Did you mean a Set literal '{. item, ... .}'? '{' opens a code block."
        return None

    def _report_habit_hints(
        self,
        tokenized: TokenizedInput | None,
        input_info: InputInfo,
        start_entries: int,
    ) -> bool:
        """Warn about common Python habits that mean something else in Oort.

        Empty braces and a line-leading `//` are legal but almost certainly
        not what a Python user meant, so they warn even without a parse
        error; the remaining hints only accompany parse failures. Returns
        whether a hint was emitted.
        """
        if tokenized is None:
            return False
        failed = self.error_handler.pending_count > start_entries
        tokens = tokenized.tokens
        prev_line = 0
        for index, token in enumerate(tokens):
            token_type = token.type
            text = token.text or ""
            if token_type == OortLexer.LBC and index + 1 < len(tokens):
                if (
                    tokens[index + 1].type == OortLexer.RBC
                    # Only expression positions are suspicious: `val d = {}`,
                    # `f({})`, `return {}`. Empty class/function/if bodies
                    # are ordinary code and stay silent.
                    and index > 0
                    and tokens[index - 1].type
                    in (OortLexer.ASSIGN, OortLexer.LPA, OortLexer.COMMA, OortLexer.RETURN)
                ):
                    self._add_habit_hint(
                        "Did you mean an empty Dict '{:}' or Set '{.}'? "
                        "'{}' is an empty code block.",
                        token,
                        input_info,
                    )
                    return True
            elif token_type == OortLexer.FLOOR_DIV and token.line != prev_line:
                self._add_habit_hint(
                    "Did you mean a comment? Comments start with '#'; '//' is integer division.",
                    token,
                    input_info,
                )
                return True
            elif failed and token_type == OortLexer.USER_OP and text in ("++", "--"):
                # Postfix framing: a binary `operator "++"` may be user
                # defined, but Oort has no postfix operators at all.
                self._add_habit_hint(
                    f"Oort has no postfix {text!r}; use {'+=' if text == '++' else '-='} 1.",
                    token,
                    input_info,
                )
                return True
            elif failed and token_type == OortLexer.IDENTIFIER and text == "lambda":
                self._add_habit_hint(
                    "'lambda' is not a keyword; Oort lambdas use 'do', e.g. do(x): x.",
                    token,
                    input_info,
                )
                return True
            elif (
                failed
                and token_type == OortLexer.DOT
                and index + 1 < len(tokens)
                and tokens[index + 1].type == OortLexer.DEC_INT
                # Adjacent (no space) rules out member-access typos like `a . 5`.
                and tokens[index + 1].column == token.column + 1
            ):
                self._add_habit_hint(
                    f"Leading-dot floats are not supported; "
                    f"did you mean '0.{tokens[index + 1].text}'?",
                    token,
                    input_info,
                )
                return True
            elif failed and token_type in (OortLexer.IF, OortLexer.WHILE):
                hint = self._condition_assignment_hint(tokens[index + 1 :], token)
                if hint is not None:
                    self._add_habit_hint(hint, token, input_info)
                    return True
            if token_type != Token.EOF:
                prev_line = token.line
        return False

    def _condition_assignment_hint(self, tokens: list[Token], opener: Token) -> str | None:
        """Detect `if x = 1` — assignment inside a condition (meant '==')."""
        depth = 0
        for token in tokens:
            token_type = token.type
            if token_type == Token.EOF or (
                depth == 0 and token_type in (OortLexer.LBC, OortLexer.COLON)
            ):
                return None  # condition ended without an assignment
            if token_type in (OortLexer.LPA, OortLexer.LBK):
                depth += 1
            elif token_type in (OortLexer.RPA, OortLexer.RBK):
                depth -= 1
            elif depth == 0 and token_type == OortLexer.ASSIGN:
                return "Assignment is a statement; did you mean '==' in the condition?"
        return None

    def _add_habit_hint(self, message: str, token: Token, input_info: InputInfo) -> None:
        self.error_handler.add(
            OortSyntaxWarning(message, SourcePosition.from_token(token)),
            input_info,
        )

    def make_semantic_analyzer(
        self,
        input_info: InputInfo,
        dialect: DialectConfig = DEFAULT_DIALECT,
    ) -> SemanticAnalyzer:
        resolver = self._resolve_core_module if dialect.features.type_checking else None
        return create_semantic_analyzer(
            self.error_handler,
            input_info,
            dialect,
            module_resolver=resolver,
        )

    def _resolve_core_module(
        self,
        spec: str,
        importer_dir: Path,
        position: SourcePosition,
    ) -> CoreModuleInfo | None:
        """Resolve and compile one `oort-core` import for static checking."""
        if spec in NATIVE_MODULE_NAMES:
            return CoreModuleInfo(name=spec, dialect_name="native", exports=())

        entry_dir = self._entry_dir or importer_dir
        try:
            path = resolve_module_path(
                spec,
                importer_dir=importer_dir,
                entry_dir=entry_dir,
                search_paths=self.module_paths,
                position=position,
            )
        except OortImportError as error:
            self._add_import_diagnostic(error.msg, position)
            return None

        if path in self._core_compile_stack:
            chain_paths = [
                item
                for item in [self._entry_path, *self._core_compile_stack, path]
                if item is not None
            ]
            chain = " -> ".join(item.name for item in chain_paths)
            self._add_import_diagnostic(f"Circular import detected: {chain}.", position)
            return None

        self._core_compile_stack.append(path)
        try:
            unit = self.compile_unit_details(FileInputInfo(path))
        finally:
            self._core_compile_stack.pop()
        if unit is None:
            return None
        return CoreModuleInfo(
            name=spec,
            dialect_name=unit.dialect.name,
            exports=unit.exports,
            type_exports=unit.type_exports,
        )

    def _add_import_diagnostic(self, message: str, position: SourcePosition) -> None:
        input_info = self.error_handler.input_info_for(position)
        if input_info is not None:
            self.error_handler.add(
                TypeCheckError(message, position),
                input_info,
            )

    def semantic_analyze(
        self,
        ast: ASTNode,
        analyzer: SemanticAnalyzer,
        exit_on_error: bool = True,
        summary: bool = True,
        report_errors: bool = True,
    ) -> ASTNode | None:
        if not ast:
            return None

        start_errors = self.error_handler.error_count
        analyzer.parse(ast)
        logging.debug("Semantic analysis done")

        if report_errors:
            num_errors = self.error_handler.report(exit_on_error=exit_on_error, summary=summary)
        else:
            num_errors = self.error_handler.error_count - start_errors
        if num_errors > 0:
            return None

        return ast
