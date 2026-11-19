#! /usr/bin/env python

from .base import OortException


class OortRuntimeError(OortException):
    """Oort runtime error."""


class OortNameError(OortRuntimeError):
    pass


class OortTypeError(OortRuntimeError):
    pass


class OortAttributeError(OortRuntimeError):
    pass


class OortImportError(OortRuntimeError):
    """Module resolution, loading or import-binding failure."""
