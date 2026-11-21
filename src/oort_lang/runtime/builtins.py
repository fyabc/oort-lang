#! /usr/bin/env python

"""Builtin Oort types and values in AST-interpreter."""

import time
from collections.abc import Callable

from .environment import Environment
from .functions import OortIterator, OortNativeFunction
from .native import NativeMode
from .objects import (
    OortDict,
    OortList,
    OortSet,
    OortString,
    OortTuple,
)
from .stdlib.collections import define_collection_builtins
from .type_system import OortType, Runtime


def _define_native_function(
    env: Environment,
    name: str,
    func: Callable,
    *,
    mode: NativeMode = NativeMode.HOST,
):
    """Define a builtin function."""
    env.define(name, OortNativeFunction(func, name=name, mode=mode))


def _len(value):
    """Length without projecting the whole container to the host."""
    if isinstance(value, (OortList, OortTuple, OortDict, OortSet, OortString)):
        return len(value)
    raise TypeError(f"Type {value.type.name!r} has no len()")


def _iter(value):
    """Create a fresh snapshot iterator for a built-in container."""
    return OortIterator(list(value))


def setup_builtins(runtime: Runtime, env: Environment):
    """Setup all builtin names for one runtime."""

    # === Builtin types
    # Type
    t_type = runtime.types.type_type
    t_type.fields = {
        "mro": OortNativeFunction(OortType.mro, name="mro"),
    }
    env.define(t_type.name, t_type)

    # Object
    t_object = runtime.types.object_type
    t_object.fields = {}
    env.define(t_object.name, t_object)

    # Function
    t_function = runtime.types.function_type
    t_function.bases = []
    t_function.fields = {}
    env.define(t_function.name, t_function)

    # Method
    t_method = runtime.types.method_type
    t_method.bases = []
    t_method.fields = {}
    env.define(t_method.name, t_method)

    # Null
    t_null = runtime.types.null_type
    t_null.bases = []
    t_null.fields = {}
    env.define(t_null.name, t_null)
    env.define("null", runtime.null)

    # Int
    t_int = runtime.types.int_type
    t_int.bases = []
    t_int.fields = {}
    env.define(t_int.name, t_int)

    # Float
    t_float = runtime.types.float_type
    t_float.bases = []
    t_float.fields = {}
    env.define(t_float.name, t_float)

    # Bool
    t_bool = runtime.types.bool_type
    t_bool.fields = {}
    env.define(t_bool.name, t_bool)
    env.define("true", runtime.true)
    env.define("false", runtime.false)

    # String
    t_string = runtime.types.string_type
    t_string.fields = {
        "__iter__": OortNativeFunction(_iter, name="__iter__", mode=NativeMode.VALUE),
    }
    env.define(t_string.name, t_string)

    # List
    t_list = runtime.types.list_type
    t_list.fields = {
        "__iter__": OortNativeFunction(_iter, name="__iter__", mode=NativeMode.VALUE),
        "length": OortNativeFunction(_len, mode=NativeMode.VALUE),
    }
    env.define(t_list.name, t_list)

    # Tuple
    t_tuple = runtime.types.tuple_type
    t_tuple.fields = {
        "__iter__": OortNativeFunction(_iter, name="__iter__", mode=NativeMode.VALUE),
        "length": OortNativeFunction(_len, mode=NativeMode.VALUE),
    }
    env.define(t_tuple.name, t_tuple)

    # Dict
    t_dict = runtime.types.dict_type
    t_dict.fields = {
        "__iter__": OortNativeFunction(_iter, name="__iter__", mode=NativeMode.VALUE),
        "length": OortNativeFunction(_len, mode=NativeMode.VALUE),
    }
    env.define(t_dict.name, t_dict)

    # Set
    t_set = runtime.types.set_type
    t_set.fields = {
        "__iter__": OortNativeFunction(_iter, name="__iter__", mode=NativeMode.VALUE),
        "length": OortNativeFunction(_len, mode=NativeMode.VALUE),
    }
    env.define(t_set.name, t_set)

    # Iterator
    t_iterator = runtime.types.iterator_type
    t_iterator.fields = {
        "__iter__": OortNativeFunction(lambda value: value, name="__iter__", mode=NativeMode.VALUE),
    }
    env.define(t_iterator.name, t_iterator)

    # === Builtin functions
    _define_native_function(env, "print", print, mode=NativeMode.VALUE)
    _define_native_function(env, "clock", time.perf_counter)
    _define_native_function(env, "type", lambda obj: obj.type, mode=NativeMode.VALUE)
    _define_native_function(env, "len", _len, mode=NativeMode.VALUE)
    _define_native_function(env, "range", range)
    # Keep Oort objects wrapped so their own `__str__` / `__repr__` decide
    # the display syntax (containers use Oort literal delimiters).
    _define_native_function(env, "str", str, mode=NativeMode.VALUE)
    _define_native_function(env, "repr", repr, mode=NativeMode.VALUE)
    _define_native_function(env, "int", int)
    _define_native_function(env, "float", float)
    _define_native_function(env, "bool", bool)

    # === Collection helpers (eager, CONTEXT mode)
    define_collection_builtins(env)

    # === Builtin variables
