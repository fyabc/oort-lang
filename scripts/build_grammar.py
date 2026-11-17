#! /usr/bin/env python
# -*- encoding: utf-8 -*-

"""Build lexer / parser / visitor files from grammar."""

import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).absolute().parent.parent
GRAMMAR_FILE_DIR = PROJECT_ROOT / "grammars"
GRAMMAR_FILENAME = GRAMMAR_FILE_DIR / "Oort.g4"
GENERATED_DIR = PROJECT_ROOT / "src" / "oort_lang" / "grammar"


def main():
    command = (
        f"antlr4 -encoding UTF-8 -visitor -no-listener -Dlanguage=Python3 "
        f"-o {GENERATED_DIR} "
        f"-lib {GRAMMAR_FILE_DIR} "
        f"{GRAMMAR_FILENAME}"
    )
    subprocess.run(
        command.split(),
    )


if __name__ == "__main__":
    main()
