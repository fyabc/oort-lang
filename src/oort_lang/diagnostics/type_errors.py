#!/usr/bin/env python3

from .base import OortSyntaxError


class TypeCheckError(OortSyntaxError):
    """A compile-time static type error."""
