# OP 0003: 文法清理与语义收紧

- **状态**：Implemented
- **作者**：Oort 设计讨论
- **相关**：[实现笔记 02](../implementation/02-parser.md)、[规范 01](../spec/01-lexical.md)

## 摘要

依据“拒绝半成品、消除特殊字符歧义”的原则，对 `Oort.g4` 与运行时语义做了一轮清理：

1. 收紧 `USER_OP` 字符集；
2. 删除没有 parser 规则的“死 token”；
3. 正式实现 `elif`，对称化 `else`；
4. 支持 `[::step]` 切片；
5. 赋值/声明两侧使用表达式列表，支持元组解包；
6. 格式化字符串显式拒绝，避免解析期执行任意代码；
7. 未实现特性在语义分析阶段统一报 `UnsupportedSyntax`。

## 动机

原文法为了“以后可能支持”保留了多个 token，但没有对应的解析规则；同时
`USER_OP` 包含 `.`、`:`、`@`，会与方法链、作用域、宏调用的结构字符冲突。
此外，AST visitor 的默认行为是遍历子节点，导致未实现的节点被静默“穿透”，
产生错误结果而不是报错。

## 设计（已实现）

### 1. `USER_OP` 字符集

```text
! % & * + - / < = > ? ^ | ~
```

移除 `.`、`:`、`@`：

| 输入 | 之前 | 现在 |
|------|------|------|
| `a..b` | `USER_OP("..")`（无法解析） | `DOT DOT`（语法错误，清晰） |
| `a::b` | `DOUBLE_COLON`（恰好正确） | 不变 |
| `@@foo` | `USER_OP("@@") + Id`（宏调用被破坏） | `AT AT Id` |
| `a:::` | `USER_OP(":::")` | `DOUBLE_COLON + COLON` |

### 2. 删除死 token

`DOTIF`（`.?`）、`ASIF`（`as?`）、`FATARROW`（`=>`）、`COMPTIME`、`ASYNC`。
需要时通过提案重新引入并同时实现语义，而不是保留无法使用的词法 token。

### 3. `elif` 与 `else`

```antlr
ifStmt
    : IF condition blockBody (term? ELIF condition blockBody)* (term? ELSE elseBlock=elseBody)?
    ;
elseBody
    : COLON expression
    | LBC statementList? RBC
    | expression
    ;
```

- `elif` 在 AST 中降级为嵌套 `if`；
- `else` 同时接受 `else expr`、`else: expr`、`else { ... }`，消除原来的不对称；
- `elif` / `else` 可以换行书写。

### 4. 切片

`DOUBLE_COLON` 同时用于元类语法 `class C :: M`，因此切片文法显式接受它：

```antlr
sliceLiteral
    : lower=expression? COLON upper=expression? (COLON stride=expression?)?
    | lower=expression? DOUBLE_COLON stride=expression?
    ;
```

支持 `[1:3]`、`[::2]`、`[1::2]`。

### 5. 表达式列表

```antlr
assignStmt: lhs=expressionList op=(ASSIGN | AUG_ASSIGN) rhs=expressionList;
variableDecl: kind=(VAR | VAL) declTarget ASSIGN expressionList;
```

支持 `a, b = b, a`、`var a, b = 1, 2`、`var p, q = [3, 4]`。
增强赋值不允许元组目标。

### 6. 字符串

`f"..."` 在 AST 构建阶段报 `UnsupportedSyntax`；普通/原始字符串用
`ast.literal_eval` 解析，替换了原来的 Python `eval`（后者可在解析期执行任意代码）。

### 7. 显式拒绝未实现特性

`Pass1Analyzer` 对模块、宏、`yield`/`await`、类型参数、默认/可变参数、
关键字实参、匿名形参、编译器属性等统一报错。完整清单见
[06-conformance.md](../spec/06-conformance.md)。

## 影响

- 原先依赖 `..`、`@@` 等 token 组合的代码本来就不能正确运行，清理是兼容的。
- `else` 的两种写法都保留，`elif` 是新增语法。
- 赋值两侧的表达式列表使 `a = 1, 2` 成为元组赋值，而不是语法错误。

## 测试

- `tests/unit/frontend/test_lexer.py`：token 字符集、换行、注释。
- `tests/unit/frontend/test_parser.py`：优先级、切片、`elif`、`..`、格式化字符串。
- `tests/unit/runtime/test_declarations.py`：多目标声明与交换。
- `tests/unit/frontend/test_unsupported.py`：完整拒绝清单。

## 未解决问题

- 是否引入显式的范围运算符（`..<`、`..=`、`..`）？需要先定义 Range 类型。
- 类型标注目前解析但不检查；在类型系统落地前保持“接受但忽略”。
