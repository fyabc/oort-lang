#! /usr/bin/env python

"""Eager collection helpers exposed as global builtins."""

from functools import cmp_to_key

from ..environment import Environment
from ..functions import OortNativeFunction
from ..native import NativeContext, NativeMode
from ..objects import OortInt, OortList, OortNull, OortTuple


def _map(ctx: NativeContext, iterable, callback):
    items = ctx.iterate(iterable)
    return OortList([ctx.call(callback, [item]) for item in items])


def _filter(ctx: NativeContext, iterable, predicate):
    items = ctx.iterate(iterable)
    if isinstance(predicate, OortNull):
        return OortList([item for item in items if ctx.truthy(item)])
    return OortList([item for item in items if ctx.truthy(ctx.call(predicate, [item]))])


def _zip(ctx: NativeContext, *iterables):
    if not iterables:
        return OortList([])
    rows = [ctx.iterate(iterable) for iterable in iterables]
    length = min(len(row) for row in rows)
    return OortList([OortTuple(tuple(row[index] for row in rows)) for index in range(length)])


def _enumerate(ctx: NativeContext, iterable, start=None):
    if start is None:
        first = 0
    elif isinstance(start, OortInt):
        first = start.host_value
    else:
        raise TypeError("enumerate() start must be an Int")

    items = ctx.iterate(iterable)
    return OortList([OortTuple((OortInt(first + index), item)) for index, item in enumerate(items)])


def _sorted(ctx: NativeContext, iterable, key=None, reverse=None):
    items = ctx.iterate(iterable)
    if key is None or isinstance(key, OortNull):
        keys = items
    else:
        keys = [ctx.call(key, [item]) for item in items]

    def compare(left: int, right: int) -> int:
        if ctx.truthy(ctx.binary("<", keys[left], keys[right])):
            return -1
        if ctx.truthy(ctx.binary("<", keys[right], keys[left])):
            return 1
        return 0

    descending = reverse is not None and ctx.truthy(reverse)
    order = sorted(
        range(len(items)),
        key=cmp_to_key(compare),
        reverse=descending,
    )
    return OortList([items[index] for index in order])


def define_collection_builtins(env: Environment):
    """Define map/filter/zip/enumerate/sorted in the builtins scope."""
    for name, func in {
        "map": _map,
        "filter": _filter,
        "zip": _zip,
        "enumerate": _enumerate,
        "sorted": _sorted,
    }.items():
        env.define(
            name,
            OortNativeFunction(func, name=name, mode=NativeMode.CONTEXT),
        )
