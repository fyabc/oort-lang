#! /usr/bin/env python

import sys

from oort_lang.support.arguments import get_main_parser, parse_main_args
from oort_lang.support.logging_utils import setup_logging
from oort_lang.top_level.compiler import Compiler, CompilerError
from oort_lang.top_level.repl import run_repl


def main():
    parser = get_main_parser()
    args = parse_main_args(parser)

    setup_logging(level=args.logging_level)

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
