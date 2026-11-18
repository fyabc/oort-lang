#! /usr/bin/env python

"""Build AST from syntax tree."""

import ast
import re
import reprlib

from antlr4 import ParserRuleContext, Token
from antlr4.tree.Tree import ParseTree, TerminalNodeImpl

from ..ast.nodes import *
from ..ast.nodes.declarations import TypeQualifierKind
from ..exceptions import OortException, OortSyntaxError
from ..exceptions.syntax_errors import ParameterError, UnsupportedSyntax
from ..grammar.OortParser import OortParser
from ..grammar.OortVisitor import OortVisitor
from ..support.input_info import InputInfo
from ..support.source_position import SourcePosition
from .dialect import DEFAULT_DIALECT, DialectConfig
from .error_handler import CompilerErrorHandler
from .names import anonymous_param_index
from .operator_defs import Arity, Associativity

_STRING_PREFIX_RE = re.compile(r"^([A-Za-z]*)")


def _collect_anonymous_params(node: ASTNode, found: set[int]):
    """Collect `$n` uses in one lambda body, without entering nested scopes."""
    if isinstance(node, (FunctionDef, ClassDef)):
        return
    if isinstance(node, Name):
        index = anonymous_param_index(node.id)
        if index is not None:
            found.add(index)
    for _, child in node.named_children():
        if child is not None:
            _collect_anonymous_params(child, found)


def _parse_string_literal(ctx: ParserRuleContext | Token) -> str:
    """Parse a string literal.

    Only plain and raw string literals are supported for now. Formatted
    string literals are rejected explicitly instead of being evaluated by
    Python (which would execute arbitrary code at parse time).
    """
    text = ctx.getText()
    prefix = _STRING_PREFIX_RE.match(text).group(1).lower()
    position = (
        SourcePosition.from_context(ctx)
        if isinstance(ctx, ParserRuleContext)
        else SourcePosition.from_token(ctx)
    )
    if "f" in prefix:
        raise UnsupportedSyntax("Formatted string literals are not implemented yet.", position)
    # `ast.literal_eval` is safe: it only accepts Python literals.
    try:
        return ast.literal_eval(text)
    except (ValueError, SyntaxError) as e:
        raise UnsupportedSyntax(f"Invalid string literal: {e}", position) from e


class ASTBuilder(OortVisitor):
    def __init__(
        self,
        error_handler: CompilerErrorHandler,
        input_info: InputInfo,
        dialect: DialectConfig = DEFAULT_DIALECT,
    ):
        self.error_handler = error_handler
        self.input_info = input_info
        self.dialect = dialect

        # Pratt parser states.
        self._op_table = dialect.new_operator_table()
        self._p_items = []
        self._p_pos = 0

    def parse(self, tree: ParserRuleContext) -> ASTNode:
        try:
            return tree.accept(self)
        except OortException as e:
            # Convert recoverable builder errors into diagnostics instead of
            # aborting the whole compilation with a traceback.
            self.error_handler.add(e, self.input_info)
            return None
        except SyntaxError as e:
            self.error_handler.add(
                OortSyntaxError(str(e), SourcePosition.from_context(tree)), self.input_info
            )
            return None

    def visitStartRule(self, ctx: OortParser.StartRuleContext) -> ModuleNode:
        _, stmt_list = self._get_ctx_with_stmt_list(ctx)
        if isinstance(stmt_list, list):
            # Empty input: wrap in a block so the AST always has a body node.
            stmt_list = BlockExpr(ctx, stmt_list)
        return ModuleNode(ctx, stmt_list)

    def _get_ctx_with_stmt_list(self, ctx):
        """Get statment list with its content, handle empty case (set to outer ctx)."""
        stmt_ctx = ctx.statementList()
        if stmt_ctx is None:
            return ctx, []
        return stmt_ctx, self.visitStatementList(stmt_ctx)

    def visitStatementList(self, ctx: OortParser.StatementListContext) -> BlockExpr:
        node = BlockExpr(ctx)
        for expr_ctx in ctx.statement():
            node.statements.append(self.visit(expr_ctx))
        return node

    # visitStatement: pass

    def visitCompilerAttribute(self, ctx: OortParser.CompilerAttributeContext) -> CompilerAttribute:
        return CompilerAttribute(ctx)

    def visitVariableDecl(self, ctx: OortParser.VariableDeclContext):
        init_exprs = ctx.expressionList().expression()
        mutable = ctx.kind.type == OortParser.VAR
        decl_targets = self.parseDeclTarget(ctx.declTarget())

        if len(init_exprs) == 1:
            init_value = self.visit(init_exprs[0])
        else:
            init_value = TupleLiteral(
                ctx.expressionList(), [self.visit(expr) for expr in init_exprs]
            )

        return VarDecl(
            ctx,
            decl_targets,
            init_value,
            mutable=mutable,
        )

    def parseDeclTarget(self, ctx: OortParser.DeclTargetContext) -> list[SingleDeclTarget]:
        return [self.visitIdWithType(id_with_type) for id_with_type in ctx.idWithType()]

    def visitIdWithType(self, ctx: OortParser.IdWithTypeContext) -> SingleDeclTarget:
        type_expr = ctx.expression()
        return SingleDeclTarget(
            ctx,
            ctx.identifier().getText(),
            None if type_expr is None else self.visit(type_expr),
        )

    def visitModuleImportStmt(self, ctx: OortParser.ModuleImportStmtContext) -> ImportStmt:
        id_ctx = ctx.identifier()
        return ImportStmt(
            ctx,
            module_path=_parse_string_literal(ctx.STRING_LITERAL()),
            alias=id_ctx.getText() if id_ctx else None,
        )

    def visitNameImportStmt(self, ctx: OortParser.NameImportStmtContext) -> ImportFromStmt:
        names = {}
        for entry_ctx in ctx.importAliasEntry():
            src, dst = self.parseImportAliasEntry(entry_ctx)
            names[src] = dst
        return ImportFromStmt(
            ctx,
            module_path=_parse_string_literal(ctx.STRING_LITERAL()),
            names=names,
        )

    def parseImportAliasEntry(
        self, ctx: OortParser.ImportAliasEntryContext
    ) -> tuple[str, str | None]:
        src = ctx.src.getText()
        dst = ctx.dst.getText() if ctx.dst else None
        return src, dst

    def visitAssignStmt(self, ctx: OortParser.AssignStmtContext) -> Assignment:
        lhs_exprs = ctx.lhs.expression()
        rhs_exprs = ctx.rhs.expression()

        if len(lhs_exprs) == 1:
            lhs = self._parse_assign_target(lhs_exprs[0])
        else:
            lhs = TupleLiteral(ctx.lhs, [self._parse_assign_target(expr) for expr in lhs_exprs])

        if len(rhs_exprs) == 1:
            rhs = self.visit(rhs_exprs[0])
        else:
            rhs = TupleLiteral(ctx.rhs, [self.visit(expr) for expr in rhs_exprs])

        return Assignment(ctx, ctx.op, lhs=lhs, rhs=rhs)

    def _parse_assign_target(self, expr_ctx: OortParser.ExpressionContext) -> ASTNode:
        node = self.visit(expr_ctx)
        if isinstance(node, (Name, Attribute)):
            node.ctx = LValueContext.STORE
        return node

    # visitOperatorExpr: pass

    def visitYieldExpr(self, ctx: OortParser.YieldExprContext) -> YieldExpr:
        value_ctx = ctx.expression()
        return YieldExpr(ctx, None if value_ctx is None else self.visit(value_ctx))

    def visitReturnExpr(self, ctx: OortParser.ReturnExprContext) -> ReturnExpr:
        value_ctx = ctx.expression()
        return ReturnExpr(ctx, None if value_ctx is None else self.visit(value_ctx))

    def visitContinueExpr(self, ctx: OortParser.ContinueExprContext) -> ContinueExpr:
        return ContinueExpr(ctx)

    def visitBreakExpr(self, ctx: OortParser.BreakExprContext) -> BreakExpr:
        value_ctx = ctx.expression()
        return BreakExpr(ctx, None if value_ctx is None else self.visit(value_ctx))

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

            # atomExpr (unexpected)
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

            op_name = item.getText()
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

                        # Missing rhs, set to None.
                        rhs = None
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

    # visitClassDefExpr: pass
    # visitFuncDefExpr: pass
    # visitLambdaDefExpr: pass
    # visitMacroDefExpr: pass
    # visitIfExpr: pass
    # visitForExpr: pass
    # visitWhileExpr: pass

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

    # visitSubscriptArgumentList: pass

    def visitSliceLiteral(self, ctx: OortParser.SliceLiteralContext) -> SliceLiteral:
        return SliceLiteral(
            ctx,
            None if ctx.lower is None else self.visit(ctx.lower),
            None if ctx.upper is None else self.visit(ctx.upper),
            None if ctx.stride is None else self.visit(ctx.stride),
        )

    def visitClassDef(self, ctx: OortParser.ClassDefContext) -> ClassDef:
        class_name_ctx = ctx.className()
        names = self.parseClassName(class_name_ctx)
        type_param_def_ctx = ctx.typeParameterDef()
        type_params = self.parseTypeParameterList(
            None if type_param_def_ctx is None else type_param_def_ctx.typeParameterList()
        )
        bases = self.parseBaseClassDef(ctx.baseClassDef())
        meta = self.visitMetaClassDef(ctx.metaClassDef())

        if class_name_ctx is None:
            name_position = SourcePosition.from_token(ctx.CLASS())
        else:
            name_position = SourcePosition.from_context(class_name_ctx)

        return ClassDef(
            ctx,
            names,
            type_params,
            bases=bases,
            meta=meta,
            body=self.visitBlockBody(ctx.blockBody()),
            name_position=name_position,
        )

    def parseClassName(self, ctx: OortParser.ClassNameContext) -> list[str]:
        if ctx is None:
            return []
        return [cls_name.getText() for cls_name in ctx.identifier()]

    # visitTypeParameterDef: pass

    def parseTypeParameterList(
        self, ctx: OortParser.TypeParameterListContext | None
    ) -> list[TypeParameter]:
        if ctx is None:
            return []
        return [self.visitTypeParameter(type_param_ctx) for type_param_ctx in ctx.typeParameter()]

    def visitTypeParameter(self, ctx: OortParser.TypeParameterContext) -> TypeParameter:
        if ctx.qualifier is None:
            qualifier = TypeQualifierKind.DEFAULT
        elif ctx.qualifier.text == "<":
            qualifier = TypeQualifierKind.UPPER_BOUND
        elif ctx.qualifier.text == ">":
            qualifier = TypeQualifierKind.LOWER_BOUND
        elif ctx.qualifier.text == ":":
            qualifier = TypeQualifierKind.META_TYPE
        else:
            raise ValueError(f"Unknown type qualifier: {ctx.qualifier.text}")
        return TypeParameter(
            ctx,
            name=ctx.identifier().getText(),
            type_expr=None if ctx.typeExpr is None else self.visit(ctx.typeExpr),
            qualifier=qualifier,
            default_value=None if ctx.defaultValue is None else self.visit(ctx.defaultValue),
        )

    # visitBaseClassDef: pass

    def parseBaseClassDef(self, ctx: OortParser.BaseClassDefContext) -> list[Expression]:
        if ctx is None:
            return []
        return [self.visit(base_ctx) for base_ctx in ctx.expression()]

    def visitMetaClassDef(self, ctx: OortParser.MetaClassDefContext) -> Expression | None:
        if ctx is None:
            return None
        return self.visit(ctx.expression())

    def visitBlockBody(self, ctx: OortParser.BlockBodyContext) -> BlockExpr:
        single_expr = ctx.expression()
        if single_expr is not None:
            return BlockExpr(ctx, [self.visit(single_expr)])
        stmt_ctx, stmt_list = self._get_ctx_with_stmt_list(ctx)
        return BlockExpr(stmt_ctx, stmt_list)

    def parseParameterList(
        self, ctx: OortParser.ParameterListContext | list[OortParser.ParameterContext] | None
    ) -> list[Parameter]:
        if ctx is None:
            return []
        if isinstance(ctx, list):
            params_ctx = ctx
        else:
            params_ctx = ctx.parameter()

        pos_only_flag = False
        kw_only_flag = False
        pos_only_idx: int | None = None
        kw_only_idx: int | None = None
        var_kw_idx: int | None = None
        block_idx: int | None = None
        bare_star_idx: int | None = None
        bare_star_ctx = None

        def _make_error(msg: str, param_ctx: OortParser.ParameterContext):
            self.error_handler.add(
                ParameterError(msg, SourcePosition.from_context(param_ctx)),
                self.input_info,
            )

        params = []
        related_params_ctx = []
        for param_ctx in params_ctx:
            # Process markers.
            if isinstance(param_ctx, OortParser.ParameterMarkerContext):
                marker = param_ctx.marker
                if marker.type == OortParser.DIV:
                    if pos_only_flag:
                        _make_error("Positional-only parameter flag redefinition", param_ctx)
                    if not params:
                        _make_error(
                            "Positional-only parameter flag must follow at least one parameter",
                            param_ctx,
                        )
                    if kw_only_flag or var_kw_idx is not None or block_idx is not None:
                        _make_error(
                            "Positional-only parameter flag must come before keyword-only "
                            "and variadic parameters",
                            param_ctx,
                        )
                    pos_only_flag = True
                    pos_only_idx = len(params)
                    continue
                elif marker.type == OortParser.MUL:
                    if kw_only_flag:
                        _make_error("Keyword-only parameter flag redefinition", param_ctx)
                    if var_kw_idx is not None or block_idx is not None:
                        _make_error(
                            "Keyword-only parameter flag must come before variadic parameters",
                            param_ctx,
                        )
                    kw_only_flag = True
                    kw_only_idx = len(params)
                    bare_star_idx = len(params)
                    bare_star_ctx = param_ctx
                    continue
                else:
                    raise RuntimeError(f"Unknown marker type {marker.type}")

            param = self.visit(param_ctx)
            assert isinstance(param, Parameter)

            kind = param.kind
            if kind == ParameterKind.VAR_POS:
                if kw_only_flag:
                    _make_error("Keyword-only parameter flag redefinition", param_ctx)
                if var_kw_idx is not None or block_idx is not None:
                    _make_error(
                        "Variadic positional parameter must come before other variadic parameters",
                        param_ctx,
                    )
                kw_only_flag = True
                kw_only_idx = len(params)
            elif kind == ParameterKind.VAR_KW:
                if var_kw_idx is not None:
                    _make_error("Variadic keyword parameter redefinition", param_ctx)
                var_kw_idx = len(params)
            elif kind == ParameterKind.BLOCK:
                if block_idx is not None:
                    _make_error("Trailing-block parameter redefinition", param_ctx)
                block_idx = len(params)
            else:
                pass

            params.append(param)
            related_params_ctx.append(param_ctx)

        n_params = len(params)
        if block_idx is not None and block_idx != n_params - 1:
            _make_error(
                "Trailing block parameter must be the last parameter", related_params_ctx[block_idx]
            )

        if var_kw_idx is not None:
            expected_idx = n_params - 2 if block_idx is not None else n_params - 1
            if var_kw_idx != expected_idx:
                _make_error(
                    "Variadic keyword parameter must come after all other parameters "
                    "(except a trailing block parameter)",
                    related_params_ctx[var_kw_idx],
                )

        # Set parameter kinds.
        if pos_only_idx is not None:
            for idx in range(pos_only_idx):
                param = params[idx]
                if param.kind == ParameterKind.DEFAULT:
                    param.kind = ParameterKind.POS_ONLY
        if kw_only_idx is not None:
            for idx in range(kw_only_idx, len(params)):
                param = params[idx]
                if param.kind == ParameterKind.DEFAULT:
                    param.kind = ParameterKind.KW_ONLY

        if bare_star_idx is not None:
            has_keyword_only = any(
                param.kind == ParameterKind.KW_ONLY for param in params[bare_star_idx:]
            )
            if not has_keyword_only:
                _make_error(
                    "Bare '*' must be followed by at least one keyword-only parameter",
                    bare_star_ctx,
                )

        seen_default = False
        seen_names: set[str] = set()
        for idx, param in enumerate(params):
            if param.name in seen_names:
                _make_error(f"Duplicate parameter name {param.name!r}", related_params_ctx[idx])
            seen_names.add(param.name)

            if param.kind in (ParameterKind.POS_ONLY, ParameterKind.DEFAULT):
                if param.default_value is not None:
                    seen_default = True
                elif seen_default:
                    _make_error(
                        "Parameter without a default follows parameter with a default",
                        related_params_ctx[idx],
                    )

        return params

    def _visit_parameter(self, ctx, kind: ParameterKind) -> Parameter:
        default_value_ctx = getattr(ctx, "defaultValue", None)
        return Parameter(
            ctx,
            name=ctx.identifier().getText(),
            type_expr=None if ctx.typeExpr is None else self.visit(ctx.typeExpr),
            kind=kind,
            default_value=None if default_value_ctx is None else self.visit(default_value_ctx),
        )

    def visitDefaultParameter(self, ctx: OortParser.DefaultParameterContext) -> Parameter:
        return self._visit_parameter(ctx, ParameterKind.DEFAULT)

    def visitVarPosParameter(self, ctx: OortParser.VarPosParameterContext) -> Parameter:
        return self._visit_parameter(ctx, ParameterKind.VAR_POS)

    def visitVarKwParameter(self, ctx: OortParser.VarKwParameterContext) -> Parameter:
        return self._visit_parameter(ctx, ParameterKind.VAR_KW)

    def visitBlockParameter(self, ctx: OortParser.BlockParameterContext) -> Parameter:
        return self._visit_parameter(ctx, ParameterKind.BLOCK)

    # visitParameterMarker: pass

    def parseArgumentList(self, ctx: OortParser.ArgumentListContext) -> list[Argument]:
        if ctx is None:
            return []
        return [self.visitArgument(arg_ctx) for arg_ctx in ctx.argument()]

    def visitArgument(self, ctx: OortParser.ArgumentContext) -> Argument:
        keyword = None if ctx.identifier() is None else ctx.identifier().getText()
        return Argument(
            ctx,
            value=self.visit(ctx.expression()),
            kind=ArgumentKind.DEFAULT if keyword is None else ArgumentKind.KEYWORD,
            keyword=keyword,
        )

    def visitFunctionDef(self, ctx: OortParser.FunctionDefContext) -> FunctionDef:
        func_name_ctx = ctx.funcName()
        names = self.parseFuncName(func_name_ctx)
        type_param_def_ctx = ctx.typeParameterDef()
        if type_param_def_ctx is not None:
            type_params = self.parseTypeParameterList(type_param_def_ctx.typeParameterList())
        else:
            type_params = []
        params = self.parseParameterDef(ctx.parameterDef())
        ret_type = (
            None if ctx.returnTypeDef() is None else self.visitReturnTypeDef(ctx.returnTypeDef())
        )
        body = self.visitBlockBody(ctx.blockBody())

        return FunctionDef(
            ctx,
            names,
            type_params,
            params,
            ret_type,
            body,
            name_position=SourcePosition.from_context(func_name_ctx),
            has_explicit_param_list=ctx.parameterDef() is not None,
        )

    def parseFuncName(self, ctx: OortParser.FuncNameContext) -> list[str]:
        names = []
        if ctx.CLASS() is not None:
            names.append("class")
        names.extend(id_ctx.getText() for id_ctx in ctx.identifier())

        str_ctx = ctx.stringLiteral()
        if str_ctx is not None:
            # TODO: Map operator to method names.
            names.append("operator " + _parse_string_literal(str_ctx))

        return names

    def parseParameterDef(self, ctx: OortParser.ParameterDefContext) -> list[Parameter]:
        if ctx is None:
            return []
        return self.parseParameterList(ctx.parameterList())

    def visitReturnTypeDef(self, ctx: OortParser.ReturnTypeDefContext) -> ASTNode:
        return self.visit(ctx.expression())

    def visitLambdaDef(self, ctx: OortParser.LambdaDefContext) -> FunctionDef:
        type_param_def_ctx = ctx.typeParameterDef()
        if type_param_def_ctx is not None:
            type_params = self.parseTypeParameterList(type_param_def_ctx.typeParameterList())
        else:
            type_params = []
        params = self.parseParameterDef(ctx.parameterDef())
        ret_type = (
            None if ctx.returnTypeDef() is None else self.visitReturnTypeDef(ctx.returnTypeDef())
        )
        body = self.visitBlockBody(ctx.blockBody())
        has_explicit_param_list = ctx.parameterDef() is not None

        anonymous_count = 0
        if not has_explicit_param_list:
            found: set[int] = set()
            _collect_anonymous_params(body, found)
            if found:
                anonymous_count = max(found) + 1

        return FunctionDef(
            ctx,
            [],
            type_params,
            params,
            ret_type,
            body,
            name_position=SourcePosition.from_token(ctx.DO()),
            anonymous_count=anonymous_count,
            has_explicit_param_list=has_explicit_param_list,
        )

    def visitMacroDef(self, ctx: OortParser.MacroDefContext) -> MacroDef:
        return MacroDef(
            ctx,
            self.parseMacroName(ctx.macroName()),
            self.parseParameterDef(ctx.parameterDef()),
            self.visitBlockBody(ctx.blockBody()),
        )

    def parseMacroName(self, ctx: OortParser.MacroNameContext) -> str:
        return ctx.identifier().getText()

    def parseMacroCallName(self, ctx: OortParser.MacroCallNameContext) -> str:
        return ctx.identifier().getText()

    def visitIfStmt(self, ctx: OortParser.IfStmtContext) -> IfExpr:
        conditions = ctx.condition()
        bodies = ctx.blockBody()
        else_block = None if ctx.elseBlock is None else self.visit(ctx.elseBlock)

        # Build `elif` branches as nested `if` expressions from the last one
        # backwards, so the resulting AST is a plain if/else chain.
        for i in range(len(conditions) - 1, 0, -1):
            nested = IfExpr(
                bodies[i],
                self.visit(conditions[i]),
                self.visitBlockBody(bodies[i]),
                else_block,
            )
            else_block = BlockExpr(bodies[i], [nested])

        return IfExpr(
            ctx,
            self.visit(conditions[0]),
            self.visitBlockBody(bodies[0]),
            else_block,
        )

    def visitElseBody(self, ctx: OortParser.ElseBodyContext) -> BlockExpr:
        single_expr = ctx.expression()
        if single_expr is not None:
            return BlockExpr(ctx, [self.visit(single_expr)])
        _, stmt_list = self._get_ctx_with_stmt_list(ctx)
        return BlockExpr(ctx, stmt_list)

    def visitForStmt(self, ctx: OortParser.ForStmtContext) -> ForExpr:
        return ForExpr(
            ctx,
            self.parseDeclTarget(ctx.declTarget()),
            self.visit(ctx.expression()),
            self.visitBlockBody(ctx.blockBody()),
        )

    def visitWhileStmt(self, ctx: OortParser.WhileStmtContext) -> WhileExpr:
        return WhileExpr(
            ctx,
            self.visit(ctx.condition()),
            self.visitBlockBody(ctx.blockBody()),
        )

    # visitCondition: pass

    def visitParenthesisExpr(self, ctx: OortParser.ParenthesisExprContext) -> ASTNode:
        return self.visit(ctx.expression())

    # visitLiteralExpr: pass

    def visitIdExpr(self, ctx: OortParser.IdExprContext) -> Name:
        return Name(ctx, ctx.getText())

    def visitExplicitSuperExpr(self, ctx: OortParser.ExplicitSuperExprContext) -> Call:
        raise UnsupportedSyntax(
            "Explicit super(...) calls are not supported; use super.__init__(...) "
            "or super.method(...).",
            SourcePosition.from_context(ctx),
        )

    def visitImplicitSuperExpr(self, ctx: OortParser.ImplicitSuperExprContext) -> ImplicitSuperExpr:
        return ImplicitSuperExpr(ctx)

    def visitLiteral(self, ctx: OortParser.LiteralContext) -> Literal:
        float_ctx = ctx.FLOAT_LITERAL()
        if float_ctx is not None:
            # literal text must be valid here (ensure by lexer grammar)
            return FloatConstant(ctx, float(float_ctx.getText()))
        if ctx.TRUE() is not None:
            return BooleanConstant(ctx, True)
        if ctx.FALSE() is not None:
            return BooleanConstant(ctx, False)
        if ctx.NULL() is not None:
            return NullConstant(ctx)
        if ctx.ELLIPSIS() is not None:
            return EllipsisConstant(ctx)
        return super().visitLiteral(ctx)

    def visitIntegerLiteral(self, ctx: OortParser.IntegerLiteralContext) -> IntConstant:
        text = ctx.getText()

        if ctx.DEC_INT() is not None and (text.startswith(("0d", "0D"))):
            text = text[2:]

        value = int(text, base=0)
        return IntConstant(ctx, value)

    def visitStringLiteral(self, ctx: OortParser.StringLiteralContext) -> StringConstant:
        return StringConstant(ctx, _parse_string_literal(ctx))

    def visitListLiteral(self, ctx: OortParser.ListLiteralContext) -> ListLiteral:
        return ListLiteral(
            ctx,
            self.parseExpressionCommaList(ctx.expressionCommaList()),
        )

    def visitTupleLiteral(self, ctx: OortParser.TupleLiteralContext) -> TupleLiteral:
        return TupleLiteral(
            ctx,
            [self.visit(element) for element in ctx.expression()],
        )

    def visitSetLiteral(self, ctx: OortParser.SetLiteralContext) -> SetLiteral:
        return SetLiteral(
            ctx,
            self.parseExpressionCommaList(ctx.expressionCommaList()),
        )

    def visitDictLiteral(self, ctx: OortParser.DictLiteralContext) -> DictLiteral:
        return DictLiteral(
            ctx,
            self.parseDictKeyList(ctx.dictKeyList()),
        )

    def parseDictKeyList(
        self, ctx: OortParser.DictKeyListContext
    ) -> list[tuple[ASTNode | None, ASTNode]]:
        if ctx is None:
            return []
        return [self.parseDictKey(dict_key) for dict_key in ctx.dictKey()]

    def parseDictKey(self, ctx: OortParser.DictKeyContext) -> tuple[ASTNode | None, ASTNode]:
        if ctx.EXP() is None:
            return self.visit(ctx.expression(0)), self.visit(ctx.expression(1))
        return None, self.visit(ctx.expression(0))

    def parseExpressionCommaList(self, ctx: OortParser.ExpressionCommaListContext) -> list[ASTNode]:
        if ctx is None:
            return []
        return [self.visit(expr) for expr in ctx.expression()]

    # visitTerm: pass
    # visitIdentifier: pass
