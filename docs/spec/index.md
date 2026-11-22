# Oort 语言规范

本目录是 Oort 语言的**规范性文档**：描述当前实现实际接受的语法与语义。
与设计笔记、提案不同，规范中的内容应当与 `src/oort_lang` 的行为一致；
任何偏离都应被视为 bug。

> 状态：Oort 仍在早期演进（0.3.x）。规范只覆盖**已实现**的特性；
> 尚未实现但语法可解析的特性在 [06-conformance.md](06-conformance.md) 中列明，
> 并由编译器显式拒绝。
>
> 方言契约（首行 `#lang`）已落地：缺省 `oort-object`；`oort-core` 已有
> **薄探针**（Int/Float/Bool/String/集合/循环/静态类/函数与独立类型检查器），规范见
> [11-core-probe.md](11-core-probe.md)。其余章节描述 `oort-object` 的参考语义；
> 开发模型见 [OP 0001 §5](../proposals/0001-feature-layers-and-dialects.md#5-开发模型共享骨架--方言垂直切片2026-11-18-已接受)。

## 阅读顺序

| 文档 | 内容 |
|------|------|
| [01-lexical.md](01-lexical.md) | 源文件、词法、字面量、关键字、运算符表 |
| [02-expressions.md](02-expressions.md) | 表达式、容器、下标/切片、调用 |
| [03-statements.md](03-statements.md) | 声明、赋值、控制流 |
| [04-functions.md](04-functions.md) | 函数、lambda、闭包、尾随闭包 |
| [05-classes.md](05-classes.md) | 类、继承、元类、`this` / `super` |
| [07-modules.md](07-modules.md) | 模块身份、导入语法、路径解析、缓存与循环诊断 |
| [08-stdlib.md](08-stdlib.md) | 集合助手、`math` / `string` 原生模块 |
| [09-iterators.md](09-iterators.md) | `__iter__` 协议、流式 `for`、内置迭代器 |
| [10-extensions.md](10-extensions.md) | 扩展方法/运算符、作用域、导入、`super` |
| [11-core-probe.md](11-core-probe.md) | `oort-core` 薄探针：Int/Float/Bool/String、集合/循环、静态类/槽、函数、Unit、单态/泛型 ADT、内建 `Option`/`Result`、完整模式匹配、拒绝清单 |
| [12-hir-bytecode-vm.md](12-hir-bytecode-vm.md) | 共享后端：HIR、32 位字节码编码、寄存器 VM 语义与调用约定、显式拒绝 |
| [13-bytecode-serialization.md](13-bytecode-serialization.md) | `.obc` 字节码文件格式：头/布局/tagged 常量池 |
| [06-conformance.md](06-conformance.md) | 实现状态矩阵与诊断规则 |

## 术语

- **动态方言**：默认的 `oort-object`，不做类型检查。文件/`-c` 默认经寄存器 VM
  执行（`-t vm`，见 [12](12-hir-bytecode-vm.md)），`-t eval` 树遍历为回退。
- **静态方言**：`oort-core`，当前只实现薄探针子集；类型标注在 `oort-core` 中检查。
- **语义分析**：`Pass1Analyzer` 负责名称解析、作用域检查和显式拒绝未实现特性；
  `oort-core` 还运行独立的 `CoreTypeChecker`。
- **规范错误**：本规范列出的行为；测试套件（`tests/`）覆盖主要条目。
