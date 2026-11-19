#! /usr/bin/env python

"""Select the semantic analyzer for a dialect.

The shared compiler knows only this factory; dialect policy lives in the
semantics layer (OP 0001 §5).
"""

from typing import Protocol

from ..ast import nodes
from ..diagnostics.error_handler import CompilerErrorHandler
from ..parser.dialect import DialectConfig
from ..source.input_info import InputInfo
from .core.checker import CoreTypeChecker
from .pass1 import Pass1Analyzer


class SemanticAnalyzer(Protocol):
    def parse(self, node: nodes.ASTNode) -> object: ...


class CoreAnalyzer:
    """Pass 1 plus the independent static checker for `oort-core`."""

    def __init__(
        self,
        error_handler: CompilerErrorHandler,
        input_info: InputInfo,
        dialect: DialectConfig,
    ):
        self.pass1: Pass1Analyzer = Pass1Analyzer(error_handler, input_info, dialect=dialect)
        self.checker = CoreTypeChecker(error_handler, input_info, dialect)

    def parse(self, node: nodes.ASTNode) -> object:
        start = self.pass1.error_handler.error_count
        self.pass1.parse(node)
        if self.pass1.error_handler.error_count > start:
            # Avoid cascades after name-resolution or unsupported-syntax errors.
            return None
        return self.checker.parse(node)


def create_semantic_analyzer(
    error_handler: CompilerErrorHandler,
    input_info: InputInfo,
    dialect: DialectConfig,
) -> SemanticAnalyzer:
    if dialect.features.type_checking:
        return CoreAnalyzer(error_handler, input_info, dialect)
    return Pass1Analyzer(error_handler, input_info, dialect=dialect)
