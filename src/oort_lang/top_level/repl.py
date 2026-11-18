#! /usr/bin/env python

from antlr4 import CommonTokenStream, InputStream
from rich.console import Console

from .. import __version__
from ..ast_interpreter.ast_interpreter import ASTInterpreter
from ..exceptions import OortException
from ..frontend.error_listener import OortErrorListener
from ..frontend.pass1 import Pass1Analyzer
from ..grammar.OortLexer import OortLexer
from ..grammar.OortParser import OortParser
from ..support.input_info import ReplInputInfo
from .compiler import Compiler


def run_repl(compiler: Compiler):
    running = True

    console = Console()

    console.rule("""Welcome to Oort REPL!""")
    console.print(f"""[white]\
Oort {__version__}
Type 'ctrl + C' to exit.[/]""")

    # Setup lexer & parser.
    lexer = None
    token_stream = CommonTokenStream(None)
    parser = OortParser(None)
    input_info = ReplInputInfo()
    parser.removeErrorListeners()
    parser.addErrorListener(OortErrorListener(compiler.error_handler, input_info))

    pass1_analyzer: Pass1Analyzer = Pass1Analyzer(compiler.error_handler, input_info)
    ast_interpreter = ASTInterpreter(compiler.error_handler)

    stmt_count = 0
    continuation_mode = False
    continuation_lines = []

    while running:
        try:
            if continuation_mode:
                prompt = f"[green]{' ' * (len(str(stmt_count)) + 2)}...:[/] "
            else:
                prompt = f"\n[green]In [{stmt_count}]:[/] "

            line = console.input(prompt).strip()
            if not line:
                continue
            normalized_line = line + "\n"
            continuation_lines.append(normalized_line)
            line_stream = InputStream(normalized_line)

            # Update lexer.
            if lexer is None:
                lexer = OortLexer(line_stream)
                token_stream.setTokenSource(lexer)
                parser.setTokenStream(token_stream)
            else:
                lexer.inputStream = line_stream
            lexer.line = len(input_info.get_lines()) + len(continuation_lines)

            # Force lexer to scan the new line.
            token_stream.fill()

            # If inside any brackets or endswith backslash, run into continuation mode.
            if lexer.brackets or line[-1] == "\\":
                token_stream.tokens.pop()
                token_stream.fetchedEOF = False
                continuation_mode = True
                continue

            # Otherwise, all inputs are ready, run parser and reset states.
            input_info.add_lines(continuation_lines)
            continuation_lines.clear()
            continuation_mode = False
            lexer = None

            ast = compiler.build_ast(parser, input_info, exit_on_error=False, summary=False)
            if ast is not None:
                ast = compiler.semantic_analyze(
                    ast, pass1_analyzer, exit_on_error=False, summary=False
                )
            if ast:
                try:
                    result = ast_interpreter.run(ast)
                except OortException as e:
                    compiler.error_handler.add(e, input_info)

                    compiler.error_handler.report(exit_on_error=False, clear=True, summary=False)
                else:
                    # Skip null values.
                    if result is not ast_interpreter.runtime.null:
                        output = repr(result)
                        console.print(f"[red]Out[{stmt_count}]:[/]", output)

            # Successfully finished one statement.
            stmt_count += 1
        except KeyboardInterrupt:
            running = False

    console.print("[yellow]Exit.[/]")
    return 0
