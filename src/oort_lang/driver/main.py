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

    if args.cache_clean or args.cache_stats:
        if not args.cache_dir:
            parser.error("--cache-clean/--cache-stats require --cache-dir")
        from ..bytecode.typed_cache import TypedArtifactCache

        cache = TypedArtifactCache(args.cache_dir, max_size=args.cache_max_size)
        if args.cache_clean:
            removed = cache.clean()
            print(f"cache: removed {removed} file(s) from {cache.directory}", file=sys.stderr)
        if args.cache_stats:
            stats = cache.stats()
            print(
                f"cache: {stats.entries} entries, {stats.size_bytes} bytes in {stats.directory}",
                file=sys.stderr,
            )
        if args.input_file is None and args.cmd is None:
            sys.exit(0)

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
