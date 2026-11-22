# 跨方言边界与 FFI（Boundary / FFI）

> **状态**：设计草案 + B1 语义原型（2026-11-23）。`oort-object → oort-core`
> 导入已实现 Python 侧边界原型；反向调用、类/ADT 边界、C FFI 与性能边界仍未
> 实现。本文其余部分继续作为架构与语义设计记录。
>
> 关联：[design 02](02-bytecode-vm-design.md) 的边界调用指令、
> [design 03](03-type-system-design.md) 的渐进类型边界、
> [design 12](12-host-boundary.md) 的宿主边界、
> [design 15](15-typed-ir.md) 的 typed IR/VM、
> [spec 11](../spec/11-core-probe.md) 与 [spec 14](../spec/14-typed-bytecode.md)。

## 1. 问题与目标

Oort 有两个方言：

- `oort-object`：动态、脚本导向，适合快速迭代与 REPL；
- `oort-core`：静态、类型化，适合作为库/性能敏感代码。

目标调用方向是 **object → core**：脚本导入静态库并调用其函数，库内部
用 typed 字节码/Rust VM 执行。反向（core → object）暂时不允许。

需要回答：

1. 这种方向能否同时提供脚本体验和「库级」性能？
2. 边界值映射、类型守卫、错误/blame、集合别名、模块导入如何定义？
3. 它与 C FFI 是什么关系，是否应该合并为一份规范？
4. 在 typed IR/VM 主线中应排什么优先级？

## 2. 边界分类

| Profile | 边界 | 特点 |
|---|---|---|
| **内部：object ↔ core** | 同一语言、不同方言 | 共享 Oort 值/异常/GC，可做 blame；无 unsafe |
| **外部：Oort ↔ C** | C ABI | 手动所有权/生命周期、错误码、回调、线程、unsafe、平台 ABI |
| **宿主：Oort ↔ Python/Rust host** | 解释器/VM 的宿主边界 | [design 12](12-host-boundary.md) 的 HostBridge 模式 |

三者共享一套**边界模型**（类型映射、调用桩、守卫、错误、所有权、
回调、版本），但规范应分开：内部边界可以先简化；C FFI 必须额外定义
内存/ABI/unsafe 规则。

## 3. 方向策略

### 3.1 object → core 允许

- 动态脚本导入 core 模块，调用导出的函数/构造器/方法；
- core 内部保持静态类型与优化，入口处做参数守卫；
- 返回值装箱回动态值；
- 典型用途：数值、集合处理、解析、加密、图像/数据管道。

### 3.2 core → object 暂时拒绝

原因：

- `oort-core` 没有 `Any`/`Dynamic` 顶类型，静态代码无法安全持有动态值；
- 允许反向调用需要动态类型、契约/guard、blame、回调生命周期等一整套设计；
- 先收窄方向，可以让内部边界保持简单、可验证。

**代价**（必须明确写入库 API 约定）：

- core 库不能接受 object 的 lambda/闭包做回调；
- `map`/`filter`/`sorted(key=...)`、事件/visitor/异步 continuation 等
  callback-heavy API 在初始阶段不可用；
- 替代方案：iterator/handle/batch API，让 object 反复调用 core 的
  `next`/`step`，而不是 core 反过来调 object。

反向调用的重新评估条件：core 引入 `Dynamic`/契约类型，或出现明确的
callback 库需求。届时作为独立提案处理，不在本设计内。

## 4. 语义设计

### 4.1 值映射

| 动态值 | core 类型 | 边界规则 |
|---|---|---|
| `Int` | `Int` | 语义一致（任意精度）；`Int<N>` 需范围检查 |
| `Float` | `Float` | binary64 |
| `Bool` | `Bool` | 严格 |
| `String` | `String` | 不可变；可共享或复制 |
| `List[T]` / `Tuple[...]` | 对应容器 | 入口检查元素类型；初始深拷贝 |
| `Set[T]` / `Dict[K,V]` | 对应容器 | 同上；键用现有键协议 |
| 类/接口实例 | 名义类/接口 | 初始为不透明 handle + 方法桩 |
| ADT 值 | enum | 初始不透明；构造器/访问器桩 |
| `null` | `Unit` | core 返回 `Unit` → 动态 `null`；反向传 null 到非 Unit 报错 |
| 函数值 | 仅 core 导出 | 动态闭包不能传入 core；core 函数可作为可调用桩返回 |

### 4.2 复制、别名与可变性

初始版本采用**边界复制**：

- 动态 List/Set/Dict 传入 core 时深拷贝并检查元素类型；
- core 返回的容器装箱为新的动态容器；
- 避免两个运行时/GC 共享对象图带来的别名、写屏障与生命周期问题。

代价：大集合的 O(n) 检查与复制。后续若统一运行时/共享 GC，可评估
零拷贝或写时复制；在此之前，库 API 应提供 batch/iterator 形式减少
跨边界次数。

### 4.3 守卫、错误与 blame

- core 函数入口按 `param_types` 做守卫；失败时抛出边界错误，**归责
  动态调用方**（包含调用位置与期望/实际类型）；
- core 内部错误（除零、越界、模式失败）按 core 位置传播，动态侧看到
  的是 Oort 错误，不是宿主异常；
- 静态返回 → 动态装箱是安全的，不需要运行时类型检查；
- 不允许隐式数值转换；`Int → Int<N>` 必须显式检查收窄；
- 错误信息不泄漏宿主对象/路径。

### 4.4 回调与迭代器

初始只支持 object → core 的**直接调用**。需要遍历时：

- core 导出 iterator/handle（不透明值），object 调用 `next`/`step`；
- 或 core 提供接受集合的批量函数（`sort(xs)` 而不是 `sort(xs, key=f)`）；
- 动态函数值不能作为参数进入 core（编译/链接期报错）。

## 5. 模块与导入

跨方言导入需要一个明确的边界加载流程（示意）：

```oort
#lang oort-object
from "./mathlib" import add, Vector
print(add(1, 2))
```

其中 `mathlib.ort` 是 `#lang oort-core`。加载器：

1. 读取目标模块的方言标记；
2. core 模块编译为 typed 字节码（或加载预编译 `.obc`），构建导出表；
3. 为每个导出函数生成动态侧 **boundary stub**（做参数检查/复制/装箱）；
4. 类型/类导出为不透明句柄与构造器/方法桩；
5. 动态模块只看到 stub，core 模块不能反向导入动态模块。

约束：

- 允许 object 导入 core，拒绝 core 导入 object（编译期诊断）；
- 导出表区分值导出与类型导出（core 检查器已有类似结构）；
- 名称冲突/重导出规则沿用现有模块系统；
- 预编译 `.obc` 需携带方言/版本信息，加载时校验。

## 6. 实现路线与性能

| 方案 | 做法 | 优点 | 缺点 |
|---|---|---|---|
| **A. 统一 Rust 运行时** | 同一 VM 执行 kind=0/kind=1 字节码，边界为内部调用 | 调用最快；可共享值/GC | 需要 Rust 动态 VM，工程量最大 |
| **B. Python object VM + Rust typed VM（PyO3/进程内）** | Python 动态 VM 调用 Rust typed VM 库 | 复用 Python 前端/REPL；比 C ABI 安全 | 每次跨 Python↔Rust；值需转换 |
| **C. 原生 core 库 + C ABI** | core 编译为原生库，Python 调用 | 库性能最好；接近 CPython 扩展 | 需要 C ABI、所有权/生命周期、平台矩阵 |
| **D. Python typed VM sidecar** | boxed typed VM 作为库 | 语义原型最快 | 无性能收益 |

**建议顺序**：

1. **设计（本文）**；
2. **语义原型**：D 或 B，验证导入、守卫、错误/blame 与库 API 体验，不设性能门禁；
3. **性能实现**：Rust VM v2/阶段 A 定型后，在 B/C/A 中选择；
4. **C FFI**：与性能实现并行或稍后，单独 profile。

### 6.1 性能量级（待实测）

| 路径 | 单次调用开销量级 | 适用 |
|---|---|---|
| Python boxed typed VM | µs 级 | 语义原型 |
| Python ↔ Rust typed VM（PyO3） | ~0.1–2 µs | 中等粒度库 |
| Python ↔ 原生 C ABI | ~0.1–1 µs | 粗粒度库 |
| 统一 Rust 运行时内部边界 | 几十 ns + 值复制 | 细粒度/高频调用 |

这些是量级估计，不是承诺。真正的门禁应测：

- 空/极小 core 函数的调用开销；
- 典型库操作（排序 1e5–1e6 元素、字符串处理）相对原生实现的倍率；
- 大集合跨边界的复制成本；
- 启动/加载成本。

**性能预期**：粗粒度库调用可接近「脚本 + 原生库」体验；细粒度高频调用
需要统一运行时/批量 API；回调 API 在反向调用开放前不可用。

## 7. C FFI profile（后续）

C FFI 与内部边界共享模型，但必须额外定义：

1. **类型映射**：`Int32/Int64/UInt*`、`Float32/Float64`、`Bool`、C 字符串
   （指针+长度或 NUL 结尾）、数组/切片、struct、指针、函数指针；
   `Int`（任意精度）不能直接映射，必须显式收窄。
2. **所有权与生命周期**：谁分配/释放、借用 vs 拥有、字符串/数组的 pinning、
   GC 与 native 指针的交互。
3. **调用约定与错误**：C ABI、错误码/out-param、禁止跨 FFI 展开异常。
4. **回调**：函数指针 + userdata、生命周期、线程规则、异步完成。
5. **unsafe 边界**：所有 native 调用进入受控 unsafe 区域；不安全的输入
   必须显式校验。
6. **安全与信任**：初始只允许受信任的原生模块注册表，不加载任意宿主模块。
7. **平台与版本**：ABI/头文件版本、符号导出、平台矩阵、测试。

C FFI **不在本设计的第一阶段实现**；先做内部边界，验证模型与性能，
再决定 C profile 的优先级。

## 8. 里程碑

| 里程碑 | 范围 | 退出条件 |
|---|---|---|
| **B0 设计** | 本文；方向策略、值映射、边界模型 | 评审通过 |
| **B1 语义原型** | object→core 导入/调用（D/B），boxed | **已完成（2026-11-23）**；示例库/测试可运行；类型错误/blame 可读；无性能门禁 |
| **B2 库覆盖** | S2/S3、类/ADT、集合/库 API 约定 | 至少一个 core 库端到端可用 |
| **B3 性能实现** | 根据 Rust VM v2 选 B/C/A | 调用开销与库吞吐达到预算 |
| **B4 C FFI** | C profile | 受信任原生模块、错误/所有权/回调测试通过 |

### 8.1 B1 语义原型（2026-11-23，已实现）

B1 只做 Python 侧语义验证，不做性能门禁：

- **方向**：只允许 `oort-object` 模块导入 `oort-core` 模块；core→object 仍在
  核心检查器与模块加载器两处拒绝；
- **执行**：导入的 core 模块经 `lower_typed_module` + `compile_typed_module`
  编译，由 `TypedCodeVM` 执行模块 main，然后把顶层函数包装为动态侧 callable；
- **边界桩**：`TypedBoundaryFunction` 按 `param_types` 递归守卫参数（含嵌套
  List/Tuple/Set/Dict），容器跨边界深拷贝；返回容器同样拷贝；标量/String
  共享不可变值；
- **值映射**：当前 typed 子集（Int/Float/Bool/String/Unit/List/Tuple/Set/Dict）
  可用；Unit ↔ `null`；ADT 按 `(origin, name, args)` 名义身份守卫并复制；
  对象侧只能持有/打印/回传 ADT，不能构造或模式匹配；类、接口、函数值、
  迭代器显式拒绝；
- **错误**：守卫失败归责动态调用方，错误包含 core 函数名、参数位置与期望/实际
  类型；core 内部错误沿用 core 源码位置；
- **限制**：只导出顶层函数；core 模块自身的 typed 导入、类/接口、回调、C FFI
  均未开放；每个 core 模块一个 `TypedCodeVM` 实例，模块只执行一次；不同 core
  模块的同名 ADT 通过模块 origin 区分；
- **入口**：默认 `-t vm` 与回退 `-t eval` 的 object 入口都可用；验收示例
  `examples/09_boundary/09_00_object_calls_core.ort`（配套 `core_lib.ort`）；
  测试覆盖 `from` 导入、模块属性导入、嵌套 core 调用、Unit 返回、容器复制、
  ADT 跨模块 origin 与守卫失败。

实现入口：`src/oort_lang/bytecode/typed_boundary.py`、`runtime/modules.py`
的 object→core 分支，以及 `driver/compiler.py` 的回调接线。诊断基准
`benchmarks/boundary_run.py` 对比动态库、core Python typed VM、core Rust
typed VM 与 B1 边界；该基准只用于研究诊断，不设门禁。B1 仍不承诺 ABI；
Rust 侧边界与性能实现属于 B3。

## 9. 开放问题

1. 反向调用（core→object）何时解禁？是否等 `Dynamic`/契约设计？
2. 集合边界复制 vs 共享：是否在统一运行时后改为零拷贝/COW？
3. 类/ADT 从动态侧如何暴露：不透明句柄、访问器、还是包装类？
4. 导出函数值/方法引用如何表示与调用？
5. 边界 stub 的缓存/懒加载与模块循环导入规则？
6. `Int<N>` 与 C 整数的显式转换语法/API？
7. 性能实现选 B 还是 C？取决于 Rust VM v2 是否成为主后端。
8. C FFI 的回调/线程/GC pinning 规则。

## 10. 优先级建议

- **设计现在做**（低成本、影响 ABI/模块/typed IR）；
- **语义原型在 S2/S3 之后**（core 需要集合/字符串库能力）；
- **性能实现等 Rust VM v2/阶段 A 定型**；
- **C FFI 不阻塞脚本+库体验**，在内部边界验证后评估。

不把本工作排在 S2/S3 之前，避免拖慢 typed 语言覆盖；也不要拖到所有
类型特性完成之后，因为它会影响模块加载、值复制和 ABI 设计。
