#! /usr/bin/env python

"""Build AST from syntax tree."""

from typing import TYPE_CHECKING

from antlr4 import ParserRuleContext

from ..ast.nodes import *
from ..ast.nodes.declarations import TypeQualifierKind
from ..diagnostics import OortException, OortSyntaxError
from ..diagnostics.error_handler import CompilerErrorHandler
from ..diagnostics.syntax_errors import UnsupportedSyntax
from ..source.input_info import InputInfo
from ..source.source_position import SourcePosition
from .dialect import DEFAULT_DIALECT, DialectConfig
from .expressions import ExpressionParsingMixin
from .grammar.OortParser import OortParser
from .grammar.OortVisitor import OortVisitor
from .literals import parse_string_literal
from .names import anonymous_param_index
from .parameters import ParameterParsingMixin

if TYPE_CHECKING:
    from antlr4.tree.Tree import ParseTree


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


class ASTBuilder(ExpressionParsingMixin, ParameterParsingMixin, OortVisitor):
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
        self._p_items: list[ParseTree] = []
        self._p_pos = 0

    def parse(self, tree: ParserRuleContext) -> ASTNode | None:
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
        mutable = ctx.VAR() is not None
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
            module_path=parse_string_literal(ctx.STRING_LITERAL()),
            alias=id_ctx.getText() if id_ctx else None,
        )

    def visitNameImportStmt(self, ctx: OortParser.NameImportStmtContext) -> ImportFromStmt:
        names = {}
        for entry_ctx in ctx.importAliasEntry():
            src, dst = self.parseImportAliasEntry(entry_ctx)
            names[src] = dst
        return ImportFromStmt(
            ctx,
            module_path=parse_string_literal(ctx.STRING_LITERAL()),
            names=names,
        )

    def parseImportAliasEntry(
        self, ctx: OortParser.ImportAliasEntryContext
    ) -> tuple[str, str | None]:
        identifiers = ctx.identifier()
        src = identifiers[0].getText()
        dst = identifiers[1].getText() if len(identifiers) > 1 else None
        return src, dst

    def visitAssignStmt(self, ctx: OortParser.AssignStmtContext) -> Assignment:
        lhs_ctx = ctx.expressionList(0)
        rhs_ctx = ctx.expressionList(1)
        lhs_exprs = lhs_ctx.expression()
        rhs_exprs = rhs_ctx.expression()

        if len(lhs_exprs) == 1:
            lhs = self._parse_assign_target(lhs_exprs[0])
        else:
            lhs = TupleLiteral(lhs_ctx, [self._parse_assign_target(expr) for expr in lhs_exprs])

        if len(rhs_exprs) == 1:
            rhs = self.visit(rhs_exprs[0])
        else:
            rhs = TupleLiteral(rhs_ctx, [self.visit(expr) for expr in rhs_exprs])

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

    # visitClassDefExpr: pass
    # visitFuncDefExpr: pass
    # visitLambdaDefExpr: pass
    # visitMacroDefExpr: pass
    # visitIfExpr: pass
    # visitForExpr: pass
    # visitWhileExpr: pass

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

    # visitParameterMarker: pass

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
        return StringConstant(ctx, parse_string_literal(ctx))

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
