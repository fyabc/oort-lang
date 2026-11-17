#!/usr/bin/env python3

from .base import OortSyntaxError


class UnsupportedSyntax(OortSyntaxError):
    """未支持语言特性的默认错误类型"""


class ParameterError(OortSyntaxError):
    pass


class InvalidLiteral(OortSyntaxError):
    pass
