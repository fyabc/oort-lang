# 类型化模块 ABI（Typed Module ABI）

> **状态**：设计（2026-11-23）。配合 [OP 0027](../proposals/0027-typed-modules.md)
> 与 [spec 14](../spec/14-typed-bytecode.md)；P1c-1 的 v7 artifact 与 Python
> loader 已实现（`bytecode/typed_artifact.py`），`-t tvm`/`-t tbc` 共享该
> 链接结果；P1a/P1b 的 HIR 拍平器仅保留给 `-t thir`（调试视图）。

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

## 3. Artifact 布局（v7，已实现）

```text
OBC | kind=1 | version=7
string module_id
u16    abi_version            # 当前 1

u32 export_count
export:
  u8     kind                 # 1 function / 2 adt / 3 constructor
  string name                 # function/ADT 名，或构造器名
  string adt_name             # 构造器所属 ADT；其他为空串
  u32    symbol               # 函数/ADT 表下标；构造器为本地 id
  i64    abi_hash             # P1c-1 预留 0

u32 import_count
import:
  string module_id
  u8     kind                 # 1 module / 2 function / 3 adt / 4 constructor
  string name                 # namespace 别名或导入名
  i64    expected_abi_hash    # P1c-1 预留 0

u32 adt_decl_count
adt_decl:
  string origin               # module_id 或 <core-prelude>
  string name
  u16    constructor_count
  constructor:
    string name
    u8     arity

u32 function_count
proto[...]
proto(main)
```

- 类型表仍按 v6 的 tag 12 引用本 artifact 的 ADT 声明下标；
- 投影/寄存器/返回类型中的 `AdtType.origin` 在 artifact 构建时统一改写为
  `module_id`（prelude 除外），因此生成的文件不含宿主路径；
- proto 位置表的 filename 写 `module_id`；
- loader 接受 `abi_version=1`；`abi_hash` 字段留给 P1c-2 的类型 ABI。

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

Python loader/linker（P1c-1：`load_typed_units` + `build_typed_program`）：

1. 从 root checked AST 出发解析 import spec → path，得到 unit 图（依赖在前）；
2. 每个 unit lowering 后编译为 v7 artifact（内存或磁盘）；
3. 校验 module_id、kind/version、ABI 版本、import/export 边；
4. 检测循环，得到拓扑序；
5. 合并 ADT 声明（prelude 去重），按 `module_id` 重写 origin；
6. 重映射 `NEW_ADT` 构造器 id 与主函数 `DEF_FUN` 函数 id；
7. 生成 single-module linked program；
8. 交给现有 typed VM。

磁盘路径由 `write_typed_artifact`/`read_typed_artifact` 覆盖；编译器当前在
内存中构建 artifact，磁盘缓存留给 P1c-3。

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

| 阶段 | 内容 | 状态 |
|---|---|---|
| P1c-1 | module id/export/import 校验、v7 artifact、Python loader、linked program | 已实现 |
| P1c-2 | 导入构造器/类型、ABI hash、B1 多模块、Rust linked bundle | 待做 |
| P1c-3 | 独立缓存、Rust 原生 loader、兼容策略 | 待做 |

## 9. 开放问题

1. module_id 是否应脱离文件路径，改由 manifest 生成？
2. import/export 是否要显式 `pub`/可见性？
3. 泛型 ADT 的模块接口如何表示类型参数模板？
4. linked bundle 是新 `.obc` kind，还是纯内存结构？
5. Rust loader 是否需要与 Python loader 共用 ABI hash 计算？
6. 顶层副作用/初始化失败如何映射为诊断？
7. 模块级常量/顶层 val 何时进入 typed 子集？
