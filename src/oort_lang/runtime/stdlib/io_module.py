#! /usr/bin/env python

"""Minimal file I/O native module (UTF-8, whole-file)."""

from collections.abc import Callable
from pathlib import Path

from ..functions import OortNativeFunction
from ..objects import OortModule


def _path(value) -> str:
    if not isinstance(value, str):
        raise TypeError("io functions expect a String path")
    return value


def _read_file(path):
    return Path(_path(path)).read_text(encoding="utf-8")


def _write_file(path, text):
    if not isinstance(text, str):
        raise TypeError("io.write_file() expects a String text")
    Path(_path(path)).write_text(text, encoding="utf-8")


_FUNCTIONS: dict[str, Callable] = {
    "read_file": _read_file,
    "write_file": _write_file,
}


def build_io_module(interpreter) -> OortModule:
    with interpreter.runtime.activate():
        env = interpreter.create_module_env("io")
        for name, func in _FUNCTIONS.items():
            env.define(name, OortNativeFunction(func, name=name))
        return interpreter.new_module("io", env)
