# Oort Programming Language

[![CI](https://github.com/fyabc/oort-lang.py/actions/workflows/ci.yml/badge.svg)](https://github.com/fyabc/oort-lang.py/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 简介

Oort 是一门用于**编译原理与编程语言设计学习**的玩具语言。Python 实现目前作为原型，
未来可能迁移到 Rust。

Oort 的命名来自天文学中的“[奥尔特云](https://en.wikipedia.org/wiki/Oort_cloud)”，
相关工具链的命名也会使用天文学词汇。

## 当前状态

当前只有一条执行路径：**树遍历解释器**（动态类型）。语法前端（ANTLR + Pratt）
解析的语言超集比运行时更大；**未实现的特性会在语义分析阶段显式报错**，不会静默
产生错误结果。完整的实现/拒绝清单见
[规范：实现状态](docs/spec/06-conformance.md)。

开发以**方言垂直切片**为主轴：先完成 `oort-object` 动态方言的 v1，再以薄探针
验证并实现 `oort-core`；共享字节码后端在两个方言 v1 之后。详见
[开发计划](docs/DEVELOPMENT_PLAN.md) 与 [OP 0001 §5](docs/proposals/0001-feature-layers-and-dialects.md#5-开发模型共享骨架--方言垂直切片2026-11-18-已接受)。

### 已实现

- 类 C 语法；换行分隔语句，括号内可自由换行
- 整数/浮点/字符串/布尔/`null`
- List、Tuple、Dict、Set 字面量与下标、切片
- 一等函数、`do` lambda、闭包、尾随闭包调用
- `if` / `elif` / `else`、`while`、`for ... in`（含解包）、`break expr`
- `var` / `val`、多目标声明与元组解包、增强赋值（含 `//=`）
- 类、方法、类方法、多重继承（C3 MRO）、元类、`this` / `super`
- 运算符重载：`def operator "+"(other)` 等方法，内建类型使用同一套调度
- 行首 `.` 方法链续行；`Bool` 与 `Int` 语义分离
- 内建：`print`、`clock`、`type`、`super`、`len`、`range`、`str`、`repr`、
  `int`、`float`、`bool`
- REPL（多行输入）

### 待实现（见 proposals）

- 模块与导入系统 — [OP 0006](docs/proposals/0006-modules-and-imports.md)
- 静态类型、泛型、ADT、模式匹配 — [OP 0005](docs/proposals/0005-type-system.md)
- 自定义运算符声明与优先级 — [OP 0002](docs/proposals/0002-dsl-support.md)
- 宏系统与 `comptime` — [设计笔记](docs/design/05-macro-system-design.md)
- 字节码 VM 与 LLVM 后端 — [OP 0004](docs/proposals/0004-bytecode-vm.md)
- 语言方言（core / object / systems） — [OP 0001](docs/proposals/0001-feature-layers-and-dialects.md)

## 样例

各种样例参见 [examples](./examples)。

## 文档

- [文档中心](docs/index.md)
- [语言规范](docs/spec/index.md) — 当前实现的行为
- [提案系统](docs/proposals/README.md) — 语言演进流程
- [实现笔记](docs/implementation/index.md)
- [设计知识库](docs/design/00-INDEX.md)
- [开发计划](docs/DEVELOPMENT_PLAN.md)

## 安装与使用

### 使用 uv（推荐）

```bash
pip install uv
uv sync

# 运行文件（默认执行）
oort test.ort

# 执行一行代码
oort -c "print(42)"

# 启动 REPL
oort

# 只打印 AST / 带元数据的 AST
oort test.ort -t ast
oort test.ort -t astm
```

### 使用 pip

```bash
pip install .

oort test.ort
```

### VSCode 语法高亮

仓库内置 `.ort` 高亮插件（TextMate，含文件图标，无需 Marketplace）：

```bash
cd editors/vscode
npm install
npm run package
code --install-extension oort-lang-0.1.0.vsix
```

安装后重载窗口即可生效。开发方式、scope 说明与已知限制见
[editors/vscode/README.md](editors/vscode/README.md)。

## 开发

```bash
uv sync --extra dev
pre-commit install

# 测试
uv run pytest tests/

# 基准测试
uv run pytest benchmarks/

# 代码质量
uv run ruff check src/ tests/ benchmarks/ scripts/
uv run ruff format src/ tests/ benchmarks/ scripts/
uv run mypy src/
```

### 重新生成语法

需要 Java（17+）。语法文件位于 `grammars/Oort.g4`：

```bash
uv sync --extra build-grammar
python scripts/build_grammar.py
```

## 目录结构

```
src/oort_lang/
├── grammar/          # ANTLR 生成的词法/语法分析器（勿手改）
├── ast/              # AST 节点与 visitor
├── frontend/         # AST 构建（Pratt）、语义分析、错误报告
├── ast_interpreter/  # 树遍历解释器、对象模型、内建
├── top_level/        # 编译器入口与 REPL
├── support/          # 参数、源码位置、日志
└── exceptions/
grammars/Oort.g4      # 语法定义
tests/                # 单元测试与集成测试
examples/             # 示例程序
editors/vscode/       # VSCode 语法高亮插件
docs/                 # 规范、提案、实现笔记、设计调研
benchmarks/           # 性能基线
```

## 相关工具

- [ANTLR 4](https://www.antlr.org/) — 词法与语法分析器生成
- [uv](https://docs.astral.sh/uv/) — 依赖与虚拟环境管理
- [ruff](https://docs.astral.sh/ruff/) / [mypy](https://mypy-lang.org/) — 代码质量

## 参与贡献

- [CONTRIBUTING.md](CONTRIBUTING.md) — 开发环境、测试与提案流程
- [CHANGELOG.md](CHANGELOG.md) — 变更记录
- [SECURITY.md](SECURITY.md) — 漏洞报告方式

语言变更请先阅读 [提案流程](docs/proposals/README.md)；未实现的功能会被显式拒绝，
不会静默产生错误结果。
