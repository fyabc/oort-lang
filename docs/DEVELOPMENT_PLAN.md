# Oort 开发计划

## 定位

Oort 是用于学习编译原理与编程语言设计的玩具语言。Python 原型优先验证**语义**；
性能与工程化（字节码、LLVM、Rust）在语义稳定后再做。

设计约束（所有阶段适用）：

1. 特性正交，不写“类型特判”；
2. 未实现的语法显式报错，不保留半成品；
3. 元编程（宏、`comptime`）最后做；
4. 每个特性先有规范与测试，再有优化。

## 路线图

### 阶段 0：动态核心（已完成）

- ANTLR 语法 + Pratt 表达式解析（带源码位置）
- AST、Pass1 名称解析与作用域检查
- 树遍历解释器：函数、闭包、类、继承、元类、`this`/`super`
- 容器字面量、下标、切片、`for`、`elif`、增强赋值、多目标解包
- 内建函数与 REPL
- 测试重组：`tests/unit/{frontend,runtime}` + `tests/integration`
- 移除不成熟的寄存器字节码原型（见 [OP 0004](proposals/0004-bytecode-vm.md)）

### 阶段 1：核心语义收尾（当前）

目标：让“已声明支持”的动态特性真正闭环，规范与实现一致。

| 项目 | 说明 | 优先级 |
|------|------|--------|
| 运算符重载调度 | 二元/一元/下标/比较走 `operator "..."` / `__op_*__` 方法，替换直接使用 Python 运算 | P0 |
| 类槽变量 | `class C { var x }` 定义实例字段，`this.x` 访问；与动态字段并存规则 | P0 |
| 扩展方法 | `def C.f` 在类外定义，按词法作用域生效 | P1 |
| 默认/关键字参数 | 与函数签名统一，参数绑定算法一次设计到位 | P1 |
| 迭代器协议 | `for` 支持用户对象（`__iter__`/`__next__` 或设计笔记 06 的双返回协议） | P1 |
| 标准库最小集 | `map`/`filter`/`sorted`/`zip`/`enumerate`，`math`/`string` 模块（依赖模块系统） | P1 |
| REPL 集成测试 | 多行输入、续行、错误恢复 | P2 |
| 覆盖率基线 | 目标：核心模块 ≥ 80% 行覆盖 | P2 |

验收：`docs/spec` 中每个“已实现”条目都有测试；`test_unsupported.py` 覆盖全部拒绝项。

### 阶段 2：模块与导入

依据 [OP 0006](proposals/0006-modules-and-imports.md)：

- 模块加载器、缓存、路径解析
- 急切导入与初始化顺序
- 循环依赖诊断
- 标准库 prelude
- 移除 `import` 的拒绝诊断

### 阶段 3：类型系统与数据建模

依据 [OP 0005](proposals/0005-type-system.md)：

1. 双向类型检查 + 局部推断（动态模块不受影响）
2. 泛型（单态化 + 边界擦除）
3. ADT（`enum`）与 `match`、穷尽性检查
4. `Result[T, E]` / `Option[T]` 与 `?` 传播
5. 模块级动态/静态边界与 blame
6. Trait/接口与运算符重载对接

### 阶段 4：方言与 DSL

依据 [OP 0001](proposals/0001-feature-layers-and-dialects.md)、
[OP 0002](proposals/0002-dsl-support.md)：

1. `#lang` 模块级方言控制与 Pratt 运算符表配置
2. 属性系统 `@[...]`
3. 接收者 lambda + `@DslMarker`
4. 运算符声明、`infix`、按名参数、字符串插值器
5. 结果构建器（可选）

### 阶段 5：字节码 VM

依据 [OP 0004](proposals/0004-bytecode-vm.md) 与
[设计笔记 02](design/02-bytecode-vm-design.md)：

- 前置：显式失败约束、语义测试、对象模型统一、行号/异常表
- 寄存器式 ISA、upvalue 闭包、端到端测试
- 与解释器结果对拍
- 基准证明收益

### 阶段 6：静态后端与 Rust 迁移（远期）

- LLVM IR（llvmlite 原型，Rust/inkwell 生产）
- 静态模块单态化与 GC/ARC 选择
- Rust 重写关键路径（VM、编译器）

## 当前状态总览

```
前端 (Grammar/Parser/AST)        ████████████████████░  95%
语义分析 (Pass1)                 ████████████████░░░░░  80%
AST 解释器                       ██████████████████░░░  90%
标准库                           ██████░░░░░░░░░░░░░░░  30%
REPL                             █████████████████░░░░  85%
测试                             ████████████████░░░░░  80%
类型系统                         ░░░░░░░░░░░░░░░░░░░░░   0% (仅解析标注)
模块/导入                        ░░░░░░░░░░░░░░░░░░░░░   0% (语法已解析)
宏 / comptime                    ░░░░░░░░░░░░░░░░░░░░░   0%
字节码 VM                        ░░░░░░░░░░░░░░░░░░░░░   0% (旧原型已移除)
```

## 决策索引

| 决策 | 选择 | 参考 |
|------|------|------|
| 执行后端（当前） | 树遍历解释器 | [实现笔记 03](implementation/03-interpreter.md) |
| 执行后端（目标） | 寄存器式字节码 VM | [设计 02](design/02-bytecode-vm-design.md) / [OP 0004](proposals/0004-bytecode-vm.md) |
| 值表示（目标） | Tagged Pointer + 整数层级 | [设计 01](design/01-runtime-value-representation.md) |
| 闭包模型 | 环境链（当前）；Upvalue（VM） | [设计 02](design/02-bytecode-vm-design.md) |
| 泛型策略 | 内部单态化，边界擦除 | [OP 0005](proposals/0005-type-system.md) |
| 元类 | 扁平化、共享、`::` 语法 | [实现笔记 04](implementation/04-class-system.md) |
| `this` 绑定 | 方法内词法绑定 | [实现笔记 04](implementation/04-class-system.md) |
| 运算符重载 | Trait / `operator "..."` 显式 | [OP 0002](proposals/0002-dsl-support.md) |
| 导入语义 | 急切，模块级缓存 | [OP 0006](proposals/0006-modules-and-imports.md) |
| 错误处理 | `Result`/`Option`（静态方言） | [OP 0005](proposals/0005-type-system.md) |
| 多线程 / ABI | 暂无稳定 ABI；优先 C FFI | [设计 07](design/07-concurrency-abi-design.md) |
| 宏系统 | Token Stream + AST + `comptime`（最后） | [设计 05](design/05-macro-system-design.md) |
