#! /usr/bin/env python

try:
    from importlib.metadata import PackageNotFoundError, version
except ImportError:  # Python < 3.8
    from importlib_metadata import PackageNotFoundError, version

try:
    __version__ = version("oort-lang")
except PackageNotFoundError:
    __version__ = "unknown"
