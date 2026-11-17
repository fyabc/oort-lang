# Oort 提案（Oort Proposals）

本目录采用类似 Python PEP / Rust RFC 的流程，管理语言、语义与工具链的
**非平凡变更**。目标是避免 C++ 式“特性层层打补丁”：

- 每个特性在实现前先写清楚动机、边界与替代方案；
- 特性之间保持正交，不允许“特例 + 隐式例外”；
- 元编程类特性（宏、编译期计算）排在使用期语义稳定之后。

## 状态

| 状态 | 含义 |
|------|------|
| Draft | 讨论中，尚未定稿 |
| Proposed | 已提交，等待实现/评审 |
| Accepted | 已接受，正在或等待实现 |
| Implemented | 已实现，并由 [语言规范](../spec/index.md) 与测试覆盖 |
| Rejected | 不采纳（保留记录，避免重复讨论） |
| Withdrawn | 作者撤回 |

## 提案列表

| 编号 | 标题 | 状态 |
|------|------|------|
| [0001](0001-feature-layers-and-dialects.md) | 特性分层与语言方言（防止 C++ 化） | Accepted |
| [0002](0002-dsl-support.md) | 嵌入式 DSL 支持 | Proposed |
| [0003](0003-grammar-cleanup.md) | 文法清理与语义收紧 | Implemented |
| [0004](0004-bytecode-vm.md) | 字节码虚拟机（重新实现） | Draft |
| [0005](0005-type-system.md) | 类型系统、泛型、ADT 与模式匹配 | Draft |
| [0006](0006-modules-and-imports.md) | 模块与导入系统 | Draft |
| [0007](0007-oort-object-object-model.md) | `oort-object` 动态对象模型 | Proposed |
| [0008](0008-lexer-postprocessing-and-repl.md) | 词法后处理层与 REPL 重构 | Proposed |

## 流程

1. 复制 [0000-template.md](0000-template.md)，分配下一个编号。
2. 在提案中写清：动机、设计、语义边界、与现有特性的正交性、替代方案、
   向后兼容与测试计划。
3. 更新本页的提案列表与状态。
4. 实现时：
   - 同步更新 `docs/spec/`；
   - 增加或修改 `tests/`；
   - 若提案改变了未实现特性的拒绝清单，更新
     [06-conformance.md](../spec/06-conformance.md)。
5. 实现完成后把状态改为 `Implemented`。

## 决策记录

| 日期 | 决策 | 提案 |
|------|------|------|
| 2026-11-18 | 文法清理：`USER_OP` 去掉 `.`/`:`/`@`，删除死 token，`elif`/`else` 对称化 | [OP 0003](0003-grammar-cleanup.md)（Implemented） |
| 2026-11-18 | 移除不成熟的寄存器字节码原型；重新实现需满足显式失败与端到端测试等前置条件 | [OP 0004](0004-bytecode-vm.md) |
| 2026-11-18 | 类型参数采用声明处变型：`[out T: Bound]` / `[in T: Bound]`，上界用 `T: Bound` | [OP 0005 §3.1](0005-type-system.md#31-类型参数语法与变型已接受) |
| 2026-11-18 | 运算符方法统一用 `def operator "<sym>"` 字符串命名；内建类型与用户类共用 `OortType.operators` 调度；`!=`/`!in` 默认取反 | [OP 0002 §3](0002-dsl-support.md#3-运算符声明) |
| 2026-11-18 | 采用“共享骨架 + 方言垂直切片 + 共享后端”的开发模型；先完成 `oort-object` v1，再以薄 `oort-core` 探针验证隔离 | [OP 0001 §5](0001-feature-layers-and-dialects.md#5-开发模型共享骨架--方言垂直切片2026-11-18-已接受) |
| 2026-11-18 | `oort-object` 使用开放字段袋、拒绝类体 `var`/`val`、禁止实例字段遮蔽类方法；槽归入 `oort-core` 静态对象模型 | [OP 0007](0007-oort-object-object-model.md) |
| 2026-11-18 | `Oort.g4` 去除宿主语言动作，换行/括号交给 token 后处理层；REPL 重构为 `ReplSession` 并补分层测试 | [OP 0008](0008-lexer-postprocessing-and-repl.md) |

## 设计原则（所有提案必须满足）

- **正交性**：特性可自由组合，不为特定类型/场景写特判。
- **显式优于隐式**：隐式行为（自动转换、隐式捕获、隐式本地化）必须可关闭或有明确理由。
- **拒绝半成品**：未实现的语法要么移除，要么在语义分析阶段显式报错。
- **先语义后性能**：动态语义稳定前不引入字节码/JIT 复杂度。
- **元编程最后**：宏与编译期计算依赖稳定的 AST、作用域与类型模型。
