# 解析器实现

词法与语法分析由 [ANTLR4](https://www.antlr.org/) 生成（`grammars/Oort.g4`），
表达式部分交给手写的 **Pratt 解析器**（见 `frontend/ast_builder.py`）。

## 前端流水线

```
源码 → OortLexer → OortParser → 解析树 → ASTBuilder(+Pratt) → AST → Pass1 语义分析 → 解释器
```

- ANTLR 负责“词法扁平化”：把所有运算符 token 收集到 `flattenExprList`，
  不在文法里编码优先级。
- `ASTBuilder` 在 `flattenExprList` 上运行 Pratt 算法，生成正确的表达式树。
- 解析树不会进入后续阶段；之后的类型检查/解释只认自定义 AST。

## 为什么用 Pratt

- 优先级与结合性集中在一张表里（`frontend/operator_defs.py`），增删运算符
  不需要改文法。
- 支持中缀函数调用（`a plus b`）与用户自定义运算符 token。
- 为未来的**按方言/作用域注册运算符**留出接口（`OperatorTable.parent`），
  这是 [DSL 提案](../proposals/0002-dsl-support.md) 的基础。

## 换行与括号

Oort 语句末尾不需要分号，因此需要区分“语句结束换行”与“长表达式内部换行”。
词法器维护一个括号栈：

- 位于 `()`、`[]`、`{: :}`、`{. .}` 内且最内层不是 `{}` 时，`\n` 被丢弃；
- 否则产生 `NEWLINE` token，作为语句分隔符；
- 行尾 `\` 显式续行。

实现见 `Oort.g4` 的 `@lexer::members` 与 `IGNORED_NEWLINE` 谓词。

## 错误报告

ANTLR 默认错误信息不够详细。`OortErrorListener` 把词法/语法错误交给
`CompilerErrorHandler`，后者利用 `SourcePosition` 输出：

```
<string>:1:7: OortSyntaxError: Invalid syntax
print(
      ^^^^^
```

语义分析、AST 构建与运行期错误共用同一个处理器；`UnsupportedSyntax` 也走这条路径。
`ASTBuilder.parse` 会捕获构建期的 `OortException`，避免以 Python traceback 结束。

## 文法清理记录

作为“避免 C++ 式历史包袱”的一次实践，文法做了以下收紧（见
[proposal 0003](../proposals/0003-grammar-cleanup.md)）：

- `USER_OP` 字符集移除 `.`、`:`、`@`：它们分别属于方法链、作用域、宏调用，
  混入自定义运算符会产生 `a..b`、`a::b`、`@@foo` 等歧义。
- 删除空转 token：`DOTIF`、`ASIF`、`FATARROW`、`COMPTIME`、`ASYNC`。
  需要时通过提案重新引入，而不是保留“死 token”。
- `elif` 正式实现；`else` 统一为 `elseBody`，同时接受 `else expr`、
  `else: expr`、`else { ... }`。
- 切片支持 `[::step]` / `[lower::step]`（`DOUBLE_COLON` 与 `::` 元类语法共用词法）。
- 赋值两侧改为 `expressionList`，从而支持 `a, b = b, a` 与 `var a, b = 1, 2`。

## 已知限制

- 不支持一元后缀运算符（参考 Scala 的后缀调用争议）。
- 用户自定义运算符可以解析并按默认优先级求值；按作用域声明运算符优先级尚未实现。
- 格式化字符串尚未实现；`f"..."` 会显式报错。
- 类型参数、宏、`yield`/`await` 能解析，但语义分析阶段会拒绝。
