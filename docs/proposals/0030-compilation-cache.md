# OP 0030: 编译缓存（Compilation Cache）

- **状态**：Proposed（S1/S2/S3 已实现）
- **作者**：Oort 设计讨论
- **创建日期**：2026-11-24
- **相关**：[OP 0027](0027-typed-modules.md)、[design 19](../design/19-typed-module-abi.md)、[spec 14](../spec/14-typed-bytecode.md)

## 摘要

为 typed 模块 artifact 定义可选的磁盘编译缓存：缓存单元、键、依赖失效、
存储布局、并发与清理策略。短期先做项目内 opt-in 缓存并保证正确性；长期
演进到接口摘要/代码分离、全局共享缓存与 Rust 原生读取。

## 动机

当前 `-t tvm`/`-t tbc` 每次运行都会重新 lowering 并编译所有可达 core 模块，
即使源码完全没变。P1c-3 已有 `--cache-dir` 最小实现，S2 进一步固定了布局与键：

- 每模块一个 v8 artifact，键包含源码、`module_id`、编译器/格式/ABI 版本、
  代码生成选项与依赖接口哈希；
- 版本化内容寻址布局，原子写入，artifact 不含宿主路径；
- 命中后仍防御性校验 import ABI 哈希，损坏条目按 miss 处理。

但它还缺少明确的缓存契约：键是否包含依赖接口、目录如何分版本、如何清理、
并发写如何协调、缓存与 Rust/边界如何共享。没有契约，后续改动容易退化成
“能跑但不可预测”的构建缓存。

## 设计

### 1. 缓存单元与范围

- 缓存单元：**一个模块的 v8 artifact**（kind=1 module artifact）；
- kind=2 linked bundle 暂不缓存（长期 L2 再做）；
- kind=0 动态字节码不在本提案范围；
- 解析与类型检查仍每次执行；短期只缓存 lowering/typed 字节码编译；
- 缓存是**可选加速**：任何 miss/损坏都回退到重新编译，不影响语义。

### 2. 键（S2 已实现）

```text
H( "oort-cache-v1"
   source_sha256
   module_id
   compiler_version
   artifact_version
   abi_version
   codegen_options            # 当前为空，保留
   sorted(import_module_id + ":" + dependency_interface_hash)
)
```

- `dependency_interface_hash` 使用依赖的 `module_abi_hash`（导出签名、ADT
  结构、构造器；不含实现体）；
- 依赖接口不变时，依赖实现变化不会使依赖者 miss（early cutoff 的前置条件）；
- 依赖接口变化时，依赖者直接 miss，而不是先命中再重建；
- 载入后仍校验 artifact 内部的 `expected_abi_hash`，作为防御性检查。

### 3. 存储布局

S2：

```text
<cache>/v8/abi1/<ab>/<cd>/<sha>.obc
<cache>/tmp/
```

- `v8`/`abi1` 为版本目录；格式或 ABI 升级后整体切换，旧目录可被清理；
- 文件名是键的 SHA-256，天然去重、不依赖源码路径；
- 写入 `tmp/` 后原子 rename 到目标；
- 每条目有 `<sha>.json` sidecar：`module_id`、依赖接口哈希、编译器/格式/ABI
  版本、存储时间；供统计、清理与调试使用。

### 4. 载入与失效

1. 按依赖优先顺序处理 unit；
2. 计算键（依赖接口哈希来自已处理的依赖 artifact）；
3. 命中则校验 module_id、版本、import 哈希；
4. 任一项不匹配视为 miss，重新编译并覆盖；
5. 编译失败不写缓存；
6. 缓存损坏/截断只告警（`-v`）并按 miss 处理，绝不静默执行坏 artifact。

### 5. 并发

- 每个键使用 lockfile single-flight：miss 后获取锁、重查缓存，仍 miss 才编译；
  等待者看到条目出现即读取；
- 锁文件带超时与 stale 清理；万一锁超时则无锁编译，原子 rename 仍保证读者
  安全；
- 不要求跨机器共享时的强一致；缓存是性能设施，不是正确性来源。

### 6. 清理与容量

- `--cache-clean` 删除当前版本目录（artifact + sidecar + 锁/临时目录）；
- `--cache-stats` 输出条目数/大小；
- `--cache-max-size SIZE` 按 mtime 做 LRU 淘汰（支持 K/M/G），至少保留一条；
- 版本升级不自动删除旧目录，由清理命令处理；
- 缓存目录不进入 git；项目内默认建议 `.oort-cache/`。

### 7. CLI 与环境

| 来源 | 行为 |
|---|---|
| `--cache-dir DIR` | 开启缓存并指定目录 |
| `--cache-max-size SIZE` | 容量上限与 LRU 淘汰 |
| `--no-cache` | 强制关闭（覆盖环境变量） |
| `OORT_CACHE_DIR` | 未给 flag 时的默认目录（S4） |
| 未设置 | 不缓存 |

优先级：`--no-cache` > `--cache-dir` > `OORT_CACHE_DIR` > 关闭。

### 8. 可移植性与安全

- 键不包含绝对路径；artifact 的 ADT origin/位置表使用 `module_id`；
- 缓存条目不可作为分发格式，也不承诺跨编译器版本可读；
- 缓存目录视为用户可信输入；仍对 artifact 做结构与符号范围校验；
- 不缓存解析结果，避免把源码/诊断元数据长期落盘。

### 边界与限制

- 不做网络/远程缓存、包管理、依赖下载；
- 不做跨版本二进制兼容；
- 不缓存解释器 AST/检查结果（近期）；
- 锁超时降级时不保证“只编译一次”（仍保证结果正确）；
- 不改变任何语言语义或诊断。

## 正交性检查

- **类型系统**：接口哈希覆盖类型/ADT 导出；类型变化自然 miss。
- **模块/ABI**：缓存键建立在 OP 0027 的 module_id/export/import 之上。
- **B1 边界**：边界使用同一 loader/缓存；只绑定根模块导出。
- **Rust**：Rust 读取 Python 产出的 artifact；长期可只读共享缓存。
- **REPL/字符串输入**：无文件路径，不缓存。

## 替代方案

1. **源码旁 `.pyc` 风格**：实现最简单，但污染源码树、跨项目不共享、依赖
   跟踪弱；不作为默认。
2. **只依赖构建工具缓存**：Oort 目前没有统一构建系统，CLI 直接运行需要
   自己的缓存契约。
3. **一开始就做全局内容寻址缓存**：需要清理/并发/信任模型，超出当前需求；
   先项目内 opt-in，S4 再升级。
4. **缓存整个 linked program**：失效粒度过粗，任一模块变化都要重链；先按
   模块缓存。

## 向后兼容

- 缓存完全可选，关闭时行为与现在一致；
- 缓存格式/键变化通过版本目录隔离，旧条目自然失效；
- 不改变 CLI 现有语义，只新增选项。

## 实现计划

### 短期（S1–S4）

| 阶段 | 内容 | 验收 |
|---|---|---|
| S1（已实现） | `--cache-dir`、源码+版本键、载入重钉依赖哈希、原子写入、路径剥离 | 冷/热运行输出一致；缓存文件不含宿主路径 |
| S2（已实现） | 版本化布局、依赖接口哈希入键、代码生成选项入键、`--cache-clean`/`--cache-stats`、损坏条目降级 | 依赖接口变化只重建依赖者；依赖实现变化不重编依赖者；热运行编译 0 个 artifact；目录可清理 |
| S3（已实现） | single-flight 锁、容量上限/LRU、sidecar manifest、并发测试 | 8 个并发进程无损坏、每键最多一次编译 |
| S4 | `OORT_CACHE_DIR`、`--no-cache`、可选全局共享缓存、文档与基准 | 跨项目命中同一模块；优先级符合契约 |

S2 的失效矩阵测试至少覆盖：源码、module_id、编译器版本、artifact/ABI
版本、代码生成选项、依赖接口、依赖实现（应命中）。

### 长期（L1–L3）

| 阶段 | 内容 | 理由 |
|---|---|---|
| L1 | 接口元数据与代码分离（`.oortmeta` + `.obc`），依赖者只依赖接口摘要 | 实现变化不重编依赖者（OCaml `.cmi`/GHC `.hi` 模型） |
| L2 | 缓存 kind=2 linked bundle，键为模块图接口哈希；Rust loader 只读共享缓存 | 减少重复链接；Rust 成为默认执行引擎后的必要条件 |
| L3 | Go/Bazel 式 action ID 与可选远程缓存 | 仅在 CI/团队共享出现明确需求后评估 |

长期非目标：把缓存当分发格式、跨编译器版本兼容、热替换、增量式前端。

## 参考与对照

| 系统 | 键 | 依赖处理 | 存储 |
|---|---|---|---|
| Python `.pyc` | magic + mtime/size | 无 | 源码旁 `__pycache__` |
| Go | action ID（完整输入哈希） | 依赖 action ID 传递 | 全局 `GOCACHE` + trim |
| Zig | 输入哈希 + manifest | 哈希传递 | 全局缓存 + 锁/清理 |
| OCaml/Dune | `.cmi` 接口 CRC | 接口摘要、early cutoff | `_build` |
| Rust/Cargo | fingerprint（版本/flags/依赖） | dep-info | `target/` |
| Node/Deno | 模块键 + 运行时版本 | 模块图 | `NODE_COMPILE_CACHE`/`DENO_DIR` |
| GHC | `.hi` 接口摘要 | recompilation avoidance | 源码旁/构建目录 |

结论：Oort 短期采用 **内容寻址 + 版本目录 + 依赖接口哈希**；长期再考虑
接口/代码分离与共享缓存。

## 未解决问题

- 默认是否应开启项目内缓存，还是保持 opt-in？
- 全局缓存目录在 Windows/macOS/Linux 的默认位置与权限模型；
- manifest 格式与缓存统计的最小字段；
- L1 接口文件的版本与校验方式；
- Rust 是否应直接管理缓存写入，还是只读 Python 产物；
- 缓存条目是否需要内容校验和（防篡改/防磁盘损坏）。
