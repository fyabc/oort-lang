# OP 0020: 诊断消息质量（效仿 Python 的错误消息改进）

- **状态**：Implemented
- **作者**：fyabc
- **创建日期**：2026-11-22
- **相关提案**：[OP 0008](0008-lexer-postprocessing-and-repl.md)（token 后处理层）、
  [OP 0003](0003-grammar-cleanup.md)（文法清理）

## 摘要

把「能用但含混」的诊断消息改进为「说出类别、指对位置」的消息。本轮覆盖
四个高频类别：**词法错误**（未终止字符串、非法字符）、**定界符错误**
（未闭合/多余的括号）、**花括号字面量习惯提示**（Python 式 `{1, 2}` 的
定向 did-you-mean）与**Python 习惯建议**（None/True/self、`&&`/`||`/`!`、
`{}` 空块、行首 `//`、`i++`、`lambda`、条件内 `=`）。方法论与措辞对照
Python 3.10+ 的错误消息改进。

## 动机

改进前的真实输出（`oort -c`）：

```text
$ oort -c "'1"
line 1:0 token recognition error at: ''1'      # ANTLR 原文透出，且退出码 0

$ oort -c "{: '1':"
<string>:1:8: OortSyntaxError: Invalid syntax   # 位置与 caret 都不知所云
{: '1':
       ^^^^^
```

问题分三层：

1. **词法错误未接入诊断管线**：ANTLR Lexer 挂的是默认 ConsoleErrorListener，
   原文直接进 stderr，且出错字符被跳过后程序可能以退出码 0「成功」；
2. **消息不分类**：`Invalid token` / `Invalid syntax` 是 V8
   `Invalid or unexpected token` 式的万能句，用户无从下手；
3. **位置指错地方**：括号未闭合时，ANTLR 在耗尽输入处报错，离真正的
   错误（开括号）很远。

参照系（各语言对同一类错误的措辞）：

| 语言 | 未终止字符串 | 非法字符 | 未闭合括号 |
|---|---|---|---|
| Python 3.10+ | `unterminated string literal` | `invalid character '“' (U+201C)` | `'{' was never closed` |
| javac | `unclosed string literal` | `illegal character: '#'` | `reached end of file while parsing` |
| Go | `newline in string` | — | `unexpected $end` |
| SpiderMonkey | `unterminated string literal` | — | — |
| V8（反例） | `Invalid or unexpected token` | 同左 | 同左 |

要点：好的消息**命名类别**并**带上出错文本**（含码点，对从网页/字处理
软件粘贴的全角引号、不可见字符至关重要）；Python 3.10 的 PEG 解析器
错误消息重写（3.8 的 `EOL while scanning string literal` → 3.10 的
`unterminated string literal`）证明了这不是玄学，而是可以逐类积累的
工程工作。本提案采取同样的路径。

## 设计

### 原则

1. **说类别，不说行话**：消息命名失败种类（unterminated / unmatched /
   invalid character），不暴露实现细节（token、rule、ANTLR 术语）；
2. **指对位置**：错误指向**根因处**（开括号、出错字符），不是解析器
   放弃处；caret 覆盖最小有用跨度；
3. **保持单条**：定界符错误引发的级联解析错误被替换为一条根因诊断，
   不重复报噪音（Python 同此行为）；
4. **分类信号来自已有数据**：不新增词法/语法分析遍数——词法分类用
   ANTLR msg 中「失败规则尝试匹配的文本」，定界符用 token 后处理层
   既有的括号栈（OP 0008 为 REPL 完整性检查引入）。

### 词法错误分类

Lexer 挂 `OortErrorListener`（与 parser 同一管线）。词法通知没有
offending token，位置由行/列构造，caret 指向出错字符。消息按尝试匹配
文本分类：

| 输入 | 消息 |
|---|---|
| `'1` / `"abc` / `r'x` | `Unterminated string literal` |
| `"""abc` | `Unterminated triple-quoted string literal` |
| `` ` `` / `\` | ``Invalid character '`' (U+0060)`` |
| 兜底（msg 不可解析） | `Invalid token` |

分类依据文法可穷尽：`EscapeSequence` 在词法层宽松（`\\ ~[\n]`），
字符串类词法错误只有「未终止」；数字字面量总能回退到 `DEC_INT` 短匹配
（`0x` 的词法结果是 `0` + 标识符 `x`，报解析错），不产生词法错误；
非引号开头的失败按构造只可能是单个非法字符。

三引号判别：ANTLR 对 `"""abc` 的报错在第 **3** 个引号处（前两个引号
先匹配成空字符串），因此用**错误位置之前的两个源码字符**是否同为该
引号来判别，而非错误文本前缀。

### 定界符错误

`process_tokens`（OP 0008 的 token 后处理层）本就维护括号栈供 REPL
判断输入完整性；现在把栈内容与「栈空时遇到的闭括号」记入
`TokenizedInput.unclosed_openers / unmatched_closers`。

`Compiler.build_ast` 在解析产生错误且存在定界符问题时，**回撤**本次
解析新增的诊断，替换为一条指向定界符本身的消息：

| 输入 | 消息 | 位置 |
|---|---|---|
| `{: '1':` | `'{:' was never closed` | 开括号处（1:1） |
| `if true { print(1)` | `'{' was never closed` | 开括号处（1:9） |
| `]` | `Unmatched ']'` | 闭括号处 |

措辞与位置策略均对齐 Python（`'{' was never closed` 指向开括号、
`unmatched ']'` 指向闭括号）。REPL 不受影响：未闭合括号仍判定为
「输入未完成」继续读行；仅 EOF flush 路径会给出该诊断。

### 花括号字面量提示（轻量 did-you-mean）

Python 用户的常见习惯错误是写 `{1, 2}` / `{1: 2}`——在 Oort 里 `{}` 是
代码块，解析失败后报的是 ANTLR 噪音
（`mismatched input '}' expecting {AUG_ASSIGN, '='}`）。对齐 Python 3.10+
"did you mean" 的思路，解析失败后扫描 token 流：单行 `{` 块体内、
括号嵌套深度为 0 处出现的首个分隔符（`:` → Dict、`,` → Set）触发一条
`OortSyntaxWarning` 建议：

```text
val _ = {1, 2}
<string>:1:9: OortSyntaxWarning: Did you mean a Set literal '{. item, ... .}'? '{' opens a code block.
```

守卫：块体首 token 为语句关键字（`if`/`def`/`var` 等，避免误报
`{ if a: 1 }`）、分隔符嵌套在 `()`/`[]` 内（`{ g(1, 2) }` 正常解析且
不提示）、每次输入至多一条提示。

### Python 习惯建议

对运行期与解析期的另几类 Python 习惯，追加「did you mean」建议：

| 输入 | 诊断 |
|---|---|
| `print(None)` / `True` / `self` | `Name 'None' is not defined (did you mean 'null'?)`（名称表：None/True/False/self → null/true/false/this；解释器与 VM 共享） |
| `1 && 2` / `!true` | `does not support operator '&&' (did you mean 'and'?)`（运算符表：&&/\|\|/! → and/or/not；VM 运算符分发委托解释器，天然共享） |
| `val d = {}` | `Did you mean an empty Dict '{:}' or Set '{.}'?`——`{}` 是空代码块，程序**合法**且值为 null，属静默语义陷阱，故以 SyntaxWarning 提示且退出码仍为 0；仅表达式位置（前一 token 为 `=`/`(`/`,`/`return`）触发，空类体/空函数体不误报 |
| 行首 `//` | `Did you mean a comment? …`——`//` 是整除运算符，`// comment` 会解析成奇怪的表达式后在运行期报无关的 NameError |
| `i++` | `Oort has no postfix '++'; use += 1.`——措辞限定**后缀**：二元 `operator "++"` 可被用户定义，但 Oort 没有任何后缀运算符；提示仅在解析失败时触发，合法的中缀 `a ++ b` 不受影响 |
| `lambda(x): x` | `'lambda' is not a keyword; Oort lambdas use 'do'` |
| `if x = 1 { }` | `Assignment is a statement; did you mean '==' in the condition?` |

Pratt 阶段的错误（如缺操作数）在 AST 构建期才进入错误处理器，因此
失败门控的提示在解析后与构建后各跑一次（发出即短路）；`elif` 经查是
既有关键字（if/elif/else 链），无需提示。

### 输出通道

rich 控制台按宽度折行会把消息短语拆开（也使 grep/管道处理困难）。
新增 `--plain` 选项：诊断输出不走 rich，每条记录一行，用于管道与
脚本场景。

### 边界与限制

本轮**不做**（记录为后续工作）：

- ANTLR `extraneous input … expecting {大集合}` 的精简（如 `val x 1`、
  `x =`；需要 curated 规则或迁移到带恢复策略的解析层）；
- 拼写错误的编辑距离 did-you-mean（固定 Python 拼写对照表已完成，
  `esle` 这类任意拼写候选仍属后续）；
- 多错误恢复（当前首个解析错误后由 ANTLR 默认恢复策略继续，质量不一）；
- REPL 控制台对长消息的折行美化（rich 按宽度折行会把短语拆开；
  `--plain` 是当前的出口）。

## 正交性检查

- 与类型系统：无关（纯前端诊断）；
- 与类/对象：无关；
- 与函数/闭包：无关；
- 与模块：`compile_unit_details`（模块导入编译）同样传入 tokenized，
  模块文件享受相同诊断；
- 与方言：诊断发生在词法/解析层，先于方言门控，两方言一致；
- 与 REPL：括号栈语义不变（`incomplete` 判定不动），仅 flush 路径新增
  诊断。

## 实现与测试

- `diagnostics/error_listener.py`：词法分类（尝试文本 + 源码前缀）；
- `parser/token_processor.py`：`unclosed_openers` / `unmatched_closers`；
- `diagnostics/error_handler.py`：`retract_since`（回撤级联条目）；
- `driver/compiler.py`：`build_ast(tokenized=...)` 与
  `_report_delimiter_diagnostic`；REPL flush 传入 tokenized。
- 测试：CLI 参数化语料（词法 5 例 + 定界符 8 例 + 花括号提示 3 例与
  防误报守卫 + 习惯建议 10 例与防误报，断言消息与位置）、token 后处理
  定界符追踪 8 例、`--plain` 子进程用例、REPL EOF 子进程用例更新。

## 后续工作

1. 解析错误 curated 消息：`missing ... before ...`、`expected ':'` 等
   （Python 3.10 PEG 的做法是给每个失败点写人话模板）；
2. 语义/名称阶段引入 did-you-mean（编辑距离 ≤ 2 的候选）；
3. `docs/spec/06-conformance.md` 增补诊断消息清单，作为回归基线。

## 参考

- Python 3.10 错误消息改进（PEG parser rewrite）与
  [invalid character 诊断说明](https://adamj.eu/tech/2022/01/14/how-to-fix-python-syntaxerror-invalid-character)；
  [版本间 SyntaxError 演进](https://dev.to/lavary/how-to-fix-syntaxerror-invalid-character-in-python-28ie)；
- javac `unclosed string literal` / `illegal character`；
- Go `newline in string`；SpiderMonkey `unterminated string literal`；
  V8 `Invalid or unexpected token`（反面参照）。
