# 类型化模块 ABI（Typed Module ABI）

> **状态**：设计草案（2026-11-23）。配合 [OP 0027](../proposals/0027-typed-modules.md)
> 与 [spec 14](../spec/14-typed-bytecode.md)；当前 P1a/P1b 仍是编译期拍平，
> 本文描述 P1c 的 artifact/loader 方向。

## 1. 目标

把现在的：

```text
AST dependencies → lower → merge → one TypedProgram
```

升级为：

```text
module artifacts → import/export validation → relocation → linked program
```

目标：

- core 模块可独立编译成 typed artifact；
- import/export 使用模块限定符号；
- 类型/ADT/构造器跨模块可校验；
- Python/Rust typed VM 可加载 linked program；
- 支持缓存、版本拒绝、循环诊断。

非目标：package manager、热替换、动态 import、core→object 回调。

## 2. 模块身份

- `module_id`：相对入口/模块根的 POSIX 路径，例如 `lib`、`math`；
- artifact 不保存绝对路径；
- 后续 package manager 使用 `package::module`；
- source path 与 module_id 的映射由 loader/清单提供。

## 3. Artifact 布局（v7 草案）

```text
OBC | kind=1 | version=7
string module_id
u16    abi_version

u32 export_count
export:
  u8   kind          # function / adt / constructor / type
  string name
  u32  symbol
  type_desc signature_or_type
  u64  abi_hash

u32 import_count
import:
  string module_id
  u8   kind
  string name
  u64  expected_abi_hash

u32 adt_decl_count
adt_decl[...]

u32 function_count
proto[...]
proto(main)
```

具体字段在 P1c-1 实现前再收敛；先固定：

- 模块限定符号；
- 类型/ADT 的模块引用；
- ABI hash/version；
- 不写宿主路径。

## 4. 符号模型

### 函数

- 导出符号：`module_id::function`；
- import 解析到导出函数；
- bytecode `LOAD_G` 使用符号名，loader 建全局表；
- 可选后续用符号 ID + relocation 替代字符串。

### 类型/ADT

- 类型引用：`(module_id, name, args)`；
- 类型表中的 ADT tag 保存模块引用，而不是当前模块的 decl_id；
- loader 解析到全局 ADT 实例身份；
- 同名 ADT 不同 module_id 不冲突。

### 构造器

- 构造器符号：`(module_id, adt_name, ctor_name)`；
- `NEW_ADT` 通过构造器符号表/引用定位；
- loader 生成全局构造器 ID；
- 不再依赖模块内 `decl_id`。

## 5. Loader / linker

Python `TypedModuleLoader`：

1. 解析 import spec → path；
2. 读取 artifact，或从 checked AST 编译并缓存；
3. 校验 module_id、kind/version、ABI hash；
4. 构建依赖图，检测循环；
5. 拓扑初始化；
6. 构建函数/ADT/构造器/类型全局表；
7. 生成 linked program；
8. 交给现有 typed VM。

Rust：

- P1c-1：消费 Python 生成的 linked bundle；
- P1c-2：原生 module registry + loader；
- 缓存键含源码 hash、编译器版本、ABI 版本。

## 6. 初始化

- 依赖先于依赖者；
- 每个模块 main 只执行一次；
- 循环显式拒绝；
- 顶层副作用限制；
- 导出函数在初始化前可绑定，但可观察状态以初始化完成为准。

## 7. 版本与兼容

- artifact `abi_version` 与 kind/version 分离；
- loader 遇到不兼容版本显式拒绝；
- v6 与 v7 不静默互读；
- 暂不承诺跨版本模块混用。

## 8. 分阶段

| 阶段 | 内容 |
|---|---|
| P1c-1 | v7 metadata、Python loader、linked program |
| P1c-2 | 导入构造器/类型、ABI hash、B1 多模块、Rust linked bundle |
| P1c-3 | 独立缓存、Rust 原生 loader、兼容策略 |

## 9. 开放问题

1. module_id 是否应脱离文件路径，改由 manifest 生成？
2. import/export 是否要显式 `pub`/可见性？
3. 泛型 ADT 的模块接口如何表示类型参数模板？
4. linked bundle 是新 `.obc` kind，还是纯内存结构？
5. Rust loader 是否需要与 Python loader 共用 ABI hash 计算？
6. 顶层副作用/初始化失败如何映射为诊断？
7. 模块级常量/顶层 val 何时进入 typed 子集？
