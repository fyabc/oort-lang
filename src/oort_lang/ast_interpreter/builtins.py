#! /usr/bin/env python

"""Builtin Oort types and values in AST-interpreter."""

import operator
import time
from collections.abc import Callable

from .environment import Environment
from .objects import *


def _define_native_function(env: Environment, name: str, func: Callable, **kwargs):
    """Define a builtin function."""
    env.define(name, OortNativeFunction(func, name=name, **kwargs))


def setup_builtins(runtime: Runtime, env: Environment):
    """Setup all builtin names for one runtime."""

    # === Builtin types
    # Type
    t_type = runtime.types.type_type
    t_type.fields = {
        "mro": OortNativeFunction(OortType.mro, name="mro"),
        "__op_le__": OortNativeFunction(lambda t1, t2: t1.is_subclass_of(t2)),
        "__op_lt__": OortNativeFunction(lambda t1, t2: t1.is_subclass_of(t2) and t1 is not t2),
        "__op_ge__": OortNativeFunction(lambda t1, t2: t2.is_subclass_of(t1)),
        "__op_gt__": OortNativeFunction(lambda t1, t2: t2.is_subclass_of(t1) and t1 is not t2),
    }
    env.define(t_type.name, t_type)

    # Object
    t_object = runtime.types.object_type
    t_object.fields = {
        "__op_eq__": OortNativeFunction(operator.eq),
        "__op_ne__": OortNativeFunction(operator.ne),
        "__str__": OortNativeFunction(str),
        "__repr__": OortNativeFunction(repr),
    }
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
    t_int.fields = {
        "__op_neg__": OortNativeFunction(operator.neg),
        "__op_add__": OortNativeFunction(operator.add),
        "__op_sub__": OortNativeFunction(operator.sub),
        "__op_mul__": OortNativeFunction(operator.mul),
        "__op_truediv__": OortNativeFunction(operator.truediv),
        "__op_floordiv__": OortNativeFunction(operator.floordiv),
        "__op_mod__": OortNativeFunction(operator.mod),
        "__op_pow__": OortNativeFunction(operator.pow),
    }
    env.define(t_int.name, t_int)

    # Float
    t_float = runtime.types.float_type
    t_float.bases = []
    t_float.fields = {
        "__op_neg__": OortNativeFunction(operator.neg),
        "__op_add__": OortNativeFunction(operator.add),
        "__op_sub__": OortNativeFunction(operator.sub),
        "__op_mul__": OortNativeFunction(operator.mul),
        "__op_truediv__": OortNativeFunction(operator.truediv),
        "__op_floordiv__": OortNativeFunction(operator.floordiv),
        "__op_mod__": OortNativeFunction(operator.mod),
        "__op_pow__": OortNativeFunction(operator.pow),
    }
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
        "__op_add__": OortNativeFunction(operator.add),
        "__op_mul__": OortNativeFunction(operator.mul),
    }
    env.define(t_string.name, t_string)

    # List
    t_list = runtime.types.list_type
    t_list.fields = {
        "length": OortNativeFunction(len),
        "__op_getitem__": OortNativeFunction(operator.getitem),
        "__op_setitem__": OortNativeFunction(operator.setitem),
        "__op_delitem__": OortNativeFunction(operator.delitem),
        "__op_contains__": OortNativeFunction(operator.contains),
        "__op_add__": OortNativeFunction(operator.add),
    }
    env.define(t_list.name, t_list)

    # Tuple
    t_tuple = runtime.types.tuple_type
    t_tuple.fields = {
        "length": OortNativeFunction(len),
        "__op_getitem__": OortNativeFunction(operator.getitem),
        "__op_contains__": OortNativeFunction(operator.contains),
        "__op_add__": OortNativeFunction(operator.add),
    }
    env.define(t_tuple.name, t_tuple)

    # Dict
    t_dict = runtime.types.dict_type
    t_dict.fields = {
        "length": OortNativeFunction(len),
        "__op_getitem__": OortNativeFunction(operator.getitem),
        "__op_setitem__": OortNativeFunction(operator.setitem),
        "__op_delitem__": OortNativeFunction(operator.delitem),
        "__op_contains__": OortNativeFunction(operator.contains),
    }
    env.define(t_dict.name, t_dict)

    # Set
    t_set = runtime.types.set_type
    t_set.fields = {
        "length": OortNativeFunction(len),
        "__op_contains__": OortNativeFunction(operator.contains),
    }
    env.define(t_set.name, t_set)

    # === Builtin functions
    _define_native_function(env, "print", print, unwrap=False)
    _define_native_function(env, "clock", time.perf_counter)
    _define_native_function(env, "type", lambda obj: obj.type, unwrap=False)
    _define_native_function(env, "super", OortSuperProxy, unwrap=False)
    _define_native_function(env, "len", len)
    _define_native_function(env, "range", range)
    # Keep Oort objects wrapped so their own `__str__` / `__repr__` decide
    # the display syntax (containers use Oort literal delimiters).
    _define_native_function(env, "str", str, unwrap=False)
    _define_native_function(env, "repr", repr, unwrap=False)
    _define_native_function(env, "int", int)
    _define_native_function(env, "float", float)
    _define_native_function(env, "bool", bool)

    # === Builtin variables
