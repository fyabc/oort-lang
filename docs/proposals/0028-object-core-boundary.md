# OP 0028: object → core 跨方言边界

- **状态**：Proposed（B1 原型已实现，边界规范待定稿）
- **作者**：Oort 设计讨论
- **创建日期**：2026-11-23
- **相关**：[OP 0001](0001-feature-layers-and-dialects.md)、[OP 0006](0006-modules-and-imports.md)、[OP 0017](0017-oort-core-thin-probe.md)、[design 17](../design/17-boundary-ffi.md)

## 摘要

允许 `oort-object` 模块导入并调用 `oort-core` 库，同时继续拒绝
`oort-core` 导入或回调 `oort-object`。边界负责类型守卫、值复制、ADT
名义身份、错误归责和模块执行；它不是 C FFI，也不提供回调或类/接口边界。

## 动机

- 动态脚本适合 agent 编排和快速迭代；静态 core 适合工具、数值和库；
- 当前规范要求所有跨方言导入都拒绝，导致“脚本 + 静态库”无法组合；
- B1 原型已经验证了 object→core 的可用路径，但代码行为与 spec 07/11
  仍冲突；需要把行为固化为语言契约。

## 设计

### 语法与方向

```oort
# main.ort: oort-object
from "./mathlib" import add
import "./mathlib"

print(add(1, 2))
print(mathlib.add(3, 4))
```

- 允许 object → core；
- 继续拒绝 core → object；
- 允许 core 模块继续导入其他 core 模块（P1 linker）；
- 跨方言失败在导入/编译期诊断，不退化成运行时猜测。

### 值映射

| 动态值 | core 类型 | 规则 |
|---|---|---|
| `Int`/`Float`/`Bool` | 对应标量 | 运行时守卫 |
| `String` | `String` | 不可变，可共享 |
| `List`/`Tuple`/`Set`/`Dict` | 对应容器 | 递归守卫 + 边界复制 |
| ADT | 对应 ADT | 按 `(origin, name, args)` 守卫；容器复制 |
| `null` | `Unit` | core→动态映射为 null；反向传 null 到非 Unit 报错 |
| 函数值 | — | core 导出函数可包装为动态 callable；动态函数不能传入 core |
| 类/接口实例 | — | 初始拒绝 |

### 错误与 blame

- 参数守卫失败归责动态调用方，包含 core 函数名、参数位置、期望/实际类型；
- core 内部错误按 core 源码位置传播；
- 不允许隐式数值转换；
- 错误信息不得泄漏宿主路径或对象。

### 回调与类

第一阶段明确不支持：

- core 接收动态 lambda/闭包；
- core 调用 object；
- 类/接口实例跨边界；
- 跨方言共享可变对象图。

替代 API 应使用：

- 集合批处理函数；
- core 导出的 iterator/handle，由动态侧反复调用 `next`/`step`；
- 后续 `Dynamic`/契约类型设计。

### 模块与初始化

- object 导入 core 模块时编译其 checked AST 为 typed 字节码；
- core 模块及其 core 依赖按模块初始化顺序执行；
- 重复导入只执行一次；
- core 模块顶层副作用仍受 typed 子集限制（当前主要允许函数定义）；
- 导出函数在模块初始化后包装为动态 callable。

## 正交性检查

- **类型系统**：使用 core 已检查签名；动态侧不做静态类型推断。
- **对象模型**：类/接口暂不进入边界，避免对象图/生命周期问题。
- **函数**：动态函数不能进入 core，避免回调生命周期。
- **模块**：复用 OP 0006 的路径/缓存/初始化规则；仅方向不同。
- **性能**：B1 不设门禁；B3 再评估 Rust typed 边界和复制成本。

## 替代方案

1. **继续双向拒绝**：实现简单，但失去脚本调用 core 库的核心价值。
2. **双向立即开放**：需要 `Dynamic`、契约、回调生命周期和 blame，范围过大。
3. **只通过 C ABI/JSON**：失去共享 ADT/错误/模块语义，边界更重。
4. **统一动态/静态运行时**：长期方向，但不是 B1 的语义原型。

## 向后兼容

- 旧行为“object 导入 core 一律拒绝”被改变；
- core 导入 object 仍拒绝；
- 现有 object/object、core/core 导入不变；
- spec 07/11/06 需要同步修改；
- 这是**方向性新能力**，不是默认关闭的方言开关。

## 实现计划

1. **B1（已完成原型）**：Python typed VM、守卫、容器/ADT 复制、模块缓存。
2. **B2**：库覆盖（集合/ADT/类边界、导出 API 约定）。
3. **B3**：Rust typed 边界、调用开销/复制预算。
4. **B4**：C FFI profile（独立规范）。

## 未解决问题

- 类/接口实例的边界表示（opaque handle、访问器、包装类）；
- 动态函数/回调何时开放；
- 容器零拷贝/COW 与统一 GC 的关系；
- 导出函数值、方法引用、ADT 构造器的动态侧表示；
- core 模块顶层副作用与初始化失败的动态错误映射。
