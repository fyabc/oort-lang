#! /usr/bin/env python

"""Pratt expression parsing."""

import reprlib
from typing import cast

from antlr4.tree.Tree import ParseTree, TerminalNodeImpl

from ..ast.nodes import *
from ..diagnostics import OortSyntaxError
from ..source.source_position import SourcePosition
from .grammar.OortParser import OortParser
from .grammar.OortVisitor import OortVisitor
from .operator_defs import Arity, Associativity


class ExpressionParsingMixin(OortVisitor):
    _p_items: list[ParseTree]
    _p_pos: int

    def visitFlattenExprList(self, ctx: OortParser.FlattenExprListContext) -> ASTNode:
        old_p_items = self._p_items
        old_p_pos = self._p_pos

        self._p_items = list(ctx.getChildren())
        self._p_pos = 0

        expr = self._parse_expr(0)
        if not self._p_at_end():
            item = self._p_peek()
            raise SyntaxError(f"Unexpected item '{item}'")

        self._p_items = old_p_items
        self._p_pos = old_p_pos

        return expr

    def _parse_expr(self, min_bp: int) -> ASTNode:
        lhs = self._parse_prefix()
        if lhs is None:
            item = self._p_peek()
            raise SyntaxError(f"Unexpected item '{item}' in prefix expression")

        last_non_assoc_prec: int | None = None

        while not self._p_at_end():
            item = self._p_peek()
            assert item is not None
            op_name = item.getText()
            if isinstance(item, OortParser.AtomExprContext) and not isinstance(
                item, OortParser.IdExprContext
            ):
                self.error_handler.add(
                    OortSyntaxError(
                        f"Expected operator or infix call here, but got {reprlib.repr(item.start.text)}",
                        position=SourcePosition.from_context(item),
                    ),
                    self.input_info,
                )
                # Visit and skip all remain items.
                for item in self._p_items[self._p_pos :]:
                    self.visit(item)
                self._p_pos = len(self._p_items)
                continue

            if isinstance(item, OortParser.IdExprContext):
                # Infix call (e.g. `a plus b`). Infix calls must be declared
                # explicitly; implicit infix is disabled until OP 0002.
                op_def = self._op_table.get(op_name, Arity.INFIX, default=False)
                if op_def is None:
                    self.error_handler.add(
                        OortSyntaxError(
                            f"Infix call {op_name!r} is not supported yet; "
                            f"use a method call or an explicit operator declaration.",
                            position=SourcePosition.from_context(item),
                        ),
                        self.input_info,
                    )
                    for remaining in self._p_items[self._p_pos :]:
                        self.visit(remaining)
                    self._p_pos = len(self._p_items)
                    break
                if op_def.precedence >= min_bp:
                    attr_node = Attribute(
                        SourcePosition(lhs.position.start, item.stop), lhs, op_name
                    )

                    self._p_advance()
                    if self._p_at_end():
                        symbol = item.identifier().symbol
                        self.error_handler.add(
                            OortSyntaxError(
                                f"Missing right operand of infix call {op_name!r}",
                                position=SourcePosition.from_token(symbol),
                            ),
                            self.input_info,
                        )

                        # Missing rhs, set to None.
                        args = []
                        position = SourcePosition(lhs.position.start, item.stop)
                    else:
                        if op_def.associativity == Associativity.NONE:
                            if last_non_assoc_prec == op_def.precedence:
                                self._report_chained_comparison(item)
                                last_non_assoc_prec = None
                            else:
                                last_non_assoc_prec = op_def.precedence
                        else:
                            last_non_assoc_prec = None
                        rhs = self._parse_expr(self._right_bp(op_def))
                        args = [Argument(rhs.position, rhs)]
                        position = SourcePosition(lhs.position.start, rhs.position.stop)
                    lhs = Call(position, attr_node, args, infix=True)
                    continue
            else:
                assert isinstance(item, TerminalNodeImpl)

                # [NOTE]: Oort language does NOT support prefix operator, or you can add processing here.
                # op_def = self._op_table.get(op_name, Arity.POSTFIX, default=True)
                # if op_def.precedence >= min_bp:
                #     self._p_advance()
                #     lhs = UnaryExpr(SourcePosition(lhs.position.start, item.symbol), op=item.symbol, operand=lhs)
                #     continue

                # Infix operator (e.g. `a + b`).
                op_def = self._op_table.get(op_name, Arity.INFIX, default=True)
                assert op_def is not None
                if op_def.precedence >= min_bp:
                    self._p_advance()
                    if self._p_at_end():
                        self.error_handler.add(
                            OortSyntaxError(
                                f"Missing right operand of infix operator {op_name!r}",
                                position=SourcePosition.from_token(item.symbol),
                            ),
                            self.input_info,
                        )

                        # Missing rhs. Diagnosis is recorded and compilation
                        # stops before evaluation, so a placeholder is enough.
                        rhs = cast("ASTNode", None)
                        position = SourcePosition(lhs.position.start, item.symbol)
                    else:
                        if op_def.associativity == Associativity.NONE:
                            if last_non_assoc_prec == op_def.precedence:
                                self._report_chained_comparison(item)
                                last_non_assoc_prec = None
                            else:
                                last_non_assoc_prec = op_def.precedence
                        else:
                            last_non_assoc_prec = None
                        rhs = self._parse_expr(self._right_bp(op_def))
                        position = SourcePosition(lhs.position.start, rhs.position.stop)
                    if op_name == "and":
                        lhs = AndExpr(position, op=item.symbol, lhs=lhs, rhs=rhs)
                    elif op_name == "or":
                        lhs = OrExpr(position, op=item.symbol, lhs=lhs, rhs=rhs)
                    else:
                        lhs = BinaryExpr(position, op=item.symbol, lhs=lhs, rhs=rhs)
                    continue

            break
        return lhs

    def _right_bp(self, op_def) -> int:
        """Right binding power for a binary operator."""
        if op_def.associativity == Associativity.RIGHT:
            return op_def.precedence
        return op_def.precedence + 1

    def _report_chained_comparison(self, item):
        """Report a chained non-associative comparison (e.g. `a < b < c`)."""
        position = (
            SourcePosition.from_token(item.symbol)
            if isinstance(item, TerminalNodeImpl)
            else SourcePosition.from_context(item)
        )
        self.error_handler.add(
            OortSyntaxError(
                "Comparison operators cannot be chained; use `and` to combine comparisons.",
                position,
            ),
            self.input_info,
        )

    def _parse_prefix(self) -> ASTNode | None:
        if self._p_at_end():
            return None

        item = self._p_advance()

        # atomExpr (e.g. `42`).
        if isinstance(item, OortParser.AtomExprContext):
            result = self.visit(item)
            return result

        # Prefix operator (e.g. `-a`).
        assert isinstance(item, TerminalNodeImpl)
        op_name = item.getText()
        op_def = self._op_table.get(op_name, Arity.PREFIX, default=True)
        assert op_def is not None

        # Parse operand, then create AST node.
        operand = self._parse_expr(op_def.precedence)
        position = SourcePosition(item.symbol, operand.position.stop)
        if op_name == "await":
            return AwaitExpr(position, operand)
        else:
            return UnaryExpr(
                SourcePosition(item.symbol, operand.position.stop), op=item.symbol, operand=operand
            )

    def _p_peek(self) -> ParseTree | None:
        if self._p_at_end():
            return None
        return self._p_items[self._p_pos]

    def _p_advance(self) -> ParseTree | None:
        item = self._p_peek()
        self._p_pos += 1
        return item

    def _p_at_end(self) -> bool:
        return self._p_pos >= len(self._p_items)

    def visitDotExpr(self, ctx: OortParser.DotExprContext) -> Attribute:
        attr_ctx = ctx.dotAttribute()
        return Attribute(
            ctx,
            self.visit(ctx.atomExpr()),
            self.parseDotAttribute(attr_ctx),
        )

    def visitSubscriptExpr(self, ctx: OortParser.SubscriptExprContext) -> Subscript:
        value = self.visit(ctx.atomExpr())
        arg_list_ctx = ctx.subscriptArgumentList()
        slice_args = self.parseSubscriptArgumentList(arg_list_ctx)
        if len(slice_args) == 1:
            slice_node = slice_args[0]
        else:
            slice_node = TupleLiteral(arg_list_ctx, slice_args)
        return Subscript(ctx, value, slice_node)

    def visitFunctionCallExpr(self, ctx: OortParser.FunctionCallExprContext) -> Call:
        func_node = self.visit(ctx.atomExpr())
        arg_list_nodes = []
        arg_list_ctx = ctx.argumentList()
        if arg_list_ctx is not None:
            for arg_ctx in arg_list_ctx.argument():
                arg_list_nodes.append(self.visitArgument(arg_ctx))

        trailing_block_ctx = ctx.lambdaDef()
        if trailing_block_ctx is not None:
            trailing_block_node = self.visit(trailing_block_ctx)
            trailing_block_arg = Argument(
                context=trailing_block_ctx,
                value=trailing_block_node,
                kind=ArgumentKind.BLOCK,
            )
            arg_list_nodes.append(trailing_block_arg)

        return Call(ctx, func_node, arg_list_nodes)

    def visitMacroCallExpr(self, ctx: OortParser.MacroCallExprContext) -> MacroCall:
        name = self.parseMacroCallName(ctx.macroCallName())
        arg_list_nodes = []
        arg_list_ctx = ctx.argumentList()
        if arg_list_ctx is not None:
            for arg_ctx in arg_list_ctx.argument():
                arg_list_nodes.append(self.visitArgument(arg_ctx))

        trailing_block_ctx = ctx.lambdaDef()
        if trailing_block_ctx is not None:
            trailing_block_node = self.visit(trailing_block_ctx)
            trailing_block_arg = Argument(
                context=trailing_block_ctx,
                value=trailing_block_node,
                kind=ArgumentKind.BLOCK,
            )
            arg_list_nodes.append(trailing_block_arg)
        return MacroCall(ctx, name, arg_list_nodes)

    def visitBlockExpr(self, ctx: OortParser.BlockExprContext) -> BlockExpr:
        stmt_list_ctx = ctx.statementList()
        if stmt_list_ctx is None:
            return BlockExpr(ctx, [])
        else:
            return BlockExpr(ctx, self.visitStatementList(stmt_list_ctx))

    def visitMacroBlockExpr(self, ctx: OortParser.MacroBlockExprContext) -> MacroCall:
        name = self.parseMacroCallName(ctx.macroCallName())
        arg_ctx = ctx.expression()
        argument = Argument(arg_ctx, value=self.visit(arg_ctx), kind=ArgumentKind.DEFAULT)
        return MacroCall(ctx, name, [argument])

    def parseDotAttribute(self, ctx: OortParser.DotAttributeContext) -> str:
        return ctx.getText()

    def parseSubscriptArgumentList(
        self, ctx: OortParser.SubscriptArgumentListContext
    ) -> list[ASTNode]:
        if ctx is None:
            return []
        return [self.visit(arg_ctx) for arg_ctx in ctx.subscriptArgument()]
