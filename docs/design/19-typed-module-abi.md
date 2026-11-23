# 类型化模块 ABI（Typed Module ABI）

> **状态**：设计（2026-11-23）。配合 [OP 0027](../proposals/0027-typed-modules.md)
> 与 [spec 14](../spec/14-typed-bytecode.md)；P1c-1 的 artifact 与 Python
> loader 已实现（`bytecode/typed_artifact.py`），P1c-2 已加入构造器表与
> 导入构造器（v8）；`-t tvm`/`-t tbc` 共享该链接结果；P1a/P1b 的 HIR
> 拍平器仅保留给 `-t thir`（调试视图）。

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

## 3. Artifact 布局（v8，已实现）

```text
OBC | kind=1 | version=8
string module_id
u16    abi_version            # 当前 1

u32 export_count
export:
  u8     kind                 # 1 function / 2 adt / 3 constructor
  string name                 # function/ADT 名，或构造器名
  string adt_name             # 构造器所属 ADT；其他为空串
  u32    symbol               # 函数/ADT 表下标；构造器为构造器表下标
  i64    abi_hash             # 导出签名哈希（FNV-1a 63 bit）

u32 import_count
import:
  string module_id
  u8     kind                 # 1 module / 2 function / 3 adt / 4 constructor
  string name                 # namespace 别名或导入名
  i64    expected_abi_hash    # 导入时锁定的导出签名哈希

u32 constructor_count
constructor:
  string origin               # 定义模块的 module_id，或 <core-prelude>
  string adt_name
  string name
  u16    arity

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

- `NEW_ADT` 的构造器操作数是本 artifact 构造器表的下标；表内先放本模块
  构造器，再放本模块实际使用的导入构造器。loader 解析成合并后的全局 id；
- 类型表仍按 v6 的 tag 12 引用本 artifact 的 ADT 声明下标；声明表包含本模块
  声明、prelude 以及被引用的导入 ADT（导入项不导出）；
- 投影/寄存器/返回类型中的 `AdtType.origin` 在 artifact 构建时统一改写为
  定义模块的 `module_id`（prelude 除外），因此生成的文件不含宿主路径；
- proto 位置表的 filename 写 `module_id`；
- loader 接受 `abi_version=1`；
- `abi_hash` 覆盖导出签名：函数为参数/返回的 canonical 类型键，ADT 为
  构造器与 payload，构造器为 `adt.ctor(payload)#arity`；ADT 类型键包含
  `module_id`，因此同名 ADT 不会误配；
- `build_typed_program` 在链接前把 import 的 `expected_abi_hash` 钉到依赖
  当前导出哈希；loader 在非零时校验，不一致显式拒绝。

### 3.1 Linked bundle（kind=2）

链接后的单程序写成新的 `kind=2`：

```text
OBC | kind=2 | version=1
u16 abi_version
u32 adt_decl_count        # 合并后的声明表
adt_decl[...]
u32 constructor_count     # 与声明表扁平顺序一致
constructor[...]          # origin/adt_name/name/arity
u32 function_count
proto[...]
proto(main)
```

- 位置表 filename 固定为 `<linked>`，不含宿主路径；
- 构造器表按声明表扁平顺序排列，`NEW_ADT` 直接使用全局 id；
- kind=1 仍是模块/单模块格式，kind=2 只表示已完成重定位的链接结果；
- Rust typed VM 直接消费 kind=2；Python `read_linked_bundle` 会校验构造器表
  与声明表一致。

## 4. 符号模型

### 函数

- 导出符号：`module_id::function`；
- import 解析到导出函数；
- bytecode `LOAD_G` 使用符号名，loader 建全局表；
- 可选后续用符号 ID + relocation 替代字符串。

### 类型/ADT

- 类型引用：`(module_id, name, args)`；
- artifact 类型表的 ADT tag 指向本 artifact 声明表下标；导入类型连同其
  声明副本进入声明表，origin 改写为定义模块的 `module_id`；
- loader 按 `(origin, name)` 合并并解析到全局 ADT 身份；
- 同名 ADT 不同 module_id 不冲突。

### 构造器

- 构造器符号：`(origin, adt_name, ctor_name)`；
- `NEW_ADT` 操作数指向 artifact 构造器表；
- loader 按符号解析到合并后的 `(decl, ctor)`，生成全局构造器 ID 并回填
  操作数；
- 导入构造器与本地构造器共用同一张表，不再依赖模块内 `decl_id`。

## 5. Loader / linker

Python loader/linker（`load_typed_units` + `build_typed_program`）：

1. 从 root checked AST 出发解析 import spec → path，得到 unit 图（依赖在前）；
2. 每个 unit lowering 后编译为 v8 artifact（内存或磁盘）；
3. 校验 module_id、kind/version、ABI 版本、import/export 边；
4. 检测循环，得到拓扑序；
5. 合并 ADT 声明（prelude 去重），按 `module_id` 重写 origin；
6. 解析 artifact 构造器表，回填 `NEW_ADT` 全局 id，并重映射主函数
   `DEF_FUN` 函数 id；
7. 生成 single-module linked program；
8. 交给现有 typed VM。

磁盘路径由 `write_typed_artifact`/`read_typed_artifact` 覆盖。

### 5.1 编译缓存（P1c-3，契约见 [OP 0030](../proposals/0030-compilation-cache.md)）

- `--cache-dir DIR` 或 `OORT_CACHE_DIR` 开启缓存（`--no-cache` 关闭）；布局为
  `DIR/v8/abi<N>/<ab>/<cd>/<sha256>.obc`，版本化且内容寻址；
- key 包含源码字节、`module_id`、编译器版本、artifact/ABI 版本、代码生成
  选项以及直接依赖的接口哈希；依赖实现变化不会使依赖者 miss，接口变化会
  直接 miss；
- 命中后仍防御性校验 import 哈希；损坏/截断条目按 miss 处理并覆盖；
- 每键 single-flight 锁；条目带 JSON sidecar；`--cache-max-size` 按 mtime
  LRU 淘汰；`--cache-stats`/`--cache-clean` 维护；
- 解析/类型检查仍每次执行；缓存只跳过 lowering 与字节码编译。

B1 边界使用同一 loader：`build_typed_program_exports` 返回链接后的程序与
根模块导出函数名，边界只把这些导出绑定到动态环境，不再泄漏依赖模块的
函数。

Rust（已实现）：

- 读取 kind=2 linked bundle，直接交给 typed VM；
- 读取 v8 module artifact，原生校验 import/export 与 ABI hash、合并声明、
  重定位 `NEW_ADT`/`DEF_FUN`、重映射类型表里的 ADT 声明 id；
- CLI：`oort-vm --link <root.obc> <dependency.obc>...`；
- 缓存仍由 Python 编译器负责；Rust 只读取已经产出的 artifact。

## 6. 初始化

- 依赖先于依赖者；
- 每个模块 main 只执行一次；
- 循环显式拒绝；
- 顶层副作用限制；
- 导出函数在初始化前可绑定，但可观察状态以初始化完成为准。

## 7. 版本与兼容

- artifact `abi_version` 与 kind/version 分离；
- 读取方要求精确的 kind/version/ABI 版本，不做兼容猜测：
  - kind=1 只接受 v6（单模块）或 v8（module artifact）；
  - kind=2 只接受 v1 linked bundle；
- v6 与 v8 不静默互读；v7 是未发布的过渡格式；
- 缓存 key 含 artifact/ABI/compiler 版本，升级后自然 miss；
- 暂不承诺跨版本模块混用；需要迁移时重新编译源码。

## 8. 分阶段

| 阶段 | 内容 | 状态 |
|---|---|---|
| P1c-1 | module id/export/import 校验、artifact、Python loader、linked program | 已实现（v7） |
| P1c-2 | 导入构造器/类型、ABI hash、B1 多模块、Rust linked bundle | 已实现（namespace 类型导入；from-import 类型别名规则待定） |
| P1c-3 | `--cache-dir` artifact cache、Rust `--link` 原生 loader、版本拒绝策略 | 已实现 |

## 9. 开放问题

1. module_id 是否应脱离文件路径，改由 manifest 生成？
2. import/export 是否要显式 `pub`/可见性？
3. 泛型 ADT 的模块接口如何表示类型参数模板？
4. ~~linked bundle 是新 `.obc` kind，还是纯内存结构？~~ 已定：`kind=2`。
5. Rust loader 是否需要与 Python loader 共用 ABI hash 计算？
6. 顶层副作用/初始化失败如何映射为诊断？
7. 模块级常量/顶层 val 何时进入 typed 子集？
