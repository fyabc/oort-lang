#! /usr/bin/env python

import dataclasses
import logging
from enum import Enum
from typing import Optional

from .objects import OortObject

GLOBAL_ENV_NAME = "<global>"


@dataclasses.dataclass
class Entry:
    value: OortObject
    mutable: bool = True


class DefineResult(Enum):
    OK = 1
    REDEFINED = 2


class AssignResult(Enum):
    OK = 1
    NOT_FOUND = 2
    IMMUTABLE = 3


class Environment:
    """Oort environment in AST interpreter."""

    def __init__(self, outer: Optional["Environment"] = None, name: str = GLOBAL_ENV_NAME):
        self.values: dict[str, Entry] = {}
        self.outer: Environment | None = outer
        self.name = name

    def _ancestor(self, depth: int) -> "Environment":
        env: Environment | None = self
        for _ in range(depth):
            assert env is not None
            env = env.outer
        assert env is not None
        return env

    def get(self, name: str) -> Entry | None:
        """Search name from current env and outer env."""
        value = self.values.get(name, None)
        if value is None and self.outer is not None:
            value = self.outer.get(name)
        else:
            logging.debug(f"Get {name!r} from {self.name}.")
        return value

    def get_at(self, name: str, depth: int) -> Entry | None:
        env = self._ancestor(depth)
        logging.debug(f"Get {name!r} from {env.name} (depth = {depth}).")
        return env.values.get(name, None)

    def define(self, name: str, value: OortObject, mutable: bool = False) -> DefineResult:
        """Define a new name to value."""
        if name in self.values and self.name != GLOBAL_ENV_NAME:
            # Only allow redefinition in global env.
            return DefineResult.REDEFINED
        mut_s = "(mut) " if mutable else ""
        logging.debug(f"Define {name!r} to {mut_s}{value}.")
        self.values[name] = Entry(value, mutable)
        return DefineResult.OK

    def assign(self, name: str, value: OortObject) -> AssignResult:
        """Assign a value to a name."""
        env: Environment | None = self
        while env is not None and name not in env.values:
            env = env.outer
        if env is None:
            return AssignResult.NOT_FOUND
        entry = env.values[name]
        if not entry.mutable:
            return AssignResult.IMMUTABLE
        entry.value = value
        return AssignResult.OK

    def assign_at(self, name: str, value: OortObject, depth: int) -> AssignResult:
        env = self._ancestor(depth)
        if name not in env.values:
            return AssignResult.NOT_FOUND
        entry = env.values[name]
        if not entry.mutable:
            return AssignResult.IMMUTABLE
        entry.value = value
        return AssignResult.OK

    def pprint(self):
        """Pretty print current environment."""
        env_chain = []
        env: Environment | None = self
        while env is not None:
            env_chain.append(env)
            env = env.outer
        for env in reversed(env_chain):
            print(f"{env.name}:")
            for name, entry in env.values.items():
                mut_s = "(mut) " if entry.mutable else ""
                print(f"  {name!r}: {mut_s}{entry.value}")
