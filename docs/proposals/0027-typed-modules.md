# OP 0027: `oort-core` typed modules 与模块 ABI

- **状态**：Draft（P1c-1 已实现）
- **作者**：Oort 设计讨论
- **创建日期**：2026-11-23
- **相关**：[OP 0006](0006-modules-and-imports.md)、[OP 0017](0017-oort-core-thin-probe.md)、[design 18](../design/18-typed-adt.md)、[design 19](../design/19-typed-module-abi.md)

## 摘要

为 `oort-core` 定义真正的 typed module：模块身份、导出/导入表、类型/ADT/
构造器导入、初始化顺序和 ABI 版本。P1c 的目标是把当前“编译期拍平”升级为
可分离编译、可校验、可缓存的模块 artifact + load-time linker。

## 动机

当前 typed 路径的模块支持是闭世界拍平：

- 每个模块 lowering 后直接合并函数/ADT；
- 没有模块 import/export 表；
- 没有真正的 module ID/ABI；
- 不能独立编译、缓存、版本检查；
- 函数名冲突只能拒绝，namespace 信息在 lowering 前被消解。

这适合 P1a/P1b 原型，但不是长期模块契约。

## 设计

### 1. 模块身份

- 一个 core 模块编译为一个 typed module artifact；
- `module_id` 使用相对入口/模块根的 POSIX 路径，例如 `lib`、`math`、
  `collections/list`；
- artifact 不包含绝对宿主路径；
- 后续 package manager 再升级为 `package::module`。

### 2. 导入语法

```oort
from "./lib" import add, paint
import "./math" as math
import "./collections/list"
```

- `from` 导入函数/构造器/类型（类型仍需显式规则）；
- namespace import 绑定模块名；
- 导入名与本地名冲突要在编译期诊断；
- 重导出规则由 OP 0006 扩展，不在 P1c 临时定义。

### 3. 导出/导入表

artifact 至少记录：

- 函数导出：name、symbol、签名/ABI hash；
- ADT 导出：name、类型参数、构造器、payload 模板；
- 构造器导出：module + ADT + ctor；
- 类型导出：type-only 符号；
- import 表：module_id、kind、name、期望签名/hash；
- ABI/version。

模块之间使用**符号名 + module_id**，不直接依赖模块内数字 ID。

### 4. 初始化与循环

- 依赖模块先初始化，依赖者后初始化；
- 每个模块 main 只执行一次；
- 循环 import 首版显式拒绝，诊断包含环链；
- 顶层副作用仍需限制；后续再与动态模块语义对齐；
- 导出函数在初始化后可用；模块内部调用不依赖初始化完成。

### 5. ABI 与版本

- kind=1 提升到 v8（artifact 带 module/export/import 与构造器表）；
- 模块记录 ABI/version；loader 校验；
- 旧 v6 文件不被 artifact reader 静默接受；
- 不承诺跨大版本二进制兼容；先做显式版本拒绝。

### 6. Loader / linker

- Python loader 读取/编译 artifact，校验 import/export，拓扑初始化；
- 生成内存 linked program 交给现有单模块 typed VM；
- Rust typed VM 先消费 linked bundle，后续实现原生 registry/loader；
- 模块缓存键包含源码 hash/编译器版本/ABI 版本。

## 正交性检查

- **类型系统**：类型/ADT 签名必须作为模块接口的一部分。
- **对象模型**：类/接口跨模块仍按 OP 0025/0026，不在本提案扩展。
- **函数**：函数符号导入/导出是模块 ABI 的核心。
- **模块**：扩展 OP 0006，不改变 object 方言的模块语义。
- **宏**：不涉及。
- **特例**：不为某个模块名/包名写特判。

## 替代方案

1. **继续拍平**：简单，但不支持独立编译/缓存/版本。
2. **单文件多模块 bundle**：实现较简单，但不是真正 separate compilation。
3. **运行时多模块 VM**：最完整，但 P1c 工程量过大。
4. **直接采用 WASM component model**：长期可互操作，但不能承载 Oort ADT/工具契约语义。

推荐：**module artifact + load-time linker**；执行层继续复用单模块 typed VM。

## 向后兼容

- P1a/P1b 拍平器保留为过渡实现；
- artifact 与 v6 不兼容，需要迁移/重新编译；
- B1 object→core 路径改为加载 typed module artifacts；
- 未实现的模块语义继续显式拒绝。

## 实现计划

1. **P1c-1（已实现）**：module id/export/import 校验；artifact；Python
   loader/linker；linked program 接入 `-t tvm`；artifact 不含宿主路径。
2. **P1c-2（进行中）**：导入构造器已实现（v8 构造器表）；待做：导入类型、
   ABI hash、B1 多模块、Rust linked bundle。
3. **P1c-3（待做）**：独立编译缓存、Rust 原生 loader、版本兼容策略。

## 未解决问题

- module_id 是否应完全脱离文件路径（逻辑名/清单）；
- 顶层副作用与初始化失败的错误模型；
- 泛型 ADT 的模块接口模板表示；
- 类型再导出/可见性规则；
- namespace 与函数名冲突的 mangling 规则；
- linked bundle 是否作为新的 `.obc` kind 或内存结构。
