grammar Oort;

@lexer::members {
    self.parenthesisCount = 0
    self.bracketCount = 0
    self.dictLiteralCount = 0
    self.setLiteralCount = 0
    self.brackets = []
}

startRule
    : statementList? EOF;

statementList
    : term? statement (term statement)* term?
    | term
    ;

statement
    : compilerAttribute
    | variableDecl
    | importStmt
    | assignStmt
    | expression
    ;

/*
    Compiler attribute.
    TODO: Design syntax.
*/
compilerAttribute
    : AT_LBK RBK
    ;

/*
    Variable declaration.
    TODO: Support muliple variable declaration (`var a, b = Pair(4, 8), c = 10`)
*/
variableDecl
    : kind=(VAR | VAL) declTarget ASSIGN expressionList
    ;

// TODO: Support *-based iterable unpacking (from Python)
// TODO: Support object unpacking (from Scala)
declTarget
    : idWithType (COMMA idWithType)*
    ;

idWithType
    : identifier (COLON expression)?
    ;

/*
    Import statement.
*/
importStmt
    : IMPORT STRING_LITERAL (AS identifier)?                                        # ModuleImportStmt
    | FROM STRING_LITERAL IMPORT importAliasEntry (COMMA importAliasEntry)*         # NameImportStmt
    ;

importAliasEntry
    : src=identifier (AS dst=identifier)?
    ;

/*
    Assign statement.

    Both sides are expression lists so that tuple unpacking works:
        a, b = b, a
*/
assignStmt
    : lhs=expressionList op=(ASSIGN | AUG_ASSIGN) rhs=expressionList
    ;

expressionList
    : expression (COMMA expression)*
    ;

/*
    Expression.
*/
expression
    : flattenExprList                                                   # OperatorExpr
    | YIELD expression?                                                 # YieldExpr
    | RETURN expression?                                                # ReturnExpr
    | CONTINUE                                                          # ContinueExpr
    | BREAK expression?                                                 # BreakExpr
    | macroCallName expression                                          # MacroBlockExpr
    ;

/*
    Flattened expression list (use Pratt parser to generate correct AST).
*/
flattenExprList
    : (atomExpr
        | AWAIT
        | EXP
        | ADD | SUB | BIT_NOT
        | ARROW
        | MUL | DIV | FLOOR_DIV | MOD
        | LSHIFT | RSHIFT
        | BIT_AND | BIT_XOR | BIT_OR
        | IN | NOT_IN | IS | IS_NOT | LT | LE | GT | GE
        | EQ | NE
        | NOT | AND | OR
        | USER_OP)+
    ;

atomExpr
    : LPA expression RPA                                                # ParenthesisExpr
    | literal                                                           # LiteralExpr
    | identifier                                                        # IdExpr
    | THIS                                                              # IdExpr
    | SUPER LPA argumentList RPA                                        # ExplicitSuperExpr
    | SUPER                                                             # ImplicitSuperExpr
    | atomExpr NEWLINE* op=DOT dotAttribute                             # DotExpr
    | atomExpr LBK subscriptArgumentList RBK                            # SubscriptExpr
    | atomExpr LPA argumentList RPA lambdaDef?                          # FunctionCallExpr
    | atomExpr lambdaDef                                                # FunctionCallExpr
    | macroCallName LPA argumentList RPA lambdaDef?                     # MacroCallExpr
    | classDef                                                          # ClassDefExpr
    | functionDef                                                       # FuncDefExpr
    | lambdaDef                                                         # LambdaDefExpr
    | macroDef                                                          # MacroDefExpr
    | ifStmt                                                            # IfExpr
    | forStmt                                                           # ForExpr
    | whileStmt                                                         # WhileExpr
    | LBC statementList? RBC                                            # BlockExpr
    ;

/*
    Dot expression.
*/
dotAttribute
    : identifier
    | CLASS
    ;

/*
    Subscript expression.
*/
subscriptArgumentList
    : subscriptArgument (COMMA subscriptArgument)*
    ;

subscriptArgument
    : expression
    | sliceLiteral
    ;

sliceLiteral
    : lower=expression? COLON upper=expression? (COLON stride=expression?)?
    | lower=expression? DOUBLE_COLON stride=expression?
    ;

/*
    Class definition.
*/
// TODO: Add 'where' clause for type constraints.
classDef
    : CLASS className? typeParameterDef? baseClassDef? metaClassDef? blockBody
    ;

className
    : identifier (DOT identifier)*
    ;

typeParameterDef
    : LBK typeParameterList RBK
    ;

typeParameterList
    : typeParameter (COMMA typeParameter)*
    ;

typeParameter
    : identifier (qualifier=(COLON | LT | GT) typeExpr=expression)? (ASSIGN defaultValue=expression)?
    ;

baseClassDef
    : LT expression (COMMA expression)*
    ;

metaClassDef
    : DOUBLE_COLON expression
    ;

blockBody
    : COLON expression
    | LBC statementList? RBC
    ;

parameterList
    : parameter (COMMA parameter)*
    |
    ;

parameter
    : identifier (COLON typeExpr=expression)? (ASSIGN defaultValue=expression)?     # DefaultParameter
    | MUL identifier (COLON typeExpr=expression)?                                   # VarPosParameter
    | EXP identifier (COLON typeExpr=expression)?                                   # VarKwParameter
    | BIT_AND identifier (COLON typeExpr=expression)?                               # BlockParameter
    | marker=(DIV | MUL)                                                            # ParameterMarker
    ;

// TODO: Support *args and **kwargs.
argumentList
    : argument (COMMA argument)* COMMA?
    |
    ;

argument
    : identifier ASSIGN expression
    | expression
    ;

/*
    Function / lambda definition.
*/
functionDef
    : DEF funcName typeParameterDef? parameterDef? returnTypeDef? blockBody
    ;

funcName
    : (CLASS DOT)? (identifier DOT)* (identifier | OPERATOR stringLiteral)
    ;

parameterDef
    : LPA parameterList RPA
    ;

returnTypeDef
    : ARROW expression
    ;

lambdaDef
    : DO typeParameterDef? parameterDef? returnTypeDef? blockBody
// lambda without 'do' keyword (disabled now to reduce ambiguity)
//    | LBC typeParameterDef? parameterDef? FATARROW statementList? RBC
//    | LBC statementList? RBC
    ;

/*
    Macro definition.
*/
macroDef
    : MACRO macroName parameterDef? blockBody
    ;

macroName
    : identifier
    ;

/*
    Macro call.
*/
macroCallName
    : AT identifier
    ;

/*
    Control flow statements.
*/
ifStmt
    : IF condition blockBody (term? ELIF condition blockBody)* (term? ELSE elseBlock=elseBody)?
    ;

/*
    The `else` branch accepts both forms used in practice:

    - `else { ... }`
    - `else expression`
    - `else: expression` (allowed for symmetry with the `if` branch)
*/
elseBody
    : COLON expression
    | LBC statementList? RBC
    | expression
    ;

forStmt
    : FOR declTarget IN expression blockBody
    ;

whileStmt
    : WHILE condition blockBody
    ;

condition
    : expression
    ;


/*
    Literals.
*/

// TODO: Add list / tuple / set / dict comprehension.
literal
    : integerLiteral
    | FLOAT_LITERAL
    | stringLiteral
    | listLiteral
    | tupleLiteral
    | setLiteral
    | dictLiteral
    | TRUE
    | FALSE
    | NULL
    | ELLIPSIS
    ;

integerLiteral
    : DEC_INT
    | BIN_INT
    | OCT_INT
    | HEX_INT
    ;

stringLiteral
    : STRING_LITERAL
    ;

listLiteral
    : LBK expressionCommaList RBK
    ;

tupleLiteral
    : LPA RPA
    | LPA expression COMMA RPA
    | LPA expression (COMMA expression)+ COMMA? RPA
    ;

setLiteral
    : LSET_LITERAL expressionCommaList RSET_LITERAL
    | EMPTY_SET_LITERAL
    ;

dictLiteral
    : LDICT_LITERAL dictKeyList RDICT_LITERAL
    | EMPTY_DICT_LITERAL
    ;

dictKeyList
    : dictKey (COMMA dictKey)* COMMA?
    |
    ;

dictKey
    : expression COLON expression
    | EXP expression
    ;

expressionCommaList
    : expression (COMMA expression)* COMMA?
    |
    ;

term
    : (SEMICOLON | NEWLINE)+
    ;

identifier
    : IDENTIFIER
    // Soft keywords.
    | OPERATOR
    | INFIX
    | FROM
    ;

// Lexer

// Operators.

EXP: '**';

BIT_NOT: '~';

MUL: '*';
DIV: '/';
FLOOR_DIV: '//';
MOD: '%';

ADD: '+';
SUB: '-';

LSHIFT: '<<';
RSHIFT: '>>';

LT: '<';
LE: '<=';
GT: '>';
GE: '>=';
EQ: '==';
NE: '!=';

BIT_AND: '&';
BIT_XOR: '^';
BIT_OR: '|';

LDICT_LITERAL: '{:' {self.dictLiteralCount += 1; self.brackets.append('{:')};
RDICT_LITERAL: ':}' {self.dictLiteralCount -= 1; self.brackets.pop()};
EMPTY_DICT_LITERAL: '{:}';
LSET_LITERAL: '{.' {self.setLiteralCount += 1; self.brackets.append('{.')};
RSET_LITERAL: '.}' {self.setLiteralCount -= 1; self.brackets.pop()};
EMPTY_SET_LITERAL: '{.}';

AUG_ASSIGN
    : AddAssign | SubAssign | MulAssign | DivAssign | FloorDivAssign | ModAssign | ExpAssign
    | LShiftAssign | RShiftAssign | BitAndAssign | BitXorAssign | BitOrAssign
    ;

fragment AddAssign: '+=';
fragment SubAssign: '-=';
fragment MulAssign: '*=';
fragment DivAssign: '/=';
fragment FloorDivAssign: '//=';
fragment ModAssign: '%=';
fragment ExpAssign: '**=';
fragment LShiftAssign: '<<=';
fragment RShiftAssign: '>>=';
fragment BitAndAssign: '&=';
fragment BitXorAssign: '^=';
fragment BitOrAssign: '|=';

ASSIGN: '=';

ELLIPSIS: '...';
DOT: '.';
COMMA: ',';
ARROW: '->';
AT: '@';

LPA: '(' {self.parenthesisCount += 1; self.brackets.append('(')};
RPA: ')' {self.parenthesisCount -= 1; self.brackets.pop()};
LBK: '[' {self.bracketCount += 1; self.brackets.append('[')};
RBK: ']' {self.bracketCount -= 1; self.brackets.pop()};
AT_LBK: '@[' {self.bracketCount += 1; self.brackets.append('@[')};

LBC: '{' {self.brackets.append('{')};
RBC: '}' {self.brackets.pop()};
COLON: ':';
DOUBLE_COLON: '::';
SEMICOLON: ';';

// User-defined operators.
// NOTE: `.`, `:` and `@` are deliberately excluded. They belong to the
// structural tokens above, and allowing them here makes inputs such as
// `a..b`, `a::b` and `@@foo` lex as user operators, breaking method
// chaining, scoping and macro calls respectively.
USER_OP:
    UserOpChar+
    ;

fragment UserOpChar
    : '!' | '%' | '&' | '*' | '+' | '-' | '/' | '<' | '=' | '>' | '?' | '^' | '|' | '~'
    ;

// Keywords.
AND: 'and';
OR: 'or';
NOT: 'not';
IN: 'in';
NOT_IN: '!in';
IS: 'is';
IS_NOT: '!is';
AS: 'as';

VAR: 'var';
VAL: 'val';
DO: 'do';
DEF: 'def';
CLASS: 'class';
THIS: 'this';
SUPER: 'super';

IF: 'if';
ELSE: 'else';
ELIF: 'elif';
FOR: 'for';
WHILE: 'while';
BREAK: 'break';
CONTINUE: 'continue';
RETURN: 'return';

MACRO: 'macro';

IMPORT: 'import';

YIELD: 'yield';
AWAIT: 'await';

TRUE: 'true';
FALSE: 'false';
NULL: 'null';

// Soft keywords.
OPERATOR: 'operator';
INFIX: 'infix';
FROM: 'from';

// Integer literals.
DEC_INT: ('0' [dD])? ('0' | [1-9] Digit*);
BIN_INT: '0' [bB] BinDigit+;
OCT_INT: '0' [oO] OctDigit+;
HEX_INT: '0' [xX] HexDigit+;

fragment Digit: [0-9];
fragment BinDigit: [01];
fragment OctDigit: [0-7];
fragment HexDigit: [0-9a-fA-F];

FLOAT_LITERAL
    : PointFloat | ExponentFloat
    ;

fragment PointFloat
    : Digit* '.' Digit+
//    | Digit+ '.'          // Does not support '1.' to avoid ambiguity with '1.method'.
    ;

fragment ExponentFloat
    : (Digit+ | PointFloat) [eE][+-]? Digit+
    ;

// String literals.
STRING_LITERAL
    : ([Ff] | [Rr] | [Ff][Rr] | [Rr][Ff])? (ShortString | LongString)
    ;

fragment ShortString
    : '\'' ( EscapeSequence | ~['\\\r\n\f] )* '\''
    | '"' ( EscapeSequence | ~["\\\r\n\f] )* '"'
    ;

fragment LongString
    : '\'\'\'' LongStringItem*? '\'\'\''
    | '"""' LongStringItem*? '"""'
    ;

fragment EscapeSequence
    : '\\' ~[\n]
    ;

fragment LongStringItem
    : LongStringChar
    | EscapeSequence
    ;

fragment LongStringChar
    : ~'\\'
    ;

// Identifier (include anonymous parameters).
IDENTIFIER
    : Letter LetterDigit*
    | AnonymousParameter
    ;

fragment LetterDigit
    : Letter
    | Digit
    ;

fragment Letter
    : [a-zA-Z_]
    | ~(
        // covers all characters above 0x7F which are not a surrogate
        [\u0000-\u007F\uD800-\uDBFF]
        // Chinese punctuations【】（）；。：“”
        | [\u3010\u3011\uff08\uff09\uff1b\u3002\uff1a\u201c\u201d]
        )
    | [\uD800-\uDBFF] [\uDC00-\uDFFF] // covers UTF-16 surrogate pairs encodings for U+10000 to U+10FFFF
    ;

fragment AnonymousParameter
    : '$' ('0' | [1-9] Digit*)?
    ;

COMMENT
    : '#' ~[\r\n]* -> skip;
LINE_ESCAPE
    : '\\' '\r'? '\n' -> skip;
IGNORED_NEWLINE
    : '\r'? '\n' {(self.parenthesisCount != 0 or self.bracketCount != 0 or self.dictLiteralCount != 0 or self.setLiteralCount != 0) and (self.brackets and self.brackets[-1] != '{')}? -> skip;
NEWLINE: '\r'? '\n';
WS: [ \t]+ -> skip;
