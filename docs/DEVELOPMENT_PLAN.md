# Oort 开发计划

## 定位

Oort 是用于学习编译原理与编程语言设计的玩具语言。Python 原型优先验证**语义**；
性能与工程化（字节码、LLVM、Rust）在语义稳定后再做。

设计约束（所有阶段适用）：

1. 特性正交，不写“类型特判”；
2. 未实现的语法显式报错，不保留半成品；
3. 元编程（宏、`comptime`）最后做；
4. 每个特性先有规范与测试，再有优化；
5. 方言是语义边界：共享骨架不承载方言策略，后端不为方言复制。

## 开发模型：共享骨架 + 方言垂直切片

开发与验收以**方言**为主轴，但共享组件保持方言无关：

| 层 | 内容 | 纪律 |
|----|------|------|
| 共享骨架 | 词法/语法超集、AST、源码位置、诊断、模块加载、CLI/REPL、测试框架 | 不为单个方言加特判 |
| 方言切片 | 对象模型、语义分析、特性门控、规范与测试 | 一个方言一个语义分析器 |
| 共享后端 | 树遍历解释器 → 统一 HIR → 字节码 VM | 方言差异在进入 HIR 前消化 |

原则：

- 一次只把一个方言做到端到端可运行，但共享骨架同步演进；
- 一份语法超集，方言差异在语义分析阶段门控，不提前分叉文法；
- 共享组件按需抽象：第一个方言需要时实现，第二个方言复用时才一般化；
- 两个方言都先用树遍历解释器跑通 v1，字节码/LLVM 之后作为共享后端实现；
- 第二个方言尽早用薄探针验证隔离，避免共享层被第一个方言的偶然实现污染。

**方言 v1 的完成定义**：规范声明的特性全部可端到端运行，并有正向测试、拒绝测试、
示例与文档；不以“所有后端/优化完成”为标准。

## 路线图

### 阶段 0：共享骨架与动态核心（已完成）

- ANTLR 语法 + Pratt 表达式解析（带源码位置）
- AST、Pass1 名称解析与作用域检查
- 树遍历解释器：函数、闭包、类、继承、元类、`this`/`super`
- 容器字面量、下标、切片、`for`、`elif`、增强赋值、多目标解包
- 运算符重载：`def operator "<sym>"`，一元/二元/比较/成员，内建类型同一套方法表
- 内建函数与 REPL
- 测试重组：`tests/unit/{frontend,runtime}` + `tests/integration`
- 移除不成熟的寄存器字节码原型（见 [OP 0004](proposals/0004-bytecode-vm.md)）

### 阶段 1：`oort-object` v1（当前）

目标：把动态方言做成完整、可演示、可验收的产品。对象模型见
[OP 0007](proposals/0007-oort-object-object-model.md)。

#### P0 — 方言闭环

| 项目 | 说明 |
|------|------|
| 方言契约 | 已完成（2026-11-18）：`#lang oort-object`（默认 + 显式）、`DialectConfig`、按方言构造 Pratt 表、`DialectFeatures` 门控；未知/未实现方言与非首行声明显式报错 |
| 动态对象模型 | 已完成（2026-11-18）：开放字段袋、类体 `var`/`val` 拒绝、实例字段禁止遮蔽方法与类方法、缺失属性诊断、身份相等/哈希；槽仍归 `oort-core` |
| 参数绑定 | 默认参数与关键字参数统一设计，避免后续特批 |
| 运算符重载 | 已完成（2026-11-18）；下标/属性重载另立提案 |
| 表达式/表面积清理 | 已完成（2026-11-18）：优先级、`Bool`、`!` 后缀、形参括号、隐式中缀关闭、半成品拒绝、`break value`、`.` 续行、`//=`、容器显示（[OP 0009](proposals/0009-expression-and-surface-cleanup.md)） |

#### P1 — 运行时能力

| 项目 | 说明 |
|------|------|
| 模块与导入 | 按 [OP 0006](proposals/0006-modules-and-imports.md) 实现加载器、缓存、循环诊断；属于共享骨架 |
| 标准库最小集 | `map`/`filter`/`sorted`/`zip`/`enumerate`，`math`、`string` 模块 |
| 迭代器协议 | 用户对象可用于 `for` |
| 扩展方法 | `def C.f` 在类外定义，按词法作用域生效 |

#### 共享骨架（与方言并行）

| 项目 | 说明 |
|------|------|
| 文法去宿主化 | 删除 `Oort.g4` 的 `@lexer::members`、token 动作与 `IGNORED_NEWLINE` 谓词；新增 token 后处理层处理换行与括号栈（[OP 0008](proposals/0008-lexer-postprocessing-and-repl.md)） |
| REPL 重构 | `ReplSession` + `ConsoleIO`；整缓冲区解析；正确处理 EOF/Ctrl-C；不再修改 ANTLR lexer/parser 内部字段（[OP 0008](proposals/0008-lexer-postprocessing-and-repl.md)） |
| REPL 测试 | 括号/完整性单元测试、transcript 集成测试、子进程 stdin 冒烟测试；终端交互用 `private/repl-smoke.md` 人工检查 |
| 未匹配闭括号 | 词法动作移除后，`}` / `)` 等应走语法诊断，而不是 Python traceback |

#### P2 — 动态方言的打磨

| 项目 | 说明 |
|------|------|
| 字段初始化器 | 可选语法糖；每实例求值，另行提案，不属于槽 |
| 下标/属性访问协议 | `a[b]`、`a.b` 走可重载方法，另立提案 |
| 覆盖率基线 | 核心模块 ≥ 80% 行覆盖；提高阈值前先补测试 |

验收：`docs/spec` 中 `oort-object` 的每个“已实现”条目都有测试；
`test_unsupported.py` 覆盖该方言的全部拒绝项；示例可全部运行。

### 阶段 2：`oort-core` v1

先做**薄探针**，验证方言路由与语义隔离：

- `#lang oort-core`；
- 只支持 `Int` / `Bool` / 函数的最小静态子集；
- 独立的类型检查器，复用 AST、诊断、模块加载、CLI 与测试框架；
- 同一程序在 `oort-object` 下动态运行、在 `oort-core` 下静态检查。

探针通过后，按 [OP 0005](proposals/0005-type-system.md) 实现完整切片：

1. 双向类型检查 + 局部推断
2. 泛型（单态化 + 边界擦除）；类型参数语法采用
   `[out T: Bound]` / `[in T: Bound]`（声明处变型）
3. ADT（`enum`）与 `match`、穷尽性检查
4. `Result[T, E]` / `Option[T]` 与 `?` 传播
5. 静态对象模型与**槽**：固定布局、确定赋值、`val` 只读、初始化顺序
6. 模块级动态/静态边界与 blame

槽变量属于本阶段，不属于 `oort-object`。

### 阶段 3：共享后端

前置：`oort-object` 与 `oort-core` 的 v1 对象模型均已稳定。

- 统一 HIR：把方言语义在进入 HIR 前消化掉；
- 寄存器式字节码 VM（[OP 0004](proposals/0004-bytecode-vm.md)、
  [设计 02](design/02-bytecode-vm-design.md)）；
- 与树遍历解释器做差分测试；
- 用基准证明收益，再考虑 LLVM。

禁止为每个方言复制一套字节码后端。

### 阶段 4：`oort-systems` / `oort-meta` 与 DSL 开关（按需）

- DSL 是正交维度：`oort-script` / `oort-builder` 的接收者 lambda、`@DslMarker`、
  属性系统、`infix`、按名参数、字符串插值器，按 [OP 0002](proposals/0002-dsl-support.md)
  在 `oort-object` / `oort-core` 之上开关，不单独建管线；
- `oort-systems` 依赖内存模型、ABI 与无 GC 对象表示；
- `oort-meta` 依赖稳定的 AST、类型表示与模块边界，最后做。

### 阶段 5：静态后端与 Rust 迁移（远期）

- LLVM IR（llvmlite 原型，Rust/inkwell 生产）
- 静态模块单态化与 GC/ARC 选择
- Rust 重写关键路径（VM、编译器）

## 当前状态总览

- **前端（文法、解析、AST）**：基本完成。核心语法、容器字面量、类/函数定义、
  切片与 `elif` 均已支持；Pratt 运算符表完整。文法仍含 Python lexer 动作
  （括号计数与换行谓词），计划按 OP 0008 移到 token 后处理层。
- **语义分析**：覆盖名称解析、作用域、`this`/`super`、控制流位置检查；
  并负责显式拒绝未实现特性。类型检查尚未开始。
- **解释器**：动态核心基本可用，函数、闭包、类、继承、元类、容器、循环都有测试。
  运算符重载已闭环（用户类与内建类型共用方法表）；`break value`、行首 `.`
  方法链续行、`//=` 已实现；默认/关键字参数、用户迭代器、下标/属性重载仍未实现。
- **动态对象模型**：开放字段袋、类体 `var`/`val` 拒绝、方法遮蔽检查、缺失属性
  诊断、身份相等/哈希均已完成（[OP 0007](proposals/0007-oort-object-object-model.md)）。
- **方言**：`#lang oort-object` 已实现（缺省 + 显式）；其他方言仍为占位。
- **标准库**：只有最小内建函数；集合高阶函数、`math`/`string` 等模块等待模块系统。
- **REPL**：支持多行输入、续行与错误恢复，并有 transcript 集成测试；
  但实现依赖 ANTLR lexer/parser 内部字段，EOF/Ctrl-C 行为未定义，
  重构与分层测试见 OP 0008。
- **测试**：单元测试与集成测试分目录组织，覆盖全部已实现特性与拒绝清单；
  核心代码行覆盖率约 87%。
- **类型系统**：仅解析类型标注，不检查、不推导；属于 `oort-core`，设计见 OP 0005。
- **模块/导入**：语法可解析，语义阶段显式报错；设计见 OP 0006。
- **宏 / `comptime`**：未开始，排在类型系统与模块之后。
- **字节码 VM**：旧原型已移除；在 `oort-object` 与 `oort-core` v1 后作为共享后端实现。

## 决策索引

| 决策 | 选择 | 参考 |
|------|------|------|
| 开发模型 | 共享骨架 + 方言垂直切片 + 共享后端 | [OP 0001 §5](proposals/0001-feature-layers-and-dialects.md) |
| 词法/REPL | 文法去宿主化；NEWLINE 由 token 后处理层过滤；REPL 用 `ReplSession` | [OP 0008](proposals/0008-lexer-postprocessing-and-repl.md) |
| 方言默认值 | 缺省 `oort-object`，允许显式 `#lang`；其他方言必须显式声明 | [OP 0001](proposals/0001-feature-layers-and-dialects.md) |
| `oort-object` 对象模型 | 开放字段袋；拒绝类体 `var`/`val`；禁止方法遮蔽 | [OP 0007](proposals/0007-oort-object-object-model.md) |
| 槽变量归属 | `oort-core` 静态对象模型，与类型系统一起设计 | [OP 0007](proposals/0007-oort-object-object-model.md) / [OP 0005](proposals/0005-type-system.md) |
| 执行后端（当前） | 树遍历解释器 | [实现笔记 03](implementation/03-interpreter.md) |
| 执行后端（目标） | 寄存器式字节码 VM（两个方言 v1 后） | [设计 02](design/02-bytecode-vm-design.md) / [OP 0004](proposals/0004-bytecode-vm.md) |
| 值表示（目标） | Tagged Pointer + 整数层级 | [设计 01](design/01-runtime-value-representation.md) |
| 闭包模型 | 环境链（当前）；Upvalue（VM） | [设计 02](design/02-bytecode-vm-design.md) |
| 泛型策略 | 内部单态化，边界擦除 | [OP 0005](proposals/0005-type-system.md) |
| 元类 | 扁平化、共享、`::` 语法 | [实现笔记 04](implementation/04-class-system.md) |
| `this` 绑定 | 方法内词法绑定 | [实现笔记 04](implementation/04-class-system.md) |
| 运算符重载 | `def operator "<sym>"`，内建类型同一套方法表 | [OP 0002](proposals/0002-dsl-support.md) |
| 表达式优先级 | 位运算高于比较；比较非结合 | [OP 0009](proposals/0009-expression-and-surface-cleanup.md) |
| `Bool` 语义 | 不是 `Int` 子类型；只支持 `==` / `!=` | [OP 0009](proposals/0009-expression-and-surface-cleanup.md) |
| 形参语法 | 所有形参列表必须带括号 | [OP 0009](proposals/0009-expression-and-surface-cleanup.md) |
| 语法表面积 | 关闭隐式中缀；拒绝 `def C.f` / `class A.B` / 显式 `super(...)` | [OP 0009](proposals/0009-expression-and-surface-cleanup.md) |
| Token 职责 | `:` 标签/体、`=` 绑定/命名实参、`->` 返回类型、`=>` 延迟/映射 | [OP 0010](proposals/0010-token-responsibilities-and-anonymous-parameters.md) |
| 小型 lambda | `$0` / `$1` 仅用于无显式参数列表的 lambda | [OP 0010](proposals/0010-token-responsibilities-and-anonymous-parameters.md) |
| 导入语义 | 急切，模块级缓存 | [OP 0006](proposals/0006-modules-and-imports.md) |
| 错误处理 | `Result`/`Option`（`oort-core`） | [OP 0005](proposals/0005-type-system.md) |
| 多线程 / ABI | 暂无稳定 ABI；优先 C FFI | [设计 07](design/07-concurrency-abi-design.md) |
| 宏系统 | Token Stream + AST + `comptime`（最后） | [设计 05](design/05-macro-system-design.md) |
