#! /usr/bin/env python

"""Internal representation of Oort objects in AST-interpreter."""

import operator
from collections.abc import Callable
from typing import TYPE_CHECKING

from .call_args import ArgumentBindingError
from .control_flow_exceptions import OortReturn
from .signature import build_call_env

if TYPE_CHECKING:
    from ..ast import nodes
    from .environment import Environment

__all__ = [
    "OortBool",
    "OortDict",
    "OortFloat",
    "OortFunction",
    "OortFunctionMixin",
    "OortInstance",
    "OortInt",
    "OortList",
    "OortMethod",
    "OortMethodMixin",
    "OortNativeFunction",
    "OortNativeMethod",
    "OortNativeMixin",
    "OortNull",
    "OortObject",
    "OortSet",
    "OortSlice",
    "OortString",
    "OortSuperProxy",
    "OortTuple",
    "OortType",
    "setup_type_system",
    "wrap_value",
]


def _get_operator_from_cls(
    symbol: str, operand_count: int, start_type: "OortType", receiver: "OortObject"
) -> "OortObject | None":
    """Look up an operator method in the class MRO and bind it to `receiver`.

    Operator methods live in `OortType.operators`, keyed by (symbol, operand
    count), so unary and binary forms of the same symbol (e.g. `-x` and
    `x - y`) can coexist.
    """
    key = (symbol, operand_count)
    for mro_type in start_type.mro():
        value = mro_type.operators.get(key)
        if value is not None:
            if isinstance(value, OortFunction):
                return OortMethod(
                    this=receiver, node=value.node, closure=value.closure, defining_type=mro_type
                )
            elif isinstance(value, OortNativeFunction):
                return OortNativeMethod.from_native_func(this=receiver, func=value)
            else:
                return value
    return None


def _get_from_cls(name: str, start_type: "OortType", receiver: "OortObject") -> "OortObject | None":
    """Search method from class MRO and metaclass MRO."""

    # Search from class MRO.
    for mro_type in start_type.mro():
        value = mro_type.fields.get(name, None)
        if value is not None:
            # Wrap into methods.
            if isinstance(value, OortFunction):
                return OortMethod(
                    this=receiver, node=value.node, closure=value.closure, defining_type=mro_type
                )
            elif isinstance(value, OortNativeFunction):
                return OortNativeMethod.from_native_func(this=receiver, func=value)
            else:
                return value

    if start_type is not OortType.get_type_object():
        # `Type.type is Type`, so skip resolution.
        # Search from super metaclasses (bind with receiver.type).
        # TODO: Add complier option to disallow call class methods from instance.
        meta_mro = start_type.type.mro()
        for mro_type in meta_mro:
            value = mro_type.fields.get(name, None)
            if value is not None:
                # Wrap into class methods.
                if isinstance(value, OortFunction):
                    return OortMethod(this=receiver.type, node=value.node, closure=value.closure)
                elif isinstance(value, OortNativeFunction):
                    return OortNativeMethod.from_native_func(this=receiver.type, func=value)
                else:
                    return value

    return None


class OortObject:
    """Base class of all Oort objects in AST-interpreter."""

    TYPE_OBJ: "OortType" = None

    def __init__(self, type_: "OortType"):
        self.type = type_

    def __repr__(self):
        return f"<{self.type.name} object at {hex(id(self))}>"

    @property
    def py_value(self):
        """Get Python value."""
        return self

    @property
    def is_native(self) -> bool:
        return False

    @classmethod
    def get_type_object(cls) -> "OortType":
        """Get the unique type object of this type."""
        assert cls.TYPE_OBJ is not None
        return cls.TYPE_OBJ

    def get(self, name: str) -> "OortObject | None":
        # Search from instance-level fields.
        if hasattr(self, "fields"):
            value = self.fields.get(name, None)
            if value is not None:
                if self is OortType.get_type_object() and isinstance(value, OortNativeFunction):
                    # Special case for `Type` object.
                    return OortNativeMethod.from_native_func(this=self, func=value)
                else:
                    return value

        value = _get_from_cls(name=name, start_type=self.type, receiver=self)
        if value is not None:
            return value

        # TODO: missing fallback.
        return None


class OortInstance(OortObject):
    """User-defined objects."""

    def __init__(self, type_: "OortType"):
        super().__init__(type_)

        # Instance can have its own fields.
        self.fields: dict[str, OortObject] = {}

    def set(self, name: str, value: OortObject):
        # Set to instance-level fields.
        self.fields[name] = value


class OortNativeMixin(OortObject):
    """Native objects."""

    @property
    def is_native(self) -> bool:
        return True


class OortCallableMixin:
    """Callable objects."""

    @property
    def arity(self) -> int:
        """Get arity."""
        raise NotImplementedError

    def __call__(self, interpreter, args):
        raise NotImplementedError


class OortType(OortInstance, OortCallableMixin):
    """Oort type objects."""

    TYPE_OBJ: "OortType" = None

    def __init__(
        self, name: str, fields: dict | None = None, bases: list["OortType"] | None = None
    ):
        super().__init__(type_=None)  # Lazy init.

        self.name = name
        if fields:
            self.fields.update(fields)
        self.bases: list[OortType] = bases or []
        self._mro_cache = None
        self._has_class_method: bool = False
        # Operator methods, keyed by (symbol, operand count).
        self.operators: dict[tuple[str, int], OortObject] = {}

    def __repr__(self):
        return f"<Type {self.name!r}>"

    def get(self, name: str) -> "OortObject | None":
        """Look up class attributes.

        Class objects need two lookup domains: the class MRO (ordinary
        attributes and methods, returned unbound) and the metaclass MRO
        (class methods, bound to the class). `OortObject.get` only knows
        about the latter, so handle the class MRO here first.
        """
        for mro_type in self.mro():
            value = mro_type.fields.get(name, None)
            if value is not None:
                return value
        return super().get(name)

    def _find_defining_type(self, name: str) -> "OortType | None":
        """Find the type in the MRO that defines `name`."""
        for mro_type in self.mro():
            if name in mro_type.fields:
                return mro_type
        return None

    @classmethod
    def create_type_object(
        cls,
        name: str,
        fields: dict | None = None,
        bases: list | None = None,
        metaclass: "OortType | None" = None,
    ):
        """Create type object, resolve bases and metaclass."""
        type_obj = cls(name=name, fields=fields, bases=bases)

        # Calculate correct metaclass.
        winner = metaclass or cls.get_type_object()
        for base_type in type_obj.mro()[1:]:
            base_metatype = base_type.type
            if winner.is_subclass_of(base_metatype):
                continue
            if base_metatype.is_subclass_of(winner):
                winner = base_metatype
                continue
            raise TypeError(
                "Metaclass conflict: the metaclass of a derived class must be a (non-strict) "
                "subclass of the metaclasses of all its bases."
            )
        type_obj.type = winner
        return type_obj

    def set_operator(self, symbol: str, operand_count: int, value: OortObject):
        """Register an operator method (`def operator "<sym>"`)."""
        self.operators[(symbol, operand_count)] = value

    def set_class_field(self, name: str, value: OortObject):
        """Set class-level fields, create metaclass if not exist."""
        if not self._has_class_method:
            new_type = OortType(name=f"{self.name}#Meta", fields={name: value}, bases=[self.type])
            new_type.type = self.type
            self.type = new_type
            self._has_class_method = True
        else:
            self.type.set(name, value)

    @property
    def arity(self) -> int:
        init_func = self.get("__init__")
        if init_func is None:
            return 0
        assert isinstance(init_func, OortFunction)
        return init_func.arity

    def __call__(self, interpreter, args):
        instance = OortInstance(type_=self)

        # Call initializer.
        init_func = self.get("__init__")
        if init_func is None:
            if args:
                raise ArgumentBindingError(
                    f"{self.name}() takes 0 arguments but {len(args)} were given"
                )
            return instance

        assert isinstance(init_func, OortFunction)
        init_method = OortMethod(
            this=instance,
            node=init_func.node,
            closure=init_func.closure,
            defining_type=self._find_defining_type("__init__"),
        )
        init_method(interpreter, args)
        return instance

    def mro(self) -> list["OortType"]:
        if not self._mro_cache:
            self._build_mro()
        return self._mro_cache

    def _build_mro(self):
        """Build MRO cache, using C3-linear algorithm."""
        if not self.bases:
            self._mro_cache = [self, OortObject.get_type_object()]
            return
        parent_mros = [list(base.mro()) for base in self.bases]
        parent_mros.append(list(self.bases))

        self._mro_cache = [self, *self._c3_merge(parent_mros)]
        if self._mro_cache[-1] != OortObject.get_type_object():
            self._mro_cache.append(OortObject.get_type_object())

    @staticmethod
    def _c3_merge(sequences):
        """C3 merge algorithm."""
        result = []
        while True:
            sequences = [seq for seq in sequences if seq]
            if not sequences:
                return result

            for seq in sequences:
                candidate = seq[0]
                if not any(candidate in s[1:] for s in sequences):
                    result.append(candidate)
                    for s in sequences:
                        if s and s[0] == candidate:
                            s.pop(0)
                    break
            else:
                raise TypeError(
                    "Cannot create a consistent method resolution order (MRO) for bases."
                )

    def is_subclass_of(self, other: "OortType") -> bool:
        """Check if `self` is subclass of `other`."""
        return other in self.mro()

    @property
    def is_metaclass(self) -> bool:
        return self.get_type_object() in self.mro()


class OortFunctionMixin(OortCallableMixin):
    TYPE_OBJ: "OortType" = None

    def __init__(self, name: str = "<lambda>"):
        super().__init__(type_=self.get_type_object())
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
    TYPE_OBJ: "OortType" = None

    def __init__(self, this: OortObject, name: str = "<lambda>"):
        super().__init__(type_=self.get_type_object())
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


_CALLABLE_CLASS_MEMBERS = (OortFunction, OortNativeFunction, OortMethod, OortNativeMethod)


def find_callable_class_member(name: str, start_type: "OortType") -> "OortObject | None":
    """Find the callable class member that `name` resolves to, if any.

    Lookup follows the instance attribute order used by `OortObject.get`:
    the class MRO first, then the metaclass MRO (class methods). A
    non-callable class member stops the search and is returned as no conflict;
    callers may let an instance field shadow it (OP 0007 leaves the priority
    of non-callable class attributes undefined).
    """
    for mro_type in start_type.mro():
        value = mro_type.fields.get(name)
        if value is not None:
            return value if isinstance(value, _CALLABLE_CLASS_MEMBERS) else None

    metaclass = start_type.type
    if metaclass is not None:
        for mro_type in metaclass.mro():
            value = mro_type.fields.get(name)
            if value is not None:
                return value if isinstance(value, _CALLABLE_CLASS_MEMBERS) else None

    return None


class OortSuperProxy(OortNativeMixin, OortObject):
    """Oort super proxy object."""

    TYPE_OBJ: "OortType" = None

    def __init__(self, cls: "OortType", receiver: OortObject):
        super().__init__(type_=self.get_type_object())
        self.cls = cls
        self.receiver = receiver

        if not isinstance(cls, OortType):
            raise RuntimeError(f"{cls} is not a type")
        if not receiver.type.is_subclass_of(cls):
            raise RuntimeError(f"{receiver} is not an instance of {cls}")

    def __repr__(self):
        return f"<SuperProxy: {self.cls}, {self.receiver!r}>"

    def get(self, name: str) -> OortObject | None:
        # Search from super classes.
        mro = self.receiver.type.mro()
        start_idx = mro.index(self.cls) + 1
        start_type = mro[start_idx]

        value = _get_from_cls(name=name, start_type=start_type, receiver=self.receiver)
        if value is not None:
            return value

        # TODO: missing fallback.

        return None


class OortNull(OortNativeMixin, OortObject):
    """Oort null object."""

    TYPE_OBJ: "OortType" = None
    NULL_V = None

    def __init__(self):
        super().__init__(type_=self.get_type_object())

    @classmethod
    def get_null_value(cls):
        """Get null value."""
        if cls.NULL_V is None:
            cls.NULL_V = cls()
        return cls.NULL_V

    def __repr__(self):
        return "null"

    def __str__(self):
        return "null"

    @property
    def py_value(self):
        """Get Python value."""
        return None


class OortBool(OortNativeMixin, OortObject):
    """Oort boolean object."""

    TYPE_OBJ: "OortType" = None
    TRUE_V = None
    FALSE_V = None

    def __init__(self, value: bool):
        super().__init__(type_=self.get_type_object())
        self.value = value

    @classmethod
    def get_true_value(cls):
        """Get true value."""
        if cls.TRUE_V is None:
            cls.TRUE_V = cls(value=True)
        return cls.TRUE_V

    @classmethod
    def get_false_value(cls):
        """Get false value."""
        if cls.FALSE_V is None:
            cls.FALSE_V = cls(value=False)
        return cls.FALSE_V

    @classmethod
    def get_bool_value(cls, value: bool):
        """Get boolean value."""
        return cls.get_true_value() if value else cls.get_false_value()

    def __repr__(self):
        return "true" if self.value else "false"

    def __eq__(self, other):
        return isinstance(other, OortBool) and self.value == other.value

    def __hash__(self):
        return hash(self.value)

    @property
    def py_value(self):
        """Get Python value."""
        return self.value


class OortInt(OortNativeMixin, OortObject):
    """Oort integer object."""

    TYPE_OBJ: "OortType" = None

    def __init__(self, value: int):
        super().__init__(type_=self.get_type_object())
        self.value = value

    def __repr__(self):
        return str(self.value)

    def __eq__(self, other):
        return isinstance(other, OortInt) and self.value == other.value

    def __hash__(self):
        return hash(self.value)

    @property
    def py_value(self):
        """Get Python value."""
        return self.value


class OortFloat(OortNativeMixin, OortObject):
    """Oort float object."""

    TYPE_OBJ: "OortType" = None

    def __init__(self, value: float):
        super().__init__(type_=self.get_type_object())
        self.value = value

    def __repr__(self):
        return str(self.value)

    def __eq__(self, other):
        return isinstance(other, OortFloat) and self.value == other.value

    def __hash__(self):
        return hash(self.value)

    @property
    def py_value(self):
        """Get Python value."""
        return self.value


class OortString(OortNativeMixin, OortObject):
    """Oort string object."""

    TYPE_OBJ: "OortType" = None

    def __init__(self, value: str):
        super().__init__(type_=self.get_type_object())
        self.value = value

    def __repr__(self):
        return repr(self.value)

    def __str__(self):
        return self.value

    def __eq__(self, other):
        return isinstance(other, OortString) and self.value == other.value

    def __hash__(self):
        return hash(self.value)

    def __getitem__(self, item: "OortObject"):
        index = item.py_value
        result = self.value[index]
        if isinstance(index, slice):
            return OortString(result)
        return OortString(result)

    def __len__(self):
        return len(self.value)

    def __iter__(self):
        return (OortString(char) for char in self.value)

    @property
    def py_value(self):
        """Get Python value."""
        return self.value


class OortList(OortObject):
    """Oort list object."""

    TYPE_OBJ: "OortType" = None

    def __init__(self, value: list[OortObject]):
        super().__init__(type_=self.get_type_object())
        self.value = value

    def __getitem__(self, item: "OortObject"):
        index = item.py_value
        result = self.value[index]
        if isinstance(index, slice):
            return OortList(result)
        return result

    def __setitem__(self, key: "OortObject", value: "OortObject"):
        self.value[key.py_value] = value

    def __len__(self):
        return len(self.value)

    def __iter__(self):
        return iter(self.value)

    def __repr__(self):
        return repr(self.value)

    def __str__(self):
        return "[" + ", ".join(str(item) for item in self.value) + "]"

    def __hash__(self):
        raise TypeError("unhashable type: 'List'")

    @property
    def py_value(self):
        """Get Python value."""
        return [item.py_value for item in self.value]


class OortTuple(OortObject):
    """Oort tuple object (immutable)."""

    TYPE_OBJ: "OortType" = None

    def __init__(self, value: tuple[OortObject, ...]):
        super().__init__(type_=self.get_type_object())
        self.value = value

    def __getitem__(self, item: "OortObject"):
        index = item.py_value
        result = self.value[index]
        if isinstance(index, slice):
            return OortTuple(result)
        return result

    def __len__(self):
        return len(self.value)

    def __iter__(self):
        return iter(self.value)

    def __eq__(self, other):
        return isinstance(other, OortTuple) and self.value == other.value

    def __hash__(self):
        return hash(self.value)

    def __repr__(self):
        if len(self.value) == 1:
            return f"({self.value[0]!r},)"
        return repr(self.value)

    def __str__(self):
        if len(self.value) == 1:
            return f"({self.value[0]},)"
        return "(" + ", ".join(str(item) for item in self.value) + ")"

    @property
    def py_value(self):
        """Get Python value."""
        return tuple(item.py_value for item in self.value)


class OortDict(OortObject):
    """Oort dictionary object."""

    TYPE_OBJ: "OortType" = None

    def __init__(self, value: dict[OortObject, OortObject] | None = None):
        super().__init__(type_=self.get_type_object())
        self.value = {} if value is None else value

    def __getitem__(self, key: "OortObject"):
        return self.value[key]

    def __setitem__(self, key: "OortObject", value: "OortObject"):
        self.value[key] = value

    def __contains__(self, key: "OortObject"):
        return key in self.value

    def __len__(self):
        return len(self.value)

    def __iter__(self):
        return iter(self.value)

    def __hash__(self):
        raise TypeError("unhashable type: 'Dict'")

    def __repr__(self):
        if not self.value:
            return "{:}"
        return "{: " + ", ".join(f"{k!r}: {v!r}" for k, v in self.value.items()) + " :}"

    def __str__(self):
        if not self.value:
            return "{:}"
        return "{: " + ", ".join(f"{k}: {v}" for k, v in self.value.items()) + " :}"

    @property
    def py_value(self):
        """Get Python value."""
        return {key.py_value: value.py_value for key, value in self.value.items()}


class OortSet(OortObject):
    """Oort set object."""

    TYPE_OBJ: "OortType" = None

    def __init__(self, value: set[OortObject] | None = None):
        super().__init__(type_=self.get_type_object())
        self.value = set() if value is None else value

    def __contains__(self, item: "OortObject"):
        return item in self.value

    def __len__(self):
        return len(self.value)

    def __iter__(self):
        return iter(self.value)

    def __hash__(self):
        raise TypeError("unhashable type: 'Set'")

    def __repr__(self):
        if not self.value:
            return "{.}"
        return "{. " + ", ".join(repr(item) for item in self.value) + " .}"

    def __str__(self):
        if not self.value:
            return "{.}"
        return "{. " + ", ".join(str(item) for item in self.value) + " .}"

    @property
    def py_value(self):
        """Get Python value."""
        return {item.py_value for item in self.value}


class OortSlice(OortObject):
    """Oort slice object, used as a subscript argument."""

    TYPE_OBJ: "OortType" = None

    def __init__(self, start: OortObject | None, stop: OortObject | None, step: OortObject | None):
        super().__init__(type_=self.get_type_object())
        self.start = start
        self.stop = stop
        self.step = step

    @property
    def py_value(self):
        """Get Python value."""
        return slice(
            None if self.start is None else self.start.py_value,
            None if self.stop is None else self.stop.py_value,
            None if self.step is None else self.step.py_value,
        )

    def __repr__(self):
        return f"slice({self.start}, {self.stop}, {self.step})"


def setup_type_system():
    """Setup type system (skip MRO resolution to avoid endless recursion)."""
    t_type = OortType(name="Type")
    t_type.type = t_type
    OortType.TYPE_OBJ = t_type

    t_object = OortType(name="Object")
    t_object.type = t_type
    OortObject.TYPE_OBJ = t_object

    t_type._mro_cache = [t_type, t_object]
    t_object._mro_cache = [t_object]

    def _setup_basic_type(name: str, cls, bases: list["OortType"] | None = None):
        t_name = OortType(name=name)
        t_name.type = t_type
        t_name.bases = bases or [t_object]
        t_name._mro_cache = [t_name]
        for base in t_name.bases:
            for base_type in base.mro():
                if base_type not in t_name._mro_cache:
                    t_name._mro_cache.append(base_type)
        cls.TYPE_OBJ = t_name
        return t_name

    _setup_basic_type("Function", OortFunctionMixin)
    _setup_basic_type("Method", OortMethodMixin)
    _setup_basic_type("SuperProxy", OortSuperProxy)
    t_null = _setup_basic_type("Null", OortNull)
    t_int = _setup_basic_type("Int", OortInt)
    # Bool is deliberately not a subtype of Int. `true + true` and
    # `true == 1` should not silently work just because Python's bool is int.
    t_bool = _setup_basic_type("Bool", OortBool)
    t_float = _setup_basic_type("Float", OortFloat)
    t_string = _setup_basic_type("String", OortString)
    t_list = _setup_basic_type("List", OortList)
    t_tuple = _setup_basic_type("Tuple", OortTuple)
    t_dict = _setup_basic_type("Dict", OortDict)
    t_set = _setup_basic_type("Set", OortSet)
    _setup_basic_type("Slice", OortSlice)

    _setup_native_operators(
        t_object=t_object,
        t_null=t_null,
        t_bool=t_bool,
        t_int=t_int,
        t_float=t_float,
        t_string=t_string,
        t_list=t_list,
        t_tuple=t_tuple,
        t_dict=t_dict,
        t_set=t_set,
    )


def _install_operators(
    type_obj: "OortType",
    unary: dict[str, Callable] | None = None,
    binary: dict[str, Callable] | None = None,
):
    """Install native operator implementations on a built-in type."""
    for symbol, func in (unary or {}).items():
        type_obj.operators[(symbol, 1)] = OortNativeFunction(func, name=f"operator {symbol}")
    for symbol, func in (binary or {}).items():
        type_obj.operators[(symbol, 2)] = OortNativeFunction(func, name=f"operator {symbol}")


def _setup_native_operators(
    t_object: "OortType",
    t_null: "OortType",
    t_bool: "OortType",
    t_int: "OortType",
    t_float: "OortType",
    t_string: "OortType",
    t_list: "OortType",
    t_tuple: "OortType",
    t_dict: "OortType",
    t_set: "OortType",
):
    """Define built-in operators as methods, like user-defined ones.

    Native operator functions receive Python values (`this.py_value` and the
    operands' `py_value`), because `OortNativeMethod` unwraps them before the
    call. Results are wrapped again by the interpreter.
    """
    comparisons = {
        "==": operator.eq,
        "<": operator.lt,
        "<=": operator.le,
        ">": operator.gt,
        ">=": operator.ge,
    }
    # `!=` and `!in` are derived from `==` and `in` unless a type overrides
    # them explicitly.

    def _bool_eq(lhs, rhs):
        # `False == 0` in Python; Oort keeps booleans and integers distinct.
        return isinstance(lhs, bool) and isinstance(rhs, bool) and lhs == rhs

    def _numeric_eq(lhs, rhs):
        if isinstance(lhs, bool) or isinstance(rhs, bool):
            return False
        return lhs == rhs

    def _numeric_binop(op):
        def wrapped(lhs, rhs):
            if isinstance(lhs, bool) or isinstance(rhs, bool):
                raise TypeError("Bool values are not numbers")
            return op(lhs, rhs)

        return wrapped

    def _numeric_cmp(op):
        def wrapped(lhs, rhs):
            if isinstance(lhs, bool) or isinstance(rhs, bool):
                raise TypeError("Bool values are not ordered with numbers")
            return op(lhs, rhs)

        return wrapped

    def _strict_equal(lhs, rhs):
        if isinstance(lhs, bool) != isinstance(rhs, bool):
            return False
        return lhs == rhs

    def _contains(container, item):
        return any(_strict_equal(element, item) for element in container)

    numeric_comparisons = {
        "==": _numeric_eq,
        "<": _numeric_cmp(operator.lt),
        "<=": _numeric_cmp(operator.le),
        ">": _numeric_cmp(operator.gt),
        ">=": _numeric_cmp(operator.ge),
    }

    _install_operators(t_object, binary={"==": operator.eq})
    _install_operators(t_null, binary={"==": operator.eq})
    _install_operators(t_bool, binary={"==": _bool_eq})

    _install_operators(
        t_int,
        unary={"+": operator.pos, "-": operator.neg, "~": operator.inv},
        binary={
            "+": _numeric_binop(operator.add),
            "-": _numeric_binop(operator.sub),
            "*": _numeric_binop(operator.mul),
            "/": _numeric_binop(operator.truediv),
            "//": _numeric_binop(operator.floordiv),
            "%": _numeric_binop(operator.mod),
            "**": _numeric_binop(operator.pow),
            "<<": _numeric_binop(operator.lshift),
            ">>": _numeric_binop(operator.rshift),
            "&": _numeric_binop(operator.and_),
            "|": _numeric_binop(operator.or_),
            "^": _numeric_binop(operator.xor),
            **numeric_comparisons,
        },
    )
    _install_operators(
        t_float,
        unary={"+": operator.pos, "-": operator.neg},
        binary={
            "+": _numeric_binop(operator.add),
            "-": _numeric_binop(operator.sub),
            "*": _numeric_binop(operator.mul),
            "/": _numeric_binop(operator.truediv),
            "//": _numeric_binop(operator.floordiv),
            "%": _numeric_binop(operator.mod),
            "**": _numeric_binop(operator.pow),
            **numeric_comparisons,
        },
    )
    _install_operators(
        t_string,
        binary={
            "+": operator.add,
            "*": operator.mul,
            "%": operator.mod,
            "in": lambda text, part: part in text,
            **comparisons,
        },
    )
    for type_obj in (t_list, t_tuple):
        _install_operators(
            type_obj,
            binary={
                "+": operator.add,
                "*": operator.mul,
                "in": _contains,
                **comparisons,
            },
        )
    _install_operators(
        t_dict,
        binary={
            # Keys are wrapped OortObjects, so Python's dict lookup is already
            # Bool/Int-strict and stays O(1).
            "in": lambda mapping, key: key in mapping,
            **comparisons,
        },
    )
    _install_operators(
        t_set,
        binary={
            "&": operator.and_,
            "|": operator.or_,
            "^": operator.xor,
            "-": operator.sub,
            "in": _contains,
            **comparisons,
        },
    )


def wrap_value(value) -> OortObject:
    if isinstance(value, OortObject):
        return value
    if value is None:
        return OortNull.get_null_value()
    if isinstance(value, bool):
        return OortBool.get_bool_value(value)
    if isinstance(value, int):
        return OortInt(value)
    if isinstance(value, float):
        return OortFloat(value)
    if isinstance(value, str):
        return OortString(value)
    if isinstance(value, list):
        return OortList([wrap_value(item) for item in value])
    if isinstance(value, tuple):
        return OortTuple(tuple(wrap_value(item) for item in value))
    if isinstance(value, dict):
        return OortDict({wrap_value(key): wrap_value(item) for key, item in value.items()})
    if isinstance(value, (set, frozenset)):
        return OortSet({wrap_value(item) for item in value})
    if isinstance(value, range):
        return OortList([OortInt(item) for item in value])
    if isinstance(value, slice):
        return OortSlice(
            None if value.start is None else wrap_value(value.start),
            None if value.stop is None else wrap_value(value.stop),
            None if value.step is None else wrap_value(value.step),
        )
    raise TypeError(f"Unsupported type: {type(value)}")
