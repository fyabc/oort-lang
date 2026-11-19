#! /usr/bin/env python

"""The native `string` standard-library module."""

from collections.abc import Callable

from ..functions import OortNativeFunction
from ..objects import OortModule


def _text(value):
    if not isinstance(value, str):
        raise TypeError("string functions expect String values")
    return value


def _optional_text(value):
    return None if value is None else _text(value)


def _join(parts, sep=""):
    if not isinstance(parts, (list, tuple)):
        raise TypeError("string.join() expects a List or Tuple of strings")
    if any(not isinstance(part, str) for part in parts):
        raise TypeError("string.join() expects a List or Tuple of strings")
    return _text(sep).join(parts)


def _split(text, sep=None):
    return _text(text).split(_optional_text(sep))


def _upper(text):
    return _text(text).upper()


def _lower(text):
    return _text(text).lower()


def _strip(text, chars=None):
    return _text(text).strip(_optional_text(chars))


def _lstrip(text, chars=None):
    return _text(text).lstrip(_optional_text(chars))


def _rstrip(text, chars=None):
    return _text(text).rstrip(_optional_text(chars))


def _startswith(text, prefix):
    return _text(text).startswith(_text(prefix))


def _endswith(text, suffix):
    return _text(text).endswith(_text(suffix))


def _find(text, needle):
    return _text(text).find(_text(needle))


def _replace(text, old, new):
    return _text(text).replace(_text(old), _text(new))


def _ord(text):
    value = _text(text)
    if len(value) != 1:
        raise ValueError("string.ord() expects exactly one character")
    return ord(value)


def _chr(code):
    if isinstance(code, bool) or not isinstance(code, int):
        raise TypeError("string.chr() expects an Int code point")
    if not 0 <= code <= 0x10FFFF or 0xD800 <= code <= 0xDFFF:
        raise ValueError("string.chr() expects a Unicode scalar value")
    return chr(code)


_FUNCTIONS: dict[str, Callable] = {
    "split": _split,
    "join": _join,
    "upper": _upper,
    "lower": _lower,
    "strip": _strip,
    "lstrip": _lstrip,
    "rstrip": _rstrip,
    "startswith": _startswith,
    "endswith": _endswith,
    "find": _find,
    "replace": _replace,
    "ord": _ord,
    "chr": _chr,
}


def build_string_module(interpreter) -> OortModule:
    with interpreter.runtime.activate():
        env = interpreter.create_module_env("string")
        for name, func in _FUNCTIONS.items():
            env.define(name, OortNativeFunction(func, name=name))
        return interpreter.new_module("string", env)
