#! /usr/bin/env python

"""Value objects of the tree-walking interpreter."""

from typing import TYPE_CHECKING

from .context import get_runtime

if TYPE_CHECKING:
    from .environment import Environment
    from .type_system import OortType

__all__ = [
    "OortBool",
    "OortDict",
    "OortFloat",
    "OortInstance",
    "OortInt",
    "OortList",
    "OortModule",
    "OortNativeMixin",
    "OortNull",
    "OortObject",
    "OortSet",
    "OortSlice",
    "OortString",
    "OortSuperProxy",
    "OortTuple",
    "wrap_value",
]


class OortObject:
    """Base class of all Oort objects in AST-interpreter."""

    def __init__(self, type_: "OortType"):
        self.type = type_

    def __repr__(self):
        return f"<{self.type.name} object at {hex(id(self))}>"

    @property
    def host_value(self):
        """Project to the Python host value."""
        return self

    @property
    def is_native(self) -> bool:
        return False

    @classmethod
    def get_type_object(cls) -> "OortType":
        """Get the type object of this class in the active runtime."""
        return get_runtime().types.for_class(cls)

    def get(self, name: str) -> "OortObject | None":
        # Imported lazily: dispatch and functions depend on this value module.
        from .dispatch import _get_from_cls
        from .functions import OortNativeFunction, OortNativeMethod
        from .type_system import OortType

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

    def __getitem__(self, item: "OortObject") -> "OortObject":
        raise TypeError(f"{self.type.name!r} object is not subscriptable")

    def __setitem__(self, key: "OortObject", value: "OortObject"):
        raise TypeError(f"{self.type.name!r} object does not support item assignment")


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


class OortModule(OortNativeMixin, OortObject):
    """A loaded Oort module: a live, read-only view of its global environment."""

    def __init__(self, name: str, env: "Environment"):
        super().__init__(type_=self.get_type_object())
        self.module_name = name
        self.env = env

    def __repr__(self):
        return f"<module {self.module_name!r}>"

    def get(self, name: str) -> "OortObject | None":
        entry = self.env.values.get(name)
        return None if entry is None else entry.value

    def has(self, name: str) -> bool:
        return name in self.env.values


class OortSuperProxy(OortNativeMixin, OortObject):
    """Oort super proxy object."""

    def __init__(self, cls: "OortType", receiver: OortObject):
        from .type_system import OortType

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
        from .dispatch import _get_from_cls

        # Search from super classes.
        mro = self.receiver.type.mro()
        start_idx = mro.index(self.cls) + 1
        if start_idx >= len(mro):
            return None
        start_type = mro[start_idx]

        value = _get_from_cls(name=name, start_type=start_type, receiver=self.receiver)
        if value is not None:
            return value

        # TODO: missing fallback.

        return None


class OortNull(OortNativeMixin, OortObject):
    """Oort null object."""

    def __init__(self):
        super().__init__(type_=self.get_type_object())

    @classmethod
    def get_null_value(cls):
        """Get the null value of the active runtime."""
        return get_runtime().null

    def __repr__(self):
        return "null"

    def __str__(self):
        return "null"

    @property
    def host_value(self):
        """Project to the Python host value."""
        return None


class OortBool(OortNativeMixin, OortObject):
    """Oort boolean object."""

    def __init__(self, value: bool):
        super().__init__(type_=self.get_type_object())
        self.value = value

    @classmethod
    def get_true_value(cls):
        """Get the true value of the active runtime."""
        return get_runtime().true

    @classmethod
    def get_false_value(cls):
        """Get the false value of the active runtime."""
        return get_runtime().false

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
    def host_value(self):
        """Project to the Python host value."""
        return self.value


class OortInt(OortNativeMixin, OortObject):
    """Oort integer object."""

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
    def host_value(self):
        """Project to the Python host value."""
        return self.value


class OortFloat(OortNativeMixin, OortObject):
    """Oort float object."""

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
    def host_value(self):
        """Project to the Python host value."""
        return self.value


class OortString(OortNativeMixin, OortObject):
    """Oort string object."""

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
        index = item.host_value
        result = self.value[index]
        if isinstance(index, slice):
            return OortString(result)
        return OortString(result)

    def __len__(self):
        return len(self.value)

    def __iter__(self):
        return (OortString(char) for char in self.value)

    @property
    def host_value(self):
        """Project to the Python host value."""
        return self.value


class OortList(OortObject):
    """Oort list object."""

    def __init__(self, value: list[OortObject]):
        super().__init__(type_=self.get_type_object())
        self.value = value

    def __getitem__(self, item: "OortObject"):
        index = item.host_value
        result = self.value[index]
        if isinstance(index, slice):
            return OortList(result)
        return result

    def __setitem__(self, key: "OortObject", value: "OortObject"):
        self.value[key.host_value] = value

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
    def host_value(self):
        """Project to a Python list, preserving nested containers and aliases."""
        return _project_host_value(self, {}, set())


class OortTuple(OortObject):
    """Oort tuple object (immutable)."""

    def __init__(self, value: tuple[OortObject, ...]):
        super().__init__(type_=self.get_type_object())
        self.value = value

    def __getitem__(self, item: "OortObject"):
        index = item.host_value
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
    def host_value(self):
        """Project to a Python tuple."""
        return _project_host_value(self, {}, set())


class OortDict(OortObject):
    """Oort dictionary object."""

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
    def host_value(self):
        """Project to a Python dict."""
        return _project_host_value(self, {}, set())


class OortSet(OortObject):
    """Oort set object."""

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
    def host_value(self):
        """Project to a Python set."""
        return _project_host_value(self, {}, set())


class OortSlice(OortObject):
    """Oort slice object, used as a subscript argument."""

    def __init__(self, start: OortObject | None, stop: OortObject | None, step: OortObject | None):
        super().__init__(type_=self.get_type_object())
        self.start = start
        self.stop = stop
        self.step = step

    @property
    def host_value(self):
        """Project to a Python slice."""
        return _project_host_value(self, {}, set())

    def __repr__(self):
        return f"slice({self.start}, {self.stop}, {self.step})"


def _project_host_value(value: "OortObject", memo: dict[int, object], active: set[int]) -> object:
    """Project one Oort value into the Python host representation.

    Containers are copied recursively. `memo` preserves aliasing and lets
    mutable List/Dict cycles become self-referential host containers. A tuple
    cannot be created empty and filled later, so a cycle through a tuple is
    rejected explicitly instead of recursing forever.
    """
    if isinstance(value, OortList):
        key = id(value)
        if key in memo:
            return memo[key]
        result: list[object] = []
        memo[key] = result
        result.extend(_project_host_value(item, memo, active) for item in value.value)
        return result

    if isinstance(value, OortTuple):
        key = id(value)
        if key in memo:
            return memo[key]
        if key in active:
            raise TypeError("Cannot convert a cyclic tuple to a host value")
        active.add(key)
        try:
            result_tuple = tuple(_project_host_value(item, memo, active) for item in value.value)
        finally:
            active.discard(key)
        memo[key] = result_tuple
        return result_tuple

    if isinstance(value, OortDict):
        key = id(value)
        if key in memo:
            return memo[key]
        result_dict: dict[object, object] = {}
        memo[key] = result_dict
        for item_key, item_value in value.value.items():
            result_dict[_project_host_value(item_key, memo, active)] = _project_host_value(
                item_value, memo, active
            )
        return result_dict

    if isinstance(value, OortSet):
        key = id(value)
        if key in memo:
            return memo[key]
        result_set: set[object] = set()
        memo[key] = result_set
        result_set.update(_project_host_value(item, memo, active) for item in value.value)
        return result_set

    if isinstance(value, OortSlice):
        return slice(
            None if value.start is None else _project_host_value(value.start, memo, active),
            None if value.stop is None else _project_host_value(value.stop, memo, active),
            None if value.step is None else _project_host_value(value.step, memo, active),
        )

    return value.host_value


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
