# Oort 语言规范

本目录是 Oort 语言的**规范性文档**：描述当前实现实际接受的语法与语义。
与设计笔记、提案不同，规范中的内容应当与 `src/oort_lang` 的行为一致；
任何偏离都应被视为 bug。

> 状态：Oort 仍在早期演进（0.2.x）。规范只覆盖**已实现**的特性；
> 尚未实现但语法可解析的特性在 [06-conformance.md](06-conformance.md) 中列明，
> 并由编译器显式拒绝。
>
> 方言契约（首行 `#lang`）已落地：缺省 `oort-object`，`oort-core` 已注册但
> 尚未实现。当前规范描述的是 `oort-object` 的参考语义；后续拆分共享的
> 词法/语法部分与每方言的语义规范。开发模型见
> [OP 0001 §5](../proposals/0001-feature-layers-and-dialects.md#5-开发模型共享骨架--方言垂直切片2026-11-18-已接受)。

## 阅读顺序

| 文档 | 内容 |
|------|------|
| [01-lexical.md](01-lexical.md) | 源文件、词法、字面量、关键字、运算符表 |
| [02-expressions.md](02-expressions.md) | 表达式、容器、下标/切片、调用 |
| [03-statements.md](03-statements.md) | 声明、赋值、控制流 |
| [04-functions.md](04-functions.md) | 函数、lambda、闭包、尾随闭包 |
| [05-classes.md](05-classes.md) | 类、继承、元类、`this` / `super` |
| [07-modules.md](07-modules.md) | 模块身份、导入语法、路径解析、缓存与循环诊断 |
| [06-conformance.md](06-conformance.md) | 实现状态矩阵与诊断规则 |

## 术语

- **动态方言**：默认的 `oort-object`，树遍历执行（`oort -t eval`），不做类型检查。
- **语义分析**：`Pass1Analyzer`，负责名称解析、作用域检查和显式拒绝未实现特性。
- **规范错误**：本规范列出的行为；测试套件（`tests/`）覆盖主要条目。
