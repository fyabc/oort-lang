#! /usr/bin/env python

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("oort-lang")
except PackageNotFoundError:
    __version__ = "unknown"
