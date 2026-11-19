#! /usr/bin/env python

"""The native `math` standard-library module."""

import math as _math
from collections.abc import Callable

from ..functions import OortNativeFunction
from ..objects import OortFloat, OortModule


def _number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError("math functions expect Int or Float values")
    return value


def _sqrt(x):
    return _math.sqrt(_number(x))


def _pow(x, y):
    return _math.pow(_number(x), _number(y))


def _fabs(x):
    return _math.fabs(_number(x))


def _floor(x):
    return _math.floor(_number(x))


def _ceil(x):
    return _math.ceil(_number(x))


def _trunc(x):
    return _math.trunc(_number(x))


def _exp(x):
    return _math.exp(_number(x))


def _log(x, base=None):
    x = _number(x)
    return _math.log(x) if base is None else _math.log(x, _number(base))


def _log10(x):
    return _math.log10(_number(x))


def _sin(x):
    return _math.sin(_number(x))


def _cos(x):
    return _math.cos(_number(x))


def _tan(x):
    return _math.tan(_number(x))


def _atan2(y, x):
    return _math.atan2(_number(y), _number(x))


_FUNCTIONS: dict[str, Callable] = {
    "sqrt": _sqrt,
    "pow": _pow,
    "fabs": _fabs,
    "floor": _floor,
    "ceil": _ceil,
    "trunc": _trunc,
    "exp": _exp,
    "log": _log,
    "log10": _log10,
    "sin": _sin,
    "cos": _cos,
    "tan": _tan,
    "atan2": _atan2,
}


def build_math_module(interpreter) -> OortModule:
    with interpreter.runtime.activate():
        env = interpreter.create_module_env("math")
        env.define("pi", OortFloat(_math.pi))
        env.define("e", OortFloat(_math.e))
        env.define("tau", OortFloat(_math.tau))
        for name, func in _FUNCTIONS.items():
            env.define(name, OortNativeFunction(func, name=name))
        return interpreter.new_module("math", env)
