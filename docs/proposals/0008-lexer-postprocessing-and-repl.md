# OP 0008: 词法后处理层与 REPL 重构

- **状态**：Implemented（2026-11-20）
- **作者**：Oort 设计讨论
- **相关**：[OP 0001](0001-feature-layers-and-dialects.md)、
  [实现笔记 02](../implementation/02-parser.md)、
  [实现笔记 03](../implementation/03-interpreter.md)

## 摘要

把 `Oort.g4` 中与 Python 绑定的词法动作（括号计数、换行抑制、特殊 token 计数）
移出文法，改为**词法器之后、解析器之前的 token 后处理层**；同时重构 REPL 为
独立的 `ReplSession` 状态机，不再依赖 ANTLR 的 lexer/parser 内部字段。

目标是让文法本身与宿主语言无关、让换行规则可单元测试，并让 REPL 的续行、
EOF、错误恢复行为可预测。

## 动机

### 1. 文法依赖 Python 动作

当前 `grammars/Oort.g4` 在 lexer 中嵌入 Python：

- `@lexer::members` 保存 `parenthesisCount`、`bracketCount`、`dictLiteralCount`、
  `setLiteralCount` 与 `brackets` 栈；
- `LPA` / `RPA` / `LBK` / `RBK` / `AT_LBK` / `LBC` / `RBC` 与字典/集合字面量
  token 都带 `{...}` 动作；
- `IGNORED_NEWLINE` 用 `self.brackets` 谓词决定是否丢弃换行。

后果：

- 文法不能直接生成其他 ANTLR target，阻碍未来的 Rust/其他语言实现；
- 动作在词法阶段执行宿主代码，未匹配的闭括号会直接崩溃：

  ```text
  }        → IndexError: pop from empty list
  )        → IndexError: pop from empty list
  ```

  这是语法错误，应该由诊断系统报告，而不是 Python traceback；
- 括号状态是 REPL 续行判断的唯一来源，导致 REPL 依赖 lexer 内部实现。

### 2. REPL 依赖 ANTLR 内部字段

`driver/repl.py` 目前：

- 复用同一个 lexer/parser，通过修改 `lexer.inputStream`、`lexer.line` 来喂新行；
- 调用 `token_stream.fill()` 后手动 `tokens.pop()`、重置 `fetchedEOF`；
- 用 `lexer.brackets` 判断是否需要续行；
- 没有处理 EOFError：管道输入或 Ctrl-D 会以 traceback 结束；
- Ctrl-C 的语义固定为退出，无法“取消当前多行输入”。

这些细节与 ANTLR 运行时版本耦合，难以测试，也难以在未来后端复用。

## 设计

### 1. 文法纯净

`Oort.g4` 中删除所有宿主语言动作与谓词：

- 移除 `@lexer::members`；
- 移除所有 token 上的 `{...}` 动作；
- 删除 `IGNORED_NEWLINE`，`NEWLINE` 始终产生；
- `LINE_ESCAPE`（行尾 `\` 续行）可以保留为纯文法规则。

删除后，词法器只负责把源码切成 token，不再维护语义状态。

### 2. 词法后处理层

新增 `parser/token_processor.py`（名称可调整），对 token 序列做纯函数处理：

```
源码 → OortLexer → list[Token] → NewlineFilter → parser token stream
```

- 维护一个括号栈，打开 token：`LPA`、`LBK`、`AT_LBK`、`LDICT_LITERAL`、
  `LSET_LITERAL`、`LBC`；关闭 token：`RPA`、`RBK`、`RDICT_LITERAL`、
  `RSET_LITERAL`、`RBC`。
- 与当前规则保持一致：只有当栈非空且栈顶不是 `LBC`（代码块）时，丢弃 `NEWLINE`；
  代码块内的换行仍作为语句分隔符。
- 未匹配的关闭 token 不做栈操作，原样交给 parser，由错误监听器报告。
- 暴露 `bracket_depth` / `is_incomplete` 供 REPL 使用。
- 输入结束后若括号栈非空，或最后一行以未转义的 `\` 结束，则视为“输入未完成”。

实现上可以预先把 token 收集为列表，再由 `ListTokenSource` 构造
`CommonTokenStream`；正常文件与 REPL 共用同一条管线。

### 3. REPL 会话状态机

把 `run_repl` 拆成两层：

- `ReplSession`：纯逻辑，不依赖 rich/Console。
  - 累积源码缓冲区与 `InputInfo`；
  - 调用词法后处理判断是否完整；
  - 完整时解析整个缓冲区、语义分析、在当前解释器中求值；
  - 持有持久的全局环境/解释器与语句计数；
  - 返回 `CONTINUE` / `EVALUATED` / `ERROR` / `EXIT` 等动作。
- `ConsoleIO`（或 `ReplConsole`）：负责提示符、颜色、输入、结果打印；
  测试时替换为 `FakeConsoleIO`。

行为约定：

- 每次提交重新解析完整缓冲区，不修改 lexer/parser 内部状态；
- 语法错误后清空当前缓冲区并保留解释器环境，REPL 继续运行；
- EOF（Ctrl-D、Windows Ctrl-Z + Enter，或管道结束）正常退出并返回 0；
- Ctrl-C 在输入阶段取消当前输入，在执行阶段中断当前语句，均不退出；
- `exit` / `quit` 在空闲提示符下显式退出；
- 非 TTY（管道/重定向）下仍可工作；是否隐藏提示符另行决定，但必须有
  subprocess 冒烟测试覆盖。

### 4. 与方言的关系

词法后处理与 REPL 都属于**共享骨架**，不携带方言策略：

- `#lang` 指令的解析放在词法后处理之前的入口层（注意 `#` 也是注释起始符，
  需要单独处理首行）；
- 运算符表、特性门控仍由方言配置决定；
- REPL 的求值器与语义分析器由方言提供，会话本身不感知具体方言。

## 测试策略

REPL 建议按层次测试，而不是只靠手动输入：

| 层级 | 内容 | 位置 |
|------|------|------|
| 单元 | 括号栈/换行过滤：`()`、`[]`、`{}`、`{: :}`、`{. .}`、嵌套、字符串/注释中的括号、未匹配闭括号、行尾 `\` | `tests/unit/frontend/` |
| 单元 | `ReplSession` 完整性判断与状态迁移，不依赖 Console | `tests/unit/` 或 `tests/integration/` |
| 集成 | 脚本化 transcript：多行、错误恢复、变量持久化、空行、提示符/结果格式 | `tests/integration/test_repl.py` |
| 子进程 | 用管道 stdin 启动真实 CLI，检查退出码、stdout/stderr、EOF、版本 banner | `tests/integration/` |
| PTY（可选） | Ctrl-C/Ctrl-D、行编辑、历史、粘贴；跨平台成本高，可用标记在本地/夜间运行 | 可选 |
| 性质/模糊 | 合法程序的所有前缀都不应崩溃或挂起；完整判断应单调 | 可选 |
| 手动冒烟 | 终端特有的显示、颜色、快捷键与交互体验 | `private/repl-smoke.md` |

原则：**自动化测试放 `tests/`，`private/` 只放无法稳定自动化的终端人工检查清单**；
冒烟测试不应成为唯一的 REPL 保障。

## 正交性检查

- 与方言：后处理层与 REPL 是共享骨架；方言只提供语义分析器与求值器。
- 与运算符：换行/括号处理不改变 Pratt 表或运算符语义。
- 与模块：`#lang` 指令解析在入口层，可复用同一 token 管线。
- 与后端：token 后处理与 REPL 不依赖 AST 解释器；字节码/编译模式可复用同一会话接口。

## 替代方案

1. **保留 lexer 内嵌 Python 动作**：实现最简单，但文法不可移植、错误输入会导致
   Python traceback，REPL 继续依赖内部字段。放弃。
2. **REPL 自己按字符统计括号**：会把字符串/注释中的括号算进去，且与文法规则
   重复实现。放弃。
3. **为 REPL 维护独立的分词器**：造成两套词法规则，容易漂移。放弃。
4. **增量解析器**：长期可能有价值，但当前规模不需要；先做整缓冲区重解析。

## 迁移计划

1. 在文法中删除 lexer 动作与 `IGNORED_NEWLINE`，让 `NEWLINE` 始终产生。
2. 实现 token 后处理层，并让 `Compiler` 与 REPL 共用。
3. 添加单元测试：括号/换行过滤、未匹配闭括号、字符串与注释中的括号。
4. 重构 REPL 为 `ReplSession` + `ConsoleIO`，处理 EOFError、Ctrl-C 语义与
   整缓冲区重解析。
5. 添加 transcript、子进程与（可选）PTY 测试；建立 `private/repl-smoke.md`。
6. 更新 `docs/implementation/02-parser.md` 与测试文档。

## 已决问题（2026-11-20）

- **Ctrl-C**：输入阶段取消当前行与待提交的多行缓冲区；执行阶段中断当前语句
  （`KeyboardInterrupt`）并回到提示符；两种情况下环境保留已发生的副作用。
  与 CPython/IPython/IRB/GHCi/Julia 一致，不采用 Node 的“双击 Ctrl-C 退出”。
- **退出键**：Unix 为 Ctrl-D；Windows 控制台为 Ctrl-Z 后按 Enter（Python
  `input()` 的 EOF 约定，PowerShell 同样适用）。
- **显式退出**：整行恰为 `exit` 或 `quit` 时由 REPL 层拦截（仅在没有待提交
  多行输入时），不进入语言语义；与 Python/IPython/Ruby/Bash 的显式退出命令
  对齐，也为 Windows 用户提供可发现的退出方式。
- **非 TTY**：隐藏 `In [n]` / `Out[n]` 提示符，但仍正常求值；管道 EOF 正常
  退出并返回 0。
- **历史/行编辑**：本版不做，依赖终端自身；后续如需再引入 `prompt_toolkit`。
- **`#lang` 消歧**：继续在入口层按首行预处理，词法器仍把它当注释；后处理层
  不负责指令剥离或位置重映射。
- **未匹配闭括号**：token 后处理不做栈操作，原样交给解析器报语法错误。

## 未解决问题

- 是否支持增量解析（当前每次提交重解析整个缓冲区）。
- 非 TTY 下是否需要完全静默 banner（当前保留 banner，便于日志识别）。
- `#lang` 与首行 BOM/空行的更细边界（现有入口层测试已覆盖主要情形）。
