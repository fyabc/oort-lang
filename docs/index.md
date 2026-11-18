# Oort 语言文档

欢迎来到 Oort 编程语言的文档中心。

## 快速入门

- [安装与使用](../README.md#安装与使用) — 安装 Oort 并运行第一个程序
- [示例代码](../examples/) — 通过示例学习 Oort 语法
- [VSCode 插件](../editors/vscode/README.md) — `.ort` 语法高亮与本地安装

## 语言规范

**规范**描述当前实现实际接受的行为，是语言使用者的主要参考：

- [规范索引](spec/index.md)
- [词法结构](spec/01-lexical.md) — 字面量、关键字、运算符表
- [表达式](spec/02-expressions.md) — 运算符、容器、下标与切片、调用
- [语句](spec/03-statements.md) — 声明、赋值、控制流
- [函数](spec/04-functions.md) — `def`、lambda、闭包、尾随闭包
- [类](spec/05-classes.md) — 继承、元类、`this` / `super`
- [实现状态矩阵](spec/06-conformance.md) — 已实现 / 被拒绝 / 计划中的特性

## 提案

Oort 的语言变更采用类 PEP/RFC 流程：

- [提案索引与流程](proposals/README.md)
- [OP 0001: 特性分层与语言方言](proposals/0001-feature-layers-and-dialects.md)
- [OP 0002: 嵌入式 DSL 支持](proposals/0002-dsl-support.md)
- [OP 0003: 文法清理与语义收紧](proposals/0003-grammar-cleanup.md)（已实现）
- [OP 0004: 字节码虚拟机](proposals/0004-bytecode-vm.md)
- [OP 0005: 类型系统、泛型、ADT 与模式匹配](proposals/0005-type-system.md)
- [OP 0006: 模块与导入系统](proposals/0006-modules-and-imports.md)
- [OP 0007: `oort-object` 动态对象模型](proposals/0007-oort-object-object-model.md)（已实现）
- [OP 0008: 词法后处理层与 REPL 重构](proposals/0008-lexer-postprocessing-and-repl.md)
- [OP 0009: 表达式语义与语法表面积清理](proposals/0009-expression-and-surface-cleanup.md)（已实现）
- [OP 0010: Token 职责与匿名 lambda 参数](proposals/0010-token-responsibilities-and-anonymous-parameters.md)（已实现）
- [OP 0011: 参数绑定](proposals/0011-parameter-binding.md)（已实现）

## 实现与设计

- [实现笔记](implementation/index.md) — 语法、解析器、解释器、类系统
- [设计知识库](design/00-INDEX.md) — 调研与备选方案（非规范）
- [开发计划](DEVELOPMENT_PLAN.md) — 里程碑与当前状态

## 开发

- [测试](../tests/) — 单元测试与集成测试的使用方式见 `tests/README.md`
- [基准测试](../benchmarks/) — AST 解释器性能基线
