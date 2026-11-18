#! /usr/bin/env python

"""Function signatures and argument binding."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..ast.nodes.argument import ArgumentKind
from ..ast.nodes.declarations import Parameter, ParameterKind
from .call_args import ArgumentBindingError, normalize_args

if TYPE_CHECKING:
    from ..ast.nodes.function_def import FunctionDef
    from .objects import OortObject


_NAMED_KINDS = (ParameterKind.POS_ONLY, ParameterKind.DEFAULT, ParameterKind.KW_ONLY)


class Signature:
    """Classified parameters of a user callable."""

    def __init__(self, params: list[Parameter]):
        self.params = list(params)
        self.positional_only: list[Parameter] = []
        self.positional_or_keyword: list[Parameter] = []
        self.var_positional: Parameter | None = None
        self.keyword_only: list[Parameter] = []
        self.var_keyword: Parameter | None = None
        self.block: Parameter | None = None

        for param in self.params:
            if param.kind == ParameterKind.POS_ONLY:
                self.positional_only.append(param)
            elif param.kind == ParameterKind.DEFAULT:
                self.positional_or_keyword.append(param)
            elif param.kind == ParameterKind.VAR_POS:
                self.var_positional = param
            elif param.kind == ParameterKind.KW_ONLY:
                self.keyword_only.append(param)
            elif param.kind == ParameterKind.VAR_KW:
                self.var_keyword = param
            elif param.kind == ParameterKind.BLOCK:
                self.block = param
            else:
                raise ValueError(f"Invalid parameter kind {param.kind}")

    @property
    def positional_params(self) -> list[Parameter]:
        return [*self.positional_only, *self.positional_or_keyword]

    @property
    def ordered_params(self) -> list[Parameter]:
        result = [*self.positional_only, *self.positional_or_keyword]
        if self.var_positional is not None:
            result.append(self.var_positional)
        result.extend(self.keyword_only)
        if self.var_keyword is not None:
            result.append(self.var_keyword)
        if self.block is not None:
            result.append(self.block)
        return result

    def positional_only_names(self) -> set[str]:
        return {param.name for param in self.positional_only}

    def keyword_target(self, name: str) -> Parameter | None:
        for param in (*self.positional_or_keyword, *self.keyword_only):
            if param.name == name:
                return param
        if self.block is not None and self.block.name == name:
            return self.block
        return None

    def bind(self, interpreter, args, closure, name: str):
        """Bind evaluated arguments and return the call environment."""
        from .environment import Environment
        from .objects import OortDict, OortNull, OortString, OortTuple

        args = normalize_args(args)

        provided: dict[str, OortObject] = {}
        extra_pos: list[OortObject] = []
        extra_kw: dict[str, OortObject] = {}
        block: OortObject | None = None
        seen_keyword = False
        positional_count = 0
        pos_params = self.positional_params
        pos_index = 0

        for arg in args:
            if arg.kind == ArgumentKind.BLOCK and self.block is not None:
                if block is not None:
                    raise ArgumentBindingError(
                        f"{name}() got multiple values for argument {self.block.name!r}"
                    )
                block = arg.value
                continue

            if arg.keyword is None:
                # A trailing block is syntactic sugar for the last positional
                # argument; it may follow keyword arguments when the callee has
                # no `&block` parameter, and it skips slots already filled by
                # keyword arguments.
                block_positional = arg.kind == ArgumentKind.BLOCK
                if seen_keyword and not block_positional:
                    raise ArgumentBindingError(
                        f"{name}(): positional argument follows keyword argument"
                    )
                positional_count += 1
                if block_positional:
                    while pos_index < len(pos_params) and pos_params[pos_index].name in provided:
                        pos_index += 1
                if pos_index < len(pos_params):
                    provided[pos_params[pos_index].name] = arg.value
                    pos_index += 1
                elif self.var_positional is not None:
                    extra_pos.append(arg.value)
                else:
                    raise ArgumentBindingError(
                        f"{name}() takes {len(pos_params)} positional arguments "
                        f"but {positional_count} were given"
                    )
                continue

            seen_keyword = True
            if arg.keyword in extra_kw:
                raise ArgumentBindingError(
                    f"{name}() got multiple values for argument {arg.keyword!r}"
                )

            if arg.keyword in self.positional_only_names():
                if self.var_keyword is not None:
                    extra_kw[arg.keyword] = arg.value
                    continue
                raise ArgumentBindingError(f"{name}() argument {arg.keyword!r} is positional-only")

            param = self.keyword_target(arg.keyword)
            if param is None:
                if self.var_keyword is not None:
                    extra_kw[arg.keyword] = arg.value
                    continue
                raise ArgumentBindingError(
                    f"{name}() got an unexpected keyword argument {arg.keyword!r}"
                )
            if arg.keyword in provided:
                raise ArgumentBindingError(
                    f"{name}() got multiple values for argument {arg.keyword!r}"
                )
            provided[param.name] = arg.value

        missing = [
            param.name
            for param in self.ordered_params
            if param.kind in _NAMED_KINDS
            and param.name not in provided
            and param.default_value is None
        ]
        if missing:
            if len(missing) == 1:
                raise ArgumentBindingError(f"{name}() missing required argument {missing[0]!r}")
            joined = ", ".join(repr(item) for item in missing)
            raise ArgumentBindingError(f"{name}() missing required arguments: {joined}")

        env = Environment(outer=closure, name=name)
        for param in self.ordered_params:
            if param.kind in _NAMED_KINDS:
                if param.name in provided:
                    value = provided[param.name]
                else:
                    assert param.default_value is not None
                    previous_env = interpreter.env
                    try:
                        interpreter.env = env
                        value = param.default_value.accept(interpreter)
                    finally:
                        interpreter.env = previous_env
            elif param.kind == ParameterKind.VAR_POS:
                value = OortTuple(tuple(extra_pos))
            elif param.kind == ParameterKind.VAR_KW:
                value = OortDict({OortString(key): item for key, item in extra_kw.items()})
            elif param.kind == ParameterKind.BLOCK:
                if param.name in provided:
                    if block is not None:
                        raise ArgumentBindingError(
                            f"{name}() got multiple values for argument {param.name!r}"
                        )
                    value = provided[param.name]
                else:
                    value = block if block is not None else OortNull.get_null_value()
            else:
                raise AssertionError(f"Unexpected parameter kind {param.kind}")

            env.define(param.name, value)

        return env


def get_signature(node: FunctionDef) -> Signature:
    """Build and cache the signature of a function/lambda node."""
    signature = getattr(node, "_signature", None)
    if signature is None:
        signature = Signature(node.params)
        node._signature = signature
    return signature


def build_call_env(node: FunctionDef, interpreter, args, closure, name: str):
    """Build the call environment for a function, lambda or method."""
    from .environment import Environment

    args = normalize_args(args)

    if node.anonymous_count:
        if any(arg.keyword is not None for arg in args):
            raise ArgumentBindingError(f"{name}() does not accept keyword arguments")
        values = [arg.value for arg in args]
        if len(values) != node.anonymous_count:
            raise ArgumentBindingError(
                f"{name}() takes {node.anonymous_count} arguments but {len(values)} were given"
            )
        env = Environment(outer=closure, name=name)
        for index, value in enumerate(values):
            env.define(f"${index}", value)
        return env

    return get_signature(node).bind(interpreter, args, closure, name)
