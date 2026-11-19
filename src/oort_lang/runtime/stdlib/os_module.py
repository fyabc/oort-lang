#! /usr/bin/env python

"""Minimal process module: program arguments, script path and exit code."""

from ..functions import OortNativeFunction
from ..objects import OortList, OortModule, OortString


def _exit(code):
    if isinstance(code, bool) or not isinstance(code, int):
        raise TypeError("os.exit() expects an Int exit code")
    if not 0 <= code <= 255:
        raise ValueError("os.exit() expects a status between 0 and 255")
    raise SystemExit(code)


def build_os_module(interpreter) -> OortModule:
    with interpreter.runtime.activate():
        env = interpreter.create_module_env("os")
        env.define(
            "args",
            OortList([OortString(arg) for arg in interpreter.script_args]),
        )
        script = (
            interpreter.runtime.null
            if interpreter.script_path is None
            else OortString(interpreter.script_path)
        )
        env.define("script", script)
        env.define("exit", OortNativeFunction(_exit, name="exit"))
        return interpreter.new_module("os", env)
