#! /usr/bin/env python


from antlr4 import ParserRuleContext

from ..ast_visitor import ASTVisitor
from .base import ASTNode


class ImportStmt(ASTNode):
    def __init__(
        self,
        context: ParserRuleContext,
        module_path: str,
        alias: str | None = None,
    ):
        super().__init__(context)
        self.module_path = module_path
        self.alias = alias

    def _accept(self, visitor: ASTVisitor):
        return visitor.visit_import_stmt(self)


class ImportFromStmt(ASTNode):
    def __init__(
        self,
        context: ParserRuleContext,
        module_path: str,
        names: dict[str, str | None],
    ):
        super().__init__(context)
        self.module_path = module_path
        self.names = {k: v for k, v in names.items()}

    def _accept(self, visitor: ASTVisitor):
        return visitor.visit_import_from_stmt(self)
