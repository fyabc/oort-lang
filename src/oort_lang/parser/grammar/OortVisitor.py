# Generated from Oort.g4 by ANTLR 4.13.1
from antlr4 import *
if "." in __name__:
    from .OortParser import OortParser
else:
    from OortParser import OortParser

# This class defines a complete generic visitor for a parse tree produced by OortParser.

class OortVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by OortParser#startRule.
    def visitStartRule(self, ctx:OortParser.StartRuleContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#statementList.
    def visitStatementList(self, ctx:OortParser.StatementListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#statement.
    def visitStatement(self, ctx:OortParser.StatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#compilerAttribute.
    def visitCompilerAttribute(self, ctx:OortParser.CompilerAttributeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#variableDecl.
    def visitVariableDecl(self, ctx:OortParser.VariableDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#declTarget.
    def visitDeclTarget(self, ctx:OortParser.DeclTargetContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#idWithType.
    def visitIdWithType(self, ctx:OortParser.IdWithTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#ModuleImportStmt.
    def visitModuleImportStmt(self, ctx:OortParser.ModuleImportStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#NameImportStmt.
    def visitNameImportStmt(self, ctx:OortParser.NameImportStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#importAliasEntry.
    def visitImportAliasEntry(self, ctx:OortParser.ImportAliasEntryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#assignStmt.
    def visitAssignStmt(self, ctx:OortParser.AssignStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#expressionList.
    def visitExpressionList(self, ctx:OortParser.ExpressionListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#OperatorExpr.
    def visitOperatorExpr(self, ctx:OortParser.OperatorExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#YieldExpr.
    def visitYieldExpr(self, ctx:OortParser.YieldExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#ReturnExpr.
    def visitReturnExpr(self, ctx:OortParser.ReturnExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#ContinueExpr.
    def visitContinueExpr(self, ctx:OortParser.ContinueExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#BreakExpr.
    def visitBreakExpr(self, ctx:OortParser.BreakExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#MacroBlockExpr.
    def visitMacroBlockExpr(self, ctx:OortParser.MacroBlockExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#flattenExprList.
    def visitFlattenExprList(self, ctx:OortParser.FlattenExprListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#EnumDefExpr.
    def visitEnumDefExpr(self, ctx:OortParser.EnumDefExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#WhileExpr.
    def visitWhileExpr(self, ctx:OortParser.WhileExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#IfExpr.
    def visitIfExpr(self, ctx:OortParser.IfExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#ParenthesisExpr.
    def visitParenthesisExpr(self, ctx:OortParser.ParenthesisExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#FuncDefExpr.
    def visitFuncDefExpr(self, ctx:OortParser.FuncDefExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#SubscriptExpr.
    def visitSubscriptExpr(self, ctx:OortParser.SubscriptExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#IdExpr.
    def visitIdExpr(self, ctx:OortParser.IdExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#MatchExprAtom.
    def visitMatchExprAtom(self, ctx:OortParser.MatchExprAtomContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#DotExpr.
    def visitDotExpr(self, ctx:OortParser.DotExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#MacroCallExpr.
    def visitMacroCallExpr(self, ctx:OortParser.MacroCallExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#ExplicitSuperExpr.
    def visitExplicitSuperExpr(self, ctx:OortParser.ExplicitSuperExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#BlockExpr.
    def visitBlockExpr(self, ctx:OortParser.BlockExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#ClassDefExpr.
    def visitClassDefExpr(self, ctx:OortParser.ClassDefExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#LambdaDefExpr.
    def visitLambdaDefExpr(self, ctx:OortParser.LambdaDefExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#FunctionCallExpr.
    def visitFunctionCallExpr(self, ctx:OortParser.FunctionCallExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#MacroDefExpr.
    def visitMacroDefExpr(self, ctx:OortParser.MacroDefExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#LiteralExpr.
    def visitLiteralExpr(self, ctx:OortParser.LiteralExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#ForExpr.
    def visitForExpr(self, ctx:OortParser.ForExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#ImplicitSuperExpr.
    def visitImplicitSuperExpr(self, ctx:OortParser.ImplicitSuperExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#dotAttribute.
    def visitDotAttribute(self, ctx:OortParser.DotAttributeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#subscriptArgumentList.
    def visitSubscriptArgumentList(self, ctx:OortParser.SubscriptArgumentListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#subscriptArgument.
    def visitSubscriptArgument(self, ctx:OortParser.SubscriptArgumentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#sliceLiteral.
    def visitSliceLiteral(self, ctx:OortParser.SliceLiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#classDef.
    def visitClassDef(self, ctx:OortParser.ClassDefContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#className.
    def visitClassName(self, ctx:OortParser.ClassNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#enumDecl.
    def visitEnumDecl(self, ctx:OortParser.EnumDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#enumConstructorList.
    def visitEnumConstructorList(self, ctx:OortParser.EnumConstructorListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#enumConstructor.
    def visitEnumConstructor(self, ctx:OortParser.EnumConstructorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#enumFieldList.
    def visitEnumFieldList(self, ctx:OortParser.EnumFieldListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#enumField.
    def visitEnumField(self, ctx:OortParser.EnumFieldContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#matchExpr.
    def visitMatchExpr(self, ctx:OortParser.MatchExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#matchArmList.
    def visitMatchArmList(self, ctx:OortParser.MatchArmListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#matchArm.
    def visitMatchArm(self, ctx:OortParser.MatchArmContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#ConstructorPattern.
    def visitConstructorPattern(self, ctx:OortParser.ConstructorPatternContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#NamePattern.
    def visitNamePattern(self, ctx:OortParser.NamePatternContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#patternList.
    def visitPatternList(self, ctx:OortParser.PatternListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#typeParameterDef.
    def visitTypeParameterDef(self, ctx:OortParser.TypeParameterDefContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#typeParameterList.
    def visitTypeParameterList(self, ctx:OortParser.TypeParameterListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#typeParameter.
    def visitTypeParameter(self, ctx:OortParser.TypeParameterContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#baseClassDef.
    def visitBaseClassDef(self, ctx:OortParser.BaseClassDefContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#metaClassDef.
    def visitMetaClassDef(self, ctx:OortParser.MetaClassDefContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#blockBody.
    def visitBlockBody(self, ctx:OortParser.BlockBodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#parameterList.
    def visitParameterList(self, ctx:OortParser.ParameterListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#DefaultParameter.
    def visitDefaultParameter(self, ctx:OortParser.DefaultParameterContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#VarPosParameter.
    def visitVarPosParameter(self, ctx:OortParser.VarPosParameterContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#VarKwParameter.
    def visitVarKwParameter(self, ctx:OortParser.VarKwParameterContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#BlockParameter.
    def visitBlockParameter(self, ctx:OortParser.BlockParameterContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#ParameterMarker.
    def visitParameterMarker(self, ctx:OortParser.ParameterMarkerContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#argumentList.
    def visitArgumentList(self, ctx:OortParser.ArgumentListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#argument.
    def visitArgument(self, ctx:OortParser.ArgumentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#functionDef.
    def visitFunctionDef(self, ctx:OortParser.FunctionDefContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#funcName.
    def visitFuncName(self, ctx:OortParser.FuncNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#parameterDef.
    def visitParameterDef(self, ctx:OortParser.ParameterDefContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#returnTypeDef.
    def visitReturnTypeDef(self, ctx:OortParser.ReturnTypeDefContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#lambdaDef.
    def visitLambdaDef(self, ctx:OortParser.LambdaDefContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#macroDef.
    def visitMacroDef(self, ctx:OortParser.MacroDefContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#macroName.
    def visitMacroName(self, ctx:OortParser.MacroNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#macroCallName.
    def visitMacroCallName(self, ctx:OortParser.MacroCallNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#ifStmt.
    def visitIfStmt(self, ctx:OortParser.IfStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#elseBody.
    def visitElseBody(self, ctx:OortParser.ElseBodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#forStmt.
    def visitForStmt(self, ctx:OortParser.ForStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#whileStmt.
    def visitWhileStmt(self, ctx:OortParser.WhileStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#condition.
    def visitCondition(self, ctx:OortParser.ConditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#literal.
    def visitLiteral(self, ctx:OortParser.LiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#integerLiteral.
    def visitIntegerLiteral(self, ctx:OortParser.IntegerLiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#stringLiteral.
    def visitStringLiteral(self, ctx:OortParser.StringLiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#listLiteral.
    def visitListLiteral(self, ctx:OortParser.ListLiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#tupleLiteral.
    def visitTupleLiteral(self, ctx:OortParser.TupleLiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#setLiteral.
    def visitSetLiteral(self, ctx:OortParser.SetLiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#dictLiteral.
    def visitDictLiteral(self, ctx:OortParser.DictLiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#dictKeyList.
    def visitDictKeyList(self, ctx:OortParser.DictKeyListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#dictKey.
    def visitDictKey(self, ctx:OortParser.DictKeyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#expressionCommaList.
    def visitExpressionCommaList(self, ctx:OortParser.ExpressionCommaListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#term.
    def visitTerm(self, ctx:OortParser.TermContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by OortParser#identifier.
    def visitIdentifier(self, ctx:OortParser.IdentifierContext):
        return self.visitChildren(ctx)



del OortParser
