#! /usr/bin/env python

import sys

from .arguments import get_main_parser, parse_main_args
from .compiler import Compiler, CompilerError
from .logging_utils import setup_logging
from .repl import run_repl


def main():
    parser = get_main_parser()
    args = parse_main_args(parser)

    setup_logging(level=args.logging_level, rich_logging=not args.plain)

    compiler = Compiler(args)

    try:
        if args.input_file is not None:
            compiler.run_file(args.input_file)
        elif args.cmd is not None:
            compiler.run_string(args.cmd)
        else:
            run_repl(compiler)
    except CompilerError:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
