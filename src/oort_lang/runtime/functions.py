#! /usr/bin/env python

"""Callable Oort objects."""

from collections.abc import Callable
from typing import TYPE_CHECKING

from .context import get_runtime
from .control_flow_exceptions import OortReturn
from .objects import OortInstance, OortNativeMixin, OortObject, wrap_value
from .signature import build_call_env

if TYPE_CHECKING:
    from ..ast import nodes
    from .environment import Environment
    from .type_system import OortType


class OortCallableMixin:
    """Callable objects."""

    @classmethod
    def get_type_object(cls) -> "OortType":
        return get_runtime().types.for_class(cls)

    @property
    def arity(self) -> int:
        """Get arity."""
        raise NotImplementedError

    def __call__(self, interpreter, args):
        raise NotImplementedError


class OortFunctionMixin(OortCallableMixin):
    def __init__(self, name: str = "<lambda>"):
        # Cooperative init: the next class in the concrete MRO is an OortObject.
        super().__init__(type_=self.get_type_object())  # type: ignore[call-arg]
        self.name = name


class OortNativeFunction(OortFunctionMixin, OortNativeMixin, OortObject):
    """Oort native function object."""

    def __init__(self, value: Callable, name: str = "<lambda>", unwrap: bool = True):
        super().__init__(name=name)
        self.value = value
        self.unwrap = unwrap

    def __repr__(self):
        return f"<Built-in function {self.name}>"

    def __call__(self, interpreter, args):
        if self.unwrap:
            result = self.value(*(arg.py_value for arg in args))
        else:
            result = self.value(*args)
        return wrap_value(result)

    @property
    def py_value(self):
        """Get Python value."""
        return self.value


class OortFunction(OortFunctionMixin, OortInstance):
    """Oort function object."""

    def __init__(self, node: "nodes.FunctionDef", closure: "Environment"):
        super().__init__(name=node.name)
        self.node = node
        self.closure = closure

    def __repr__(self):
        return f"<Function {self.name} at {hex(id(self))}>"

    @property
    def arity(self) -> int:
        return self.node.param_count

    def __call__(self, interpreter, args):
        call_env = build_call_env(self.node, interpreter, args, self.closure, self.name)
        try:
            result = interpreter.run_block(self.node.body, call_env)
        except OortReturn as e:
            result = e.value
        return result


class OortMethodMixin(OortCallableMixin):
    def __init__(self, this: OortObject, name: str = "<lambda>"):
        # Cooperative init: the next class in the concrete MRO is an OortObject.
        super().__init__(type_=self.get_type_object())  # type: ignore[call-arg]
        self.this = this
        self.name = name


class OortNativeMethod(OortMethodMixin, OortNativeMixin, OortObject):
    """Oort native bound method object."""

    def __init__(self, this: OortObject, value: Callable, name: str = "<lambda>"):
        super().__init__(this, name)
        self.value = value

    def __repr__(self):
        return f"<Built-in bound method {self.this.type.name}.{self.name} of {self.this}>"

    def __call__(self, interpreter, args):
        result = self.value(self.this.py_value, *(arg.py_value for arg in args))
        return wrap_value(result)

    @classmethod
    def from_native_func(cls, this: OortObject, func: OortNativeFunction):
        return cls(this, value=func.value, name=func.name)

    @property
    def py_value(self):
        """Get Python value."""
        return self.value


class OortMethod(OortMethodMixin, OortInstance):
    """Oort bound method object."""

    def __init__(
        self,
        this: OortObject,
        node: "nodes.FunctionDef",
        closure: "Environment",
        defining_type: "OortType | None" = None,
    ):
        super().__init__(this, name=node.name)
        self.node = node
        self.closure = closure
        self.defining_type = defining_type

    def __repr__(self):
        return f"<Bound method {self.this.type.name}.{self.name} of {self.this} at {hex(id(self))}>"

    @property
    def is_initializer(self) -> bool:
        return self.name == "__init__"

    @property
    def arity(self) -> int:
        return self.node.param_count

    def __call__(self, interpreter, args):
        call_env = build_call_env(self.node, interpreter, args, self.closure, self.name)

        # `this` is bound after defaults; default expressions cannot depend on
        # the instance (OP 0011 D7).
        call_env.define("this", self.this)

        prev_method = getattr(interpreter, "_current_method", None)
        interpreter._current_method = self
        try:
            result = interpreter.run_block(self.node.body, call_env)
        except OortReturn as e:
            result = e.value
        finally:
            interpreter._current_method = prev_method
        if self.is_initializer:
            result = self.this
        return result
