#! /usr/bin/env python

import logging
import os
from pathlib import Path

from antlr4 import FileStream, InputStream


class InputInfo:
    """Base class of input information."""

    def get_input_stream(self) -> InputStream:
        raise NotImplementedError

    def get_source_text(self) -> str:
        """Whole source text, before lexing."""
        raise NotImplementedError

    def get_lines(self) -> list[str]:
        raise NotImplementedError

    @property
    def input_filename(self) -> str:
        raise NotImplementedError

    @property
    def module_name(self) -> str:
        raise NotImplementedError

    @property
    def module_path(self) -> Path | None:
        """Canonical path of this input's module, if it comes from a file."""
        return None

    @property
    def module_dir(self) -> Path:
        """Base directory used to resolve relative imports."""
        return Path.cwd()


class FileInputInfo(InputInfo):
    """File input information."""

    def __init__(self, input_file: os.PathLike, encoding: str = "utf-8-sig"):
        self._orig_input_file = Path(input_file)
        self.input_file = self._orig_input_file.absolute()
        self._resolved = self._orig_input_file.resolve()
        # `utf-8-sig` accepts both plain UTF-8 and files with a BOM; the BOM is
        # stripped so it cannot be mistaken for part of the first token.
        self.encoding = encoding

        self._lines: list[str] | None = None

    def get_input_stream(self):
        logging.debug(f"Loading input from {self.input_file} ...")
        return FileStream(str(self.input_file), encoding=self.encoding)

    def get_source_text(self) -> str:
        with open(self.input_file, encoding=self.encoding) as f:
            return f.read()

    def get_lines(self) -> list[str]:
        if self._lines is None:
            self._lines = self.get_source_text().splitlines(keepends=True)
            self._lines.append("")  # Add last EOF.
        return self._lines

    @property
    def input_filename(self) -> str:
        return str(self.input_file)

    @property
    def module_name(self) -> str:
        return self.input_file.stem

    @property
    def module_path(self) -> Path:
        return self._resolved

    @property
    def module_dir(self) -> Path:
        return self._resolved.parent


class StringInputInfo(InputInfo):
    """String input information."""

    def __init__(self, input_string: str, name: str = "<string>"):
        # Match `FileInputInfo` (utf-8-sig): strip a leading BOM if present.
        if input_string.startswith("﻿"):
            input_string = input_string[1:]
        self.input_string = input_string
        self.name = name
        self._lines: list[str] | None = None
        self._hash = None

    def get_input_stream(self) -> InputStream:
        stream = InputStream(self.input_string)
        stream.name = self.module_name
        return stream

    def get_source_text(self) -> str:
        return self.input_string

    def get_lines(self) -> list[str]:
        if self._lines is None:
            self._lines = self.input_string.splitlines(keepends=True)
            self._lines.append("")  # Add last EOF.
        return self._lines

    @property
    def input_filename(self) -> str:
        return self.module_name

    @property
    def module_name(self) -> str:
        return self.name


class ReplInputInfo(InputInfo):
    """Repl input information."""

    def __init__(self):
        self._lines: list[str] = []

    def get_input_stream(self) -> InputStream:
        raise RuntimeError("Not supported.")

    def get_source_text(self) -> str:
        return "".join(self._lines)

    def get_lines(self) -> list[str]:
        return self._lines

    @property
    def input_filename(self) -> str:
        return "<stdin>"

    @property
    def module_name(self) -> str:
        return "<stdin>"

    def add_lines(self, lines: list[str]):
        self._lines.extend(lines)
