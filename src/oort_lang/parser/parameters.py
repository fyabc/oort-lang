#! /usr/bin/env python

"""Parameter lists, argument lists and lambda parameters."""

from antlr4 import ParserRuleContext

from ..ast.nodes import *
from ..ast.nodes.declarations import ParameterKind
from ..diagnostics.syntax_errors import ParameterError
from ..source.source_position import SourcePosition
from .grammar.OortParser import OortParser
from .grammar.OortVisitor import OortVisitor
from .literals import parse_string_literal


class ParameterParsingMixin(OortVisitor):
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
        bare_star_ctx: ParserRuleContext | None = None

        def _make_error(msg: str, param_ctx: ParserRuleContext):
            self.error_handler.add(
                ParameterError(msg, SourcePosition.from_context(param_ctx)),
                self.input_info,
            )

        params: list[Parameter] = []
        related_params_ctx: list[ParserRuleContext] = []
        for param_ctx in params_ctx:
            # Process markers.
            if isinstance(param_ctx, OortParser.ParameterMarkerContext):
                if param_ctx.DIV() is not None:
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
                elif param_ctx.MUL() is not None:
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
                    raise RuntimeError(f"Unknown parameter marker: {param_ctx.getText()}")

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
                assert bare_star_ctx is not None
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

    def parseFuncName(self, ctx: OortParser.FuncNameContext) -> list[str]:
        names = []
        if ctx.CLASS() is not None:
            names.append("class")
        names.extend(id_ctx.getText() for id_ctx in ctx.identifier())

        str_ctx = ctx.stringLiteral()
        if str_ctx is not None:
            # TODO: Map operator to method names.
            names.append("operator " + parse_string_literal(str_ctx))

        return names

    def parseParameterDef(self, ctx: OortParser.ParameterDefContext) -> list[Parameter]:
        if ctx is None:
            return []
        return self.parseParameterList(ctx.parameterList())

    def visitReturnTypeDef(self, ctx: OortParser.ReturnTypeDefContext) -> ASTNode:
        return self.visit(ctx.expression())
