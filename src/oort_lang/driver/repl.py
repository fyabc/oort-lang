#! /usr/bin/env python

"""REPL session logic and console front-end.

`ReplSession` owns compilation state and knows nothing about terminals;
`ConsoleIO` handles prompts and output. The session reparses the whole pending
buffer on every submission, so it never mutates ANTLR lexer/parser internals.
"""

from __future__ import annotations

import dataclasses
from enum import Enum, auto
from pathlib import Path
from typing import TYPE_CHECKING

from rich.console import Console

from .. import __version__
from ..ast import nodes
from ..diagnostics import OortException
from ..runtime.interpreter import ASTInterpreter
from ..semantics.pass1 import Pass1Analyzer
from ..source.input_info import ReplInputInfo

if TYPE_CHECKING:
    from antlr4 import Parser

    from ..runtime.objects import OortObject
    from .compiler import Compiler


class ReplAction(Enum):
    EMPTY = auto()
    CONTINUE = auto()
    EVALUATED = auto()
    ERROR = auto()


@dataclasses.dataclass(frozen=True)
class ReplResult:
    action: ReplAction
    value: OortObject | None = None
    index: int = 0


class ReplSession:
    """Compile and evaluate one REPL statement at a time."""

    def __init__(self, compiler: Compiler, entry_dir: Path | None = None):
        self.compiler = compiler
        self.input_info = ReplInputInfo()
        compiler.error_handler.register_input(self.input_info)

        self.interpreter = ASTInterpreter(compiler.error_handler)
        self.module_loader = compiler.make_module_loader(
            self.interpreter, (entry_dir or Path.cwd()).resolve()
        )
        self.interpreter.module_loader = self.module_loader
        self.statement_count = 0
        self._pending: list[str] = []

    @property
    def is_continuing(self) -> bool:
        """True while the current submission has unclosed brackets."""
        return bool(self._pending)

    def cancel(self) -> None:
        """Discard the pending multi-line input (Ctrl-C semantics)."""
        self._reset_buffer()

    def flush(self) -> ReplResult | None:
        """Parse a still-incomplete buffer at EOF so diagnostics are not lost."""
        if not self._pending:
            return None
        parser, _ = self.compiler.prepare_parser(self.input_info)
        return self._submit(parser)

    def feed_line(self, line: str) -> ReplResult:
        if not self._pending and not line.strip():
            return ReplResult(ReplAction.EMPTY)

        normalized = line + "\n"
        self._pending.append(normalized)
        self.input_info.add_lines([normalized])

        parser, tokenized = self.compiler.prepare_parser(self.input_info)
        if tokenized.incomplete:
            return ReplResult(ReplAction.CONTINUE)
        return self._submit(parser)

    def _submit(self, parser: Parser) -> ReplResult:
        ast = self.compiler.build_ast(parser, self.input_info, exit_on_error=False, summary=False)
        if ast is not None:
            analyzer: Pass1Analyzer = Pass1Analyzer(self.compiler.error_handler, self.input_info)
            ast = self.compiler.semantic_analyze(ast, analyzer, exit_on_error=False, summary=False)
        if ast is None:
            return self._error()

        assert isinstance(ast, nodes.ModuleNode)
        try:
            result = self.module_loader.execute_entry(ast, self.interpreter.entry_env)
        except OortException as e:
            matched = self.compiler.error_handler.input_info_for(e.position) or self.input_info
            self.compiler.error_handler.add(e, matched)
            self.compiler.error_handler.report(exit_on_error=False, clear=True, summary=False)
            return self._error()

        if self.compiler.error_handler.pending_count:
            self.compiler.error_handler.report(exit_on_error=False, clear=True, summary=False)

        index = self.statement_count
        value = None if result is self.interpreter.runtime.null else result
        self._finish()
        return ReplResult(ReplAction.EVALUATED, value=value, index=index)

    def _error(self) -> ReplResult:
        index = self.statement_count
        self._finish()
        return ReplResult(ReplAction.ERROR, index=index)

    def _finish(self) -> None:
        self.statement_count += 1
        self._reset_buffer()

    def _reset_buffer(self) -> None:
        self._pending.clear()
        # Positions in the next submission start at line 1 again. Register a
        # fresh input so diagnostics never read a stale buffer.
        self.input_info = ReplInputInfo()
        self.compiler.error_handler.register_input(self.input_info)


class ConsoleIO:
    """Console prompts and output for the REPL."""

    def __init__(self, console: Console | None = None):
        self.console = console or Console()
        self.interactive = self.console.is_terminal

    def banner(self) -> None:
        self.console.rule("Welcome to Oort REPL!")
        self.console.print(
            f"[white]Oort {__version__}\n"
            "Type Ctrl-D to exit; Ctrl-C cancels the current input "
            "(or exits on an empty prompt).[/]"
        )

    def input(self, count: int, continuing: bool) -> str:
        return self.console.input(self._prompt(count, continuing))

    def _prompt(self, count: int, continuing: bool) -> str:
        if not self.interactive:
            return ""
        if continuing:
            return f"[green]{' ' * (len(str(count)) + 2)}...:[/] "
        return f"\n[green]In [{count}]:[/] "

    def result(self, index: int, text: str) -> None:
        self.console.print(f"[red]Out[{index}]:[/]", text)

    def cancelled(self) -> None:
        self.console.print("[yellow]Input cancelled.[/]")

    def goodbye(self) -> None:
        self.console.print("[yellow]Exit.[/]")


def run_repl(compiler: Compiler, console_io: ConsoleIO | None = None) -> int:
    """Run the interactive REPL until EOF or Ctrl-C on an empty prompt."""
    io = console_io or ConsoleIO()
    io.banner()
    session = ReplSession(compiler)

    while True:
        try:
            line = io.input(session.statement_count, session.is_continuing)
        except EOFError:
            session.flush()
            break
        except KeyboardInterrupt:
            if session.is_continuing:
                session.cancel()
                io.cancelled()
                continue
            break

        result = session.feed_line(line)
        if result.action is ReplAction.EVALUATED and result.value is not None:
            io.result(result.index, repr(result.value))

    io.goodbye()
    return 0
