# 解析器实现

词法与语法分析由 [ANTLR4](https://www.antlr.org/) 生成（`grammars/Oort.g4`），
表达式部分交给手写的 **Pratt 解析器**（见 `parser/ast_builder.py`）。

## 前端流水线

```
源码 → OortLexer → TokenProcessor → OortParser → 解析树
     → ASTBuilder(+Pratt) → AST → Pass1 语义分析 → 解释器
```

`parser/token_processor.py` 位于词法器与解析器之间，是一层纯 token 处理：
文法本身不维护括号/换行状态，也不含宿主语言动作。

- ANTLR 负责“词法扁平化”：把所有运算符 token 收集到 `flattenExprList`，
  不在文法里编码优先级。
- `ASTBuilder` 在 `flattenExprList` 上运行 Pratt 算法，生成正确的表达式树。
- 解析树不会进入后续阶段；之后的类型检查/解释只认自定义 AST。

## 为什么用 Pratt

- 优先级与结合性集中在一张表里（`parser/operator_defs.py`），增删运算符
  不需要改文法。
- 使用整数 binding power（左结合取 `p + 1`，右结合取 `p`），不再用浮点
  epsilon；非结合运算符（比较）通过 `Associativity.NONE` 标记，链式写作
  `a < b < c` 会报语法错误。
- 为中缀函数调用与用户自定义运算符 token 保留了解析路径，但隐式中缀
  （`a plus b`）当前关闭，等 OP 0002 的显式 `infix` 声明。
- 为未来的**按方言/作用域注册运算符**留出接口（`OperatorTable.parent`），
  这是 [DSL 提案](../proposals/0002-dsl-support.md) 的基础。

## 换行与括号

Oort 语句末尾不需要分号，因此需要区分“语句结束换行”与“长表达式内部换行”。
词法器现在**始终**产生 `NEWLINE`；`TokenProcessor`（`parser/token_processor.py`）
按括号栈过滤：

- 位于 `()`、`[]`、`@[]`、`{: :}`、`{. .}` 内且最内层不是 `{}` 时，
  `NEWLINE` 被丢弃；
- 最内层是代码块 `{}` 或栈为空时保留 `NEWLINE`，作为语句分隔符；
- `LINE_ESCAPE`（行尾 `\`）由词法器产生、后处理层丢弃，并用于判断输入是否
  未完成；
- `atomExpr NEWLINE* DOT` 允许行首 `.` 继续方法链（例如 `user\n    .name()`）。

后处理还提供 `bracket_depth` 与 `incomplete`：未匹配的闭括号原样交给解析器，
由错误监听器给出正常语法诊断，不再触发词法器的 `IndexError`；REPL 用同一份
结果决定是否继续读取多行输入（见 [OP 0008](../proposals/0008-lexer-postprocessing-and-repl.md)）。

## 匿名参数

`$0` / `$1` 不需要改文法（`AnonymousParameter` 已经是 `IDENTIFIER` 的一部分）。
`ASTBuilder` 在构建无显式参数列表的 `do` lambda 时扫描 body，跳过嵌套函数/类，
以最大下标推断参数个数并记录到 `FunctionDef.anonymous_count`；
`Pass1Analyzer` 再合成 `$i` 绑定并拒绝显式声明。

## 参数形状

`ASTBuilder.parseParameterList` 负责参数布局：`/` 与 `*` 标记、`*args` /
`**kwargs` / `&block` 的位置、重复参数名、默认值后置规则与裸 `*` 后必须有
关键字限定参数。调用实参的 `identifier = expression` 被标记为
`ArgumentKind.KEYWORD`；尾随 lambda 标记为 `ArgumentKind.BLOCK`。
绑定语义不在前端实现，见 `runtime/signature.py`（OP 0011）。

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

## REPL

`driver/repl.py` 分成两层：

- `ReplSession`：纯逻辑，持有 `ReplInputInfo`、解释器与模块加载器；每次收到
  一行就把它追加到当前提交缓冲区，用 `Compiler.prepare_parser` 重新词法/
  后处理，`incomplete=True` 时继续等待，否则解析、语义分析并在持久环境中求值。
  成功或报错后清空缓冲区并递增语句计数；解释器环境保留。
- `ConsoleIO`：提示符、banner 与结果输出；非 TTY 下隐藏提示符，管道输入仍可
  正常求值。测试可替换为任意实现。

行为：EOF（Unix Ctrl-D；Windows Ctrl-Z + Enter；或管道结束）正常退出并返回
0；Ctrl-C 始终取消当前输入与待提交缓冲区并回到新提示符（与 Python/IPython
一致）；语法/运行时错误只清空当前缓冲区，REPL 继续运行。会话不修改 ANTLR 的 `lexer.inputStream` / `token_stream.tokens` /
`fetchedEOF`，也不复用 parser 实例。

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
- `IDENTIFIER` 去掉 `!` 后缀：`a!=b`、`x!in xs`、`a!is b` 无需空格即可正确分词。
- `parameterDef` 只保留括号形式，消除裸形参下 `:` 的类型标注/函数体歧义。
- `BREAK expression?` 支持 `break value`；`AUG_ASSIGN` 增加 `//=`；
  token `TRUE_DIV` 更名为 `FLOOR_DIV`。
- 方法链允许在 `.` 前换行。

## 已知限制

- 不支持一元后缀运算符（参考 Scala 的后缀调用争议）。
- 用户自定义运算符可以解析并按默认优先级求值；按作用域声明运算符优先级尚未实现。
- 隐式中缀调用（`a plus b`）已关闭，等 OP 0002 的显式 `infix` 声明。
- 格式化字符串尚未实现；`f"..."` 会显式报错。
- 类型参数、宏、`yield`/`await` 能解析，但语义分析阶段会拒绝。
- 未匹配的闭括号（如单独的 `)` / `}`）现在由文法/解析器报语法错误；词法器
  不再维护状态，也不会崩溃。
