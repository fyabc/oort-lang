# 类型化 IR 研究（Typed IR）

> **状态**：研究草案（2026-11-22）。本文只讨论设计空间、研究假设与实施顺序，
> **不改变语言表面**，也不修改当前擦除式 HIR / 字节码 / VM 的语义。
> 当前实现的行为仍以 [spec 12](../spec/12-hir-bytecode-vm.md) 与
> [spec 13](../spec/13-bytecode-serialization.md) 为准。
>
> 关联文档：[性能路线图](../roadmap.md)阶段 B；[design 02](02-bytecode-vm-design.md)
> 的长期双轨架构；[design 03](03-type-system-design.md) 的渐进类型目标；
> [design 13](13-hir-design.md) 的当前 HIR；[design 14](14-core-typechecking.md)
> 的已实现检查算法。

## 0. 结论摘要

- **从哪里开始**：先做 **typed HIR + 受限标量子集**，不碰字节码格式；在 Python
  侧用校验器、dumper、typed 解释器把语义与类型来源打通，再决定是否进入
  typed 字节码。
- **类型放在哪**：类型作为 HIR 的**结构化元数据**（寄存器/槽/签名），由检查器
  唯一提供（**T1：AST 元数据携带 `Type` 对象**，2026-11-22 选定）；不做第二套
  推断，不解析 `describe_type` 字符串。
- **执行路径**：v0 只覆盖 `#lang oort-core` 的完整子集程序；子集外继续走现有
  擦除式 VM，**不静默切换语义**，研究阶段用显式 target 区分路径。
- **验证顺序**：M1 typed HIR 之后**直接做 M2 typed 解释器**（2026-11-22 选定），
  不走“先降级到现有字节码”的替代路径。
- **何时改字节码**：等 typed HIR 的语义/差分/基准稳定后，再用 `.obc` 的
  `kind=1` 做 typed 字节码原型；未装箱值与守卫优先在 Rust VM 落地。
- **不做什么**：不改语言表面；不在 v0 做集合/ADT/类/泛型/闭包/String（String
  已由 S1 扩展）；不做
  JIT、不做动态方言的类型特化；不替换擦除式路径。

### 决策记录

| 日期 | 决策 | 说明 |
|---|---|---|
| 2026-11-22 | 类型来源采用 **T1** | 检查器在 AST 元数据中同时写 `type_obj`；改动小、`-t astm` 不变 |
| 2026-11-22 | v0 **不含 `String`** | 先把标量子集跑通；String 引入堆值，留作第一扩展 |
| 2026-11-22 | M1 之后先做 **M2 typed 解释器** | 用于语义差分与基准；typed 字节码（M3）等 M2 结果再定 |
| 2026-11-22 | CLI 增加 **`-t hir` + `-t thir`** | `hir` 为未类型化基线（诊断视图，格式非契约）；`thir` 为 typed dump；均属 M1 |
| 2026-11-22 | M2 执行目标 **`-t tvm`** | 直接执行受限 typed HIR（研究目标，暂不进 spec） |
| 2026-11-23 | **S1 扩展 String** | kind=1 v3；String 拼接/比较/`len`；Rust `TypedValue::Str(Rc<str>)`；集合留 S2/S3 |

## 1. 问题与目标

### 1.1 现状

`oort-core` 的类型在进入 HIR 前被**完全擦除**（spec 12、spec 13 的擦除边界）：

```text
源码 → 共享前端 → 方言语义分析（core 检查器）→ 擦除 → 统一 HIR → 字节码 → VM
```

后果：

- 后端只能看到统一的动态值（`OortType` 运行时对象 + tagged/boxed 值），
  类型只影响检查期诊断；
- 静态程序里的 `Int`/`Float`/`Bool` 仍走通用 `ADD`/`LT` 等动态指令，每个操作
  都要做类型判断与装箱；
- HIR/VM 无法利用“这个槽永远是 Int”“这个调用目标是静态函数”等信息，
  免装箱、直接调用、固定槽布局、决策树匹配都无从谈起；
- 这与 [design 02 §1.2–3.3](02-bytecode-vm-design.md) 的双轨设计（动态/静态
  专用操作码、类型守卫、边界调用）之间缺一层**具体的 typed IR 表示与 ABI**。

### 1.2 目标

1. 让静态方言的类型**存活到后端**，支撑：未装箱寄存器、静态调用、固定槽布局、
   模式匹配决策树、Rust VM 特化。
2. 保持现有语义与诊断不变；typed 路径与擦除路径在合法程序上输出一致。
3. 用最小垂直切片验证设计，避免在泛型/类布局未定时过早绑定 ABI。
4. 为性能路线图阶段 B 提供可度量的入口，而不是一次性大重构。

### 1.3 非目标

- 不引入新的语言表面特性（类型标注规则、检查算法保持不变）。
- 不在 v0 实现动态↔静态边界调用、blame 或 FFI（当前跨方言调用仍拒绝）。
- 不在 v0 实现 JIT、逃逸分析、SSA 优化或原生代码生成。
- 不要求动态方言 `oort-object` 获得类型特化；它是擦除路径的基线。

### 1.4 研究问题

| 编号 | 问题 |
|---|---|
| RQ1 | 类型应该由 typed HIR、typed 字节码，还是独立的静态 IR 承载？ |
| RQ2 | IR 类型模型如何表示，与检查器 `Type`、运行时 `OortType` 如何区分？ |
| RQ3 | 值/寄存器何时从 tagged 值转为未装箱表示？由谁保证类型安全？ |
| RQ4 | v0 是否允许任何跨方言边界？未来的守卫、装箱与 blame 如何接入？ |
| RQ5 | 如何验证 typed 路径与现有实现语义一致，且没有第二套类型推断？ |
| RQ6 | 最小可用子集是什么，每个里程碑的退出条件是什么？ |

## 2. 现状与约束

### 2.1 已实现基线

- **检查器**：局部双向检查 + 返回推断（design 14）；Primitive 严格相等、
  **无 Int→Float 隐式提升**；算术 `+ - * // %` 按“任一 Float 则 Float”，
  `/` 固定 Float（spec 11「表达式」）；没有静态 `Any`/`Object` 顶类型。
- **AST 元数据**：检查器目前把类型以 `describe_type()` **字符串**写入
  `node.metadata["type"]`（如 `List[Int]`、`(Int) -> Int`），供 `-t astm` 打印。
- **HIR**：线性寄存器、显式 `MOVE`、`CALL` 需要连续寄存器窗口；不携带类型
  （design 13、spec 12）。
- **字节码**：32 位 ABC/ABx/AsBx/Ax；`.obc` 头 `OBC | kind u8 | version u8`，
  `kind=0` 为擦除式，`kind=1+` 已预留给 typed（spec 13）。
- **边界**：跨方言调用仍显式拒绝；REPL 仍走 `eval`。

### 2.2 硬约束

1. **语义不变**：typed 路径不得改变合法程序的输出、返回值或错误类型。
2. **类型唯一来源**：检查器是唯一推断者；typed lowering 只消费结果并校验，
   不重新推断（否则两套规则必然漂移）。
3. **不静默执行未实现构造**：子集外必须显式拒绝或回退到明确的擦除路径。
4. **格式兼容**：v0 不改 `.obc`；typed 字节码一旦引入，必须用 `kind` 区分，
   不得复用 `kind=0` 的布局。
5. **可差分**：每个里程碑都要能与 `-t vm` / `-t eval` 做输出差分。

## 3. 先行研究

### 3.1 类型化 IR 的代表实现

| 系统 | 类型信息位置 | 控制流形态 | 对 Oort 的启示 |
|---|---|---|---|
| **Rust MIR** | 每个局部变量/操作数带类型；单态化在 codegen 前 | CFG + 显式 locals，非 SSA | 类型化 CFG IR 足够表达；单态化是代码生成阶段的事 |
| **Swift SIL** | 值带类型与所有权/地址语义 | 类 SSA，显式 load/store | typed IR 可以暴露低级操作，但不必一步到位 |
| **Dart Kernel** | 类型化 AST/IR；reified 泛型；JIT+AOT | 树/控制流混合 | 模块级 typed IR 可行；reified 泛型代价高，Oort 不必照搬 |
| **MLIR** | 多级 dialect，SSA 值带类型 | SSA | 分层 dialect 适合长期演进，但对玩具语言过重 |
| **Cranelift IR** | typed SSA，无 GC | SSA | 静态子集的合适原生后端目标 |
| **LLVM IR** | typed SSA（opaque pointers） | SSA | 远期原生后端；构建成本高 |

**提炼**：typed IR 不等于 SSA；MIR/SIL 都说明“类型 + 显式 locals + CFG”可以先
落地，SSA 留给优化/原生后端。Oort 的 typed HIR 应延续现有线性寄存器形态，
避免在 v0 重写控制流。

### 3.2 渐进类型与“先做子集”的先例

| 系统 | 策略 | 启示 |
|---|---|---|
| **Typed Racket** | 模块边界 + contract + blame | 边界设计可以后置，但必须预留 blame 语义 |
| **Reticulated Python** | 渐进类型的形式语义、cast/guard | 研究参考；运行时检查成本不可忽略 |
| **mypyc** | 类型化子集 → C，边界处装箱 | **先做受限子集**、逐函数迁移，是最接近 Oort 的工程路径 |
| **Cython** | 可选静态标注，局部 C 化 | 增量类型化可行，未标注部分保持动态 |
| **Numba** | 子集推断 → LLVM 特化 | 子集 + 单态化能带来数量级收益，但失败回退要清晰 |
| **Dart** | 健全类型系统 + `dynamic` 边界检查 | 边界守卫是健全性的关键，不是可选装饰 |
| **Hack / TypeScript** | 渐进迁移；TS 编译期擦除 | 擦除简单但无运行时保证；Oort 的 core 是“全静态模块”，可先不依赖擦除后的动态能力 |

**提炼**：mypyc 的“typed subset first”与 Oort 的模块级方言最接近；Typed Racket
与 Dart 提醒我们，边界与 blame 可以后置，但 typed IR 的**类型来源**必须一开始
就唯一、可验证。

### 3.3 动态语言的类型反馈与特化

| 系统 | 机制 | 启示 |
|---|---|---|
| **Truffle / Graal** | AST 解释 + 类型反馈 + 部分求值 | 动态方言若要特化，guard + 去优化是成熟路线 |
| **PyPy** | tracing JIT，热循环类型反馈 | 动态路径的优化可以晚于静态 typed IR |
| **V8** | Ignition 字节码 + IC + Sparkplug/Turbofan | 先 IC/反馈、后编译；不必一开始就 typed IR |
| **LuaJIT** | trace JIT | 对动态方言有效，但实现复杂度高 |

**提炼**：静态方言的 typed IR 与动态方言的类型反馈是两条独立的优化路线。
Oort 当前应只做前者；动态侧的内联缓存属于性能路线图阶段 A 的 Rust VM 设计
输入，不与 typed IR 混在一起。

## 4. 设计空间与选择

### 4.1 备选方案

| 方案 | 内容 | 语义风险 | Python 实现成本 | Rust/原生契合度 | 可度量性 |
|---|---|---|---|---|---|
| **A. Typed HIR** | 在现有 HIR 上附加结构化类型；字节码暂不变 | 低 | 低–中 | 中 | 高（可先跑解释器） |
| **B. Typed 字节码** | `kind=1`，类型化操作码/寄存器，入口守卫 | 中 | 中–高 | 高 | 高（但需先定 ABI） |
| **C. 独立静态 IR** | HIR 之后再降到 typed SSA，只服务原生后端 | 中 | 高 | 高（Cranelift/LLVM） | 中（远离现有 VM） |
| **D. 仅类型反馈/IC** | 不改 IR，在现有 VM 上做动态特化 | 低 | 中 | 高（Rust） | 高 |

### 4.2 推荐顺序

1. **A（v0）**：typed HIR + 受限子集 + 校验器 + typed 解释器。先证明类型来源、
   子集边界、差分测试与基准口径。
2. **B（v1）**：typed 字节码 `kind=1` + VM 类型化操作码 + 入口守卫；未装箱寄存器
   先在 Rust VM 落地（与性能路线图阶段 A 的 Rust VM v2 对接）。
3. **C（远期）**：静态子集 HIR → typed SSA → Cranelift/LLVM；对应性能路线图
   阶段 C。
4. **D（可选）**：动态方言的 IC/类型反馈，独立于 A/B/C，避免混淆两条路线。

**选择 A 作为第一版**的理由：

- 不触碰 `.obc` 与现有 VM，语义回归面最小；
- 可以在 Python 里快速做差分与基准，尽早暴露“类型来源字符串化”等问题；
- typed HIR 的验证器是 B 的前置：若 HIR 层都保证不了类型，字节码层只会更糟；
- 与 mypyc/Numba 的“子集先行”经验一致。

## 5. v0 受限子集（提案）

### 5.1 语言子集

只接受满足以下条件的 `#lang oort-core` 单模块程序；任一条件不满足则**不使用**
typed 路径（研究阶段用显式 target/标志，正式集成时由编译器选择并记录路径）。

- **声明**：顶层 `def` 函数；参数必须标注；返回标注可写可省（沿用 design 14
  的返回推断）；函数体内 `val`/`var` 必须初始化、单目标。
- **类型**：`Int`、`Float`、`Bool`、`Unit`。**v0 不含 `String`**（引入堆值，
  留作第一扩展；2026-11-23 已由 S1 扩展，见下文「扩展计划」）。
- **表达式**：整/浮点/布尔字面量；变量；`+ - * // % /`；一元 `+ - not`；
  比较 `== != < <= > >=`；`and`/`or`；`if/else`；块；直接调用顶层函数；
  `print`（标量 → Unit）。
- **语句**：声明、赋值、表达式语句、`return`、`if`、`while`。
- **允许**：直接递归（`fact`/`fib`）、多函数调用、早返回。
- **排除**：集合、Tuple、String、ADT/`match`、类/接口/继承、泛型、lambda/
  函数值/高阶函数、模块导入、`break`/`continue`、`for`、`Unit` 作为变量类型。

### 5.2 语义基线

- 完全沿用现有检查器与当前 VM 的语义：Primitive 严格相等、无隐式提升；
  `+ - * // %` 的混合规则与 `/` 固定 Float 按 spec 11；`1 == 1.0` 允许；
  除零等运行时错误保持现状。
- v0 不新增诊断；类型错误仍由检查器报告，typed lowering 只对“检查器已通过
  但 IR 不满足子集”的情况给内部/显式错误。

### 5.3 为什么先做标量

- 标量子集已覆盖 fib/loop/调用等性能门禁工作负载，足以验证 typed IR 的价值；
- 不需要先决定 ADT 布局、类槽偏移、泛型单态化等长期 ABI；
- String/集合是堆值，会立刻牵出 GC 与逃逸分析；放到表示层稳定之后；
- mypyc/Numba 的经验：子集越小，类型来源与失败回退越容易验证。

## 6. v0 设计草案

### 6.1 Typed HIR 数据模型

在现有 HIR 形态上增加类型表面，不改指令语义：

```text
TypedFunction
  name, params: [(register, IrType)], ret: IrType
  register_types: [IrType]        # 每个虚拟寄存器的静态类型
  code: [TypedInstr]              # 操作数寄存器有类型，指令本身不变
```

- 指令仍用现有 HIR 操作（`ADD`、`LT`、`CALL`、`JUMP`…），v0 不新增 typed
  opcode；类型用于**校验与后续特化**。
- 每个寄存器在函数内类型固定；分支合流处要求同一寄存器类型一致（检查器已
  保证，验证器复核）。
- 调用签名来自被调函数的 typed 签名；直接调用在 v0 只允许顶层函数。

### 6.2 IR 类型

- 新增后端专用的 `IrType`（v0：`Int|Float|Bool|Unit` 枚举），**不复用**
  前端 `Type` 对象，也不复用运行时 `OortType`。
- 理由：前端类型会演进（ADT/泛型/接口），运行时类型服务动态值；IR 类型是
  后端 ABI 的稳定投影。三者之间在 lowering 时做显式映射。
- 长期扩展：`IrType = Primitive | Nominal(id, args) | Function(...)`；
  泛型在静态侧单态化后再进入 IR（design 03 §2）。

### 6.3 类型来源（关键决策）

当前检查器只写 `metadata["type"] = describe_type(...)` 字符串。typed lowering
**不能**解析字符串。建议二选一：

| 方案 | 做法 | 评价 |
|---|---|---|
| **T1. 元数据携带结构化类型** | 检查器同时写 `metadata["type_obj"] = Type` | 简单；需保证所有节点都写 |
| **T2. 检查器产出 typed 结果表** | 以 `(node_id → Type)` 侧表返回 | 干净；需要节点稳定 ID |

**选定 T1（2026-11-22）**：改动小，`-t astm` 仍用字符串；typed lowering 要求
每个表达式节点都有 `type_obj`，缺失即显式失败。T2 作为备选保留在案，若后续发现
元数据覆盖不全再评估。无论选哪个方案，**检查器是唯一推断者**。

**记录点（M1 已实现）**：

| 记录点 | 触发路径 | 覆盖与记录的类型 |
|---|---|---|
| `post_process` | 所有 `node.accept(self)` | visitor 直接分派的表达式/语句；记录 visitor 返回的原始类型 |
| `_check_expr` 包装 | 显式 `_check_expr` 调用 | 块/体最后一条语句、初始化器、赋值、`return`、实参、match arm、下标、集合元素；记录期望收敛后的最终类型 |
| `_check_block_expected` 包装 | 带期望类型的 `BlockExpr` | `if`/`else` 块与表达式位置块 |
| `_check_function_body` | 函数/lambda 体（`_check_statements_expected`） | 体块类型（`body_type`） |
| `visit_module` | 模块体（`_check_statements`） | 模块体块类型 `Unit` |

**已知缺口**：类体块与类方法 `FunctionDef` 走 `visit_class_def` 专用路径，当前
不记录；v0 不含类，扩展到类之前补齐。类型标注语法（如 `(Int) -> Int` 解析出的
`->` `BinaryExpr`）不是值表达式，不需要 `type_obj`；typed lowering 读取的是
签名中的 `FunctionType`。

### 6.4 Lowering 与验证

- 新增 `lower_typed_module(ast)`：在语义分析后运行，只为子集程序产出
  `TypedModule`；子集外抛显式错误，不静默降级。
- 现有 `lower_module(ast)` 保持不变，动态方言与子集外程序继续使用。
- **验证器**检查：
  1. 每条指令的源/目标寄存器均有类型；
  2. 指令操作数类型符合规则（如算术只接受数值，`and` 只接受 Bool）；
  3. 调用实参与签名匹配，返回类型一致；
  4. 分支合流处寄存器类型一致；
  5. 无 `Unknown`/`Never` 进入 IR。
- 新增 `-t hir`（未类型化基线，复用现有 `format_module`）与 `-t thir`（typed
  HIR，带 `IrType` 注解），便于评审、diff 与快照测试。

### 6.5 执行策略

- **M2 先做 typed HIR 解释器**（Python），只执行子集：用于语义差分与基准，
  不作为长期后端（2026-11-22 选定；不采用“直接降到现有字节码”的替代路径）。
- **M3 再降到 typed 字节码 `kind=1`**：类型化操作码（`ADD_I`/`ADD_F`/`LT_I`…）、
  入口 `GUARD_*`、必要时 `BOX`/`UNBOX`；v0 子集内无动态边界，守卫可只做
  防御性检查。
- **M4 才做未装箱值**：Rust VM 的帧槽按 `IrType` 布局（Int 用 i64/Smi，
  Float 用 f64，Bool 用 tag/bit），与 design 01 的 tagged pointer 方案对接；
  Python 侧保持装箱，只验证 ABI。

### 6.6 边界策略

- **v0：无跨方言边界**。typed 路径只处理完整落在子集内的 core 程序；跨方言
  调用按现状拒绝。
- **后续**：静态模块导出/导入使用 design 02 §3.3 的 `CALL_BOUNDARY` +
  `BOX`/`UNBOX`；入口 `GUARD_TYPE`；失败按 design 03 §4.4 的 blame 规则归责
  调用方。边界语义应单独成文（未来 OP），不混入 v0。
- `oort-core` 内部没有 `Any`/`Object`；`Unknown` 只是检查器的错误恢复类型，
  绝不能出现在 typed IR 或运行时。

## 7. 研究假设与验证方法

| 假设 | 验证方法 | 失败信号 |
|---|---|---|
| H1：typed lowering 可复用现有 HIR 形态，新增代码少 | M1 代码量/结构评审；现有 HIR 测试不变 | 需要重写控制流或大量复制指令 |
| H2：检查器可单点提供结构化类型 | M1 检查所有表达式节点有 `type_obj`；缺失统计 | 需要 lowering 再推断/解析字符串 |
| H3：typed 解释器在标量子集上与 VM 输出完全一致 | M2 差分：同一程序三种路径 stdout/返回值/退出码 | 任一差异即为语义 bug |
| H4：typed 路径在标量循环上有可测收益 | M2 微/宏基准 vs 现有 VM；记录宿主开销占比 | 收益被 Python 宿主淹没 → 直接进 M3/Rust |
| H5：typed 字节码可在不改 `kind=0` 的前提下增量引入 | M3 `.obc` round-trip、kind 拒绝测试 | 需要修改现有格式或 VM 语义 |

**基准口径**：沿用 `benchmarks/` 的 fib/loop/methods 工作负载；typed 路径的
目标不是立刻超过 CPython，而是与现有 VM 对比时解释**收益来自哪里**（类型分发、
装箱、直接调用）。真正的量级目标留给 Rust/typed 字节码（性能路线图阶段 A/B）。

## 8. 里程碑

| 里程碑 | 范围 | 退出条件 |
|---|---|---|
| **M0 研究** | 本文；确定 `IrType`、类型来源（T1/T2）、子集边界 | 设计评审通过；开放问题收敛 |
| **M1 Typed HIR** | 数据模型、`lower_typed_module`、验证器、`-t hir` 基线与 `-t thir` dump；仅标量子集 | 快照测试；子集外显式拒绝；现有擦除路径零改动 |
| **M2 Typed 解释器** | 执行 typed HIR；差分与基准（M1 后的选定路径） | 与 `-t vm`/`-t eval` 输出一致；基准报告 |
| **M3 Typed 字节码** | `kind=1`、类型化操作码、入口守卫、`-t tbc` | round-trip、kind 拒绝、与 M2 语义一致 |
| **M4 未装箱/Rust** | Rust VM 消费 `kind=1`；帧槽按类型布局 | 标量门禁 ≤2× CPython；交给性能路线图阶段 A/B 合并评估 |

每个里程碑都必须：更新 spec（仅当行为对外可见）、补差分测试、更新
`benchmarks/RESULTS.md` 或研究笔记，且**不删除**擦除式路径。

### M1 实现状态（2026-11-22）

- 已实现 `-t hir`（未类型化基线）与 `-t thir`（typed dump）；
- 新增 `src/oort_lang/hir/typed.py`：`IrType`、`TypedFunction`/`TypedModule`、
  `lower_typed_module`、`validate_typed_module` 与 typed dump；
- 类型来源 T1：检查器在表达式、函数签名、声明目标与赋值目标上写 `type_obj`；
  调用目标（含内建 `print`/`len`）也显式记录——core 检查器不会把 callee Name
  当作普通表达式访问；
- 复用共享 `HirLowerer`，通过子类包装 `_lower_expr` 记录寄存器类型；不复制
  lowering，擦除路径零改动；
- prelude 注入的合成 enum 在 typed 路径中被过滤；`Never` 映射为当前函数的
  返回类型（bottom，仅用于不可达值）；显式尾 `return` 后不再追加不可达的
  Unit return；
- v0 边界：单模块、标量、顶层函数与表达式语句；拒绝顶层 `val`/`var`、
  String/集合/ADT/类/泛型/lambda/模块导入/`for`/`break`/`continue`；
- 新增验收样本 `examples/08_core/08_15_typed_subset.ort`：覆盖递归、循环、
  早返回、混合算术、布尔逻辑、`Unit` 函数，`-t thir` 可接受且 VM/eval 输出
  一致；
- 验证：全量测试 1252 passed（含 8 个 typed HIR 测试），ruff/mypy 与
  `mkdocs --strict` 通过。

### M2 实现状态（2026-11-22）

- `-t tvm` 直接执行 `TypedModule`（`src/oort_lang/hir/typed_exec.py`），复用
  运行时值与 `apply_binary`/`apply_unary`，保证与 `-t vm`/`-t eval` 同语义；
- main 的返回类型取最后一条 `Return` 寄存器的类型，因此顶层表达式值可返回；
- 差分测试：验收示例（`08_15`）与内联 fib、早返回、`while` 程序三种路径输出
  一致；子集外程序在 `-t tvm` 下同样显式拒绝；
- 初步测量（本机 Python 宿主，5 次中位数）：fib(20) **442.5 ms** vs VM
  **346.6 ms**（1.28× 慢）；loop 20000 **352.6 ms** vs **164.0 ms**（2.15×
  慢）。typed HIR 在 Python 宿主上不带来性能收益——这符合预期，M2 只验证
  语义与类型来源；真正的收益需要 M3 的 typed 字节码与 M4 的未装箱/Rust 值表示。

### M3 实现状态（2026-11-22，第一切片）

- 新增 typed 字节码：`bytecode/typed_opcodes.py`（独立 opcode 命名空间）、
  `typed_compile.py`（`TypedModule` → `TypedProgram`）、`typed_vm.py`（boxed
  值的 typed VM）、`typed_disasm.py`；
- 类型化操作码：`ADD_I/F`、`SUB_I/F`、`MUL_I/F`、`DIV_F`、`FLOORDIV_I/F`、
  `MOD_I/F`、比较/相等（`EQ_I/F/B` 等）、`NEG_I/F`、`POS_I/F`、`NOT_B`、
  `TO_FLOAT`；混合 Int/Float 运算插入 `TO_FLOAT`；`CALL` 使用 base/args/dst
  窗口；函数入口按 `param_types` 做守卫；
- CLI：`-t tbc` 打印 typed 反汇编；`-t tvm` 改为执行 typed 字节码；typed HIR
  解释器保留用于差分测试；
- `.obc` **kind=1** 序列化/读回（`bytecode/typed_serialize.py`）：携带常量、
  字/位置表、寄存器类型、参数/返回类型；kind 0 与 kind 1 互斥拒绝；格式见
  [spec 14](../spec/14-typed-bytecode.md)；
- 验证：typed 字节码、typed HIR 解释器与现有 VM 在示例及内联 fib/while/
  早返回程序上输出一致；round-trip 后再执行结果一致；
- **尚未做**：Rust VM 消费 kind=1、动态边界守卫、格式稳定化并纳入 spec；
- 初步测量（本机，5 次中位数）：fib(20) **560.0 ms** vs VM **345.1 ms**
  （1.62× 慢）；loop 20000 **382.1 ms** vs **162.0 ms**（2.36× 慢）。typed
  字节码比 typed HIR 略慢（解码 + 类型断言），符合 M3 只验证 ABI 的定位。

### M4 入口（2026-11-22）

- Rust VM 现在按 `.obc` kind 分派：kind=0 走 `obc::read_module`/`vm::Vm`，
  kind=1 走 `typed::read_typed_module`/`typed::TypedVm`
  （`rust/oort-vm/src/typed.rs`）；
- typed 标量子集执行已打通：typed opcodes、`TO_FLOAT`、CALL 窗口、入口守卫；
  值仍是 boxed `vm::Value`，未装箱留到后续；文件格式见
  [spec 14](../spec/14-typed-bytecode.md)；
- `scripts/rust_vm_check.py` 增加 typed differential（4 个 core 程序），与
  Python typed VM 的 stdout 全部一致；
- `benchmarks/typed_run.py` + `typed_report.py` 把 typed 路径接入
  `benchmarks/RESULTS.md` §6（研究快照，不进门禁）；
- 初步测量（本机，exec 口径，5 次中位数）：Rust typed **fib(20) 5.8 ms /
  loop 20000 1.2 ms**；同机 Python typed 字节码 VM 为 **631.6 / 432.7 ms**，
  kind=0 VM 为 **358.1 / 215.8 ms**。Rust typed 比 kind=0 VM 快约
  62–186×（boxed 值仍是 spike 表示）；
- **尚未做**：未装箱寄存器、动态边界；`exec_ms` 已接入 RESULTS §6。

### M4 剩余设计：未装箱值（2026-11-22 草案）

> 数值语义（Int 精度/溢出、Float 与混合比较）见
> [design 16](16-numeric-semantics.md)。U1 的 `i64` 只是 spike 表示，不是
> 最终语言语义。

现状：typed 字节码已携带寄存器类型，但 Python/Rust typed VM 仍使用 boxed
`OortObject`/`Value`。目标是让 Rust typed VM 的标量寄存器不再分配堆对象，
测量 typed ABI 能达到的上限；**不改变 `.obc` kind=1 格式与语言语义**。

#### 值表示备选

| 方案 | 内容 | 评价 |
|---|---|---|
| **A. 单一 `TypedValue` enum（推荐先做）** | `Int(i64)` / `Float(f64)` / `Bool(bool)` / `Unit` / `Function(index)` / `Native` | 无 Rc/RefCell、无堆分配；转换只发生在 native/边界；实现量小 |
| B. 分类型寄存器 bank | Int/Float/Bool 分开存放 | 编译期/ABI 更复杂，留作 U3 |
| C. NaN-boxing / Smi | 与 design 01 的长期值表示对齐 | 需要 GC/HeapInt 配套，Rust spike 阶段不引入 |

**推荐 A**：先把 typed VM 的标量路径做到零分配，量化收益；B/C 与 Rust VM v2
的正式值表示一起评估。

#### 寄存器与 frame

- 每帧 `Vec<TypedValue>`，长度 `register_count`，初始化为 `Unit`；
- 保留 proto 的 `register_types` 用于验证/调试；运行时分派依赖 opcode，
  不依赖类型表；
- 局部槽、临时寄存器与 CALL 窗口保持现有布局，ABI 不变。

#### 运算、守卫与边界

- typed opcode 直接匹配 `TypedValue` 变体；不匹配即显式运行时错误；
- 函数入口按 `param_types` 做 O(1) 守卫；
- `Int` 用 `i64`（溢出报错，spike 限制）、`Float` 用 `f64`、`Bool` 用 `bool`、
  `Unit` 无载荷；
- `print` 是当前唯一的 native 边界：`TypedValue` → 主机字符串；格式必须与
  Python `float_repr`/`display` 完全一致；
- 动态↔静态边界（box/unbox/blame）仍不在 U1：跨方言调用继续显式拒绝，
  未来单独设计。

#### 不影响

- `.obc` kind=1 格式不变（version=1），不需要重新序列化；
- Python typed VM 可继续使用 boxed 值（参考实现/差分基线）；
- spec 14 只补一句“内部值表示由实现决定”，不改文件布局。

#### 里程碑

| 里程碑 | 范围 | 退出条件 |
|---|---|---|
| **U1** | **仅 Rust**：`TypedValue` + 标量运算/比较 + print 转换；混合比较精确化（`EQ_MIXED`/`CMP_MIXED`）；Python typed VM 保持 boxed baseline | typed differential 全过；Rust 单测覆盖浮点格式/混合比较/守卫 |
| **U2** | 基准与 RESULTS §6 更新 | fib20/loop20000 exec_ms 明显优于 boxed 基线（5.8/1.2 ms），数据入 RESULTS |
| **U3（可选）** | 分 bank 或 NaN-boxing/Smi | 与 Rust VM v2/design 01 合并评估，不单独承诺 |

#### 风险与开放问题

- `Float` 输出格式必须与 Python 完全一致（`2.0`、`-0.0`、指数形式）；
- `i64` 溢出 vs Python 任意精度：spike 限制，差分测试避免溢出；正式 ABI 需
  HeapInt/BigInt；
- 未初始化寄存器用 `Unit` 可能掩盖 bug，可在验证/调试模式加断言；
- 动态边界与 box/unbox 的 blame 语义留到 FFI 设计，不与 U1 混合；
- 性能口径保持 exec_ms（wall 扣空程序启动），不把启动混入。

### M4-U1 实现状态（2026-11-22）

- Rust typed VM 的标量寄存器改为未装箱 `TypedValue`（`Int(i64)`/`Float(f64)`/
  `Bool(bool)`/`Unit`/`Function(index)`/`Native`）；无 `Rc`/`RefCell`、标量无堆分配；
- 只在 `print` 与主结果边界转换；Python typed VM 保持 boxed 作为差分 baseline；
- 混合比较新增 `EQ_MIXED`/`NE_MIXED`/`LT_MIXED`/`LE_MIXED`/`GT_MIXED`/
  `GE_MIXED`，按数学值精确比较；typed 字节码 `version` 提升到 2；Python typed
  VM 也实现这些 opcode（仍 boxed）；
- Rust `float_repr` 改为与 Python `repr(float)` 对齐（指数符号/两位指数）；
- 验证：Rust 单测 11 passed；typed differential 6 个程序全过（含 2^53 混合比较
  与浮点显示）；Python 全量 1268 passed；
- 初步测量（exec 口径，同一轮）：未装箱 Rust **fib(20) 4.7 ms / loop 20000
  0.9 ms**；同轮 kind=0 VM 为 **467.7 / 196.2 ms**；相对此前 boxed Rust 基线
  （5.8 / 1.2 ms）有改善，loop 更明显。fib 仍受每次调用的帧分配与全局名查找
  限制，留作 U2 优化输入（不是 U1 的范围）。

### M4-U2 计划：调用路径（2026-11-23）

目标：在**不改 `.obc` 格式、不改语义、不引入 unsafe/第三方依赖**的前提下，
降低 typed VM 的调用开销。fib 是主要受益者；loop 的调用少，预期变化小。

| 步骤 | 内容 | 解决的热点 |
|---|---|---|
| **U2a 全局预解析** | VM 加载时为每个 proto 建 `globals: Vec<Option<TypedGlobal>>`（Function/Native）；`LOAD_G Bx` 变成数组索引 | 当前每次 `LOAD_G` 都 `String` 分配 + `HashMap` 哈希查找 |
| **U2b 参数直拷 + 帧池** | `CALL` 不再 `to_vec()`；`call` 直接读调用者寄存器切片，复制到复用的 frame；frame 池 warmup 后零分配 | 每个调用两次 `Vec` 分配（参数 + callee 帧） |
| **U2c（可选）** | 连续寄存器栈 / 预解码指令 | 进一步降低分配与解码开销；B 方案安全版先用帧池验证 |

非目标：不改 `TypedValue` 表示、不优化 `print`/错误路径、不把 checked 算术换成
wrapping、不引入 `unsafe` 或外部 crate。

验收：typed differential 六例不变；`fib` 的 exec_ms 明显下降；RESULTS §6
重新生成；Rust 单测覆盖全局解析/帧复用（错误路径仍显式报错）。

### M4-U2 实现状态（2026-11-23）

- **U2a 全局预解析（带版本化失效）**：`ResolvedProto` 为每个常量下标保存
  `Cell<Option<CachedGlobal>>`；`LOAD_G` 命中当前 `GlobalTable.version` 时
  直接取缓存，失效时按名字重新解析并写回。`TypedVm::invalidate_globals()`
  供未来的 `STORE_G` 调用；当前 typed 子集无全局写，版本保持 0；
  - `LOAD_G` 热路径仍是数组访问 + 一次版本比较；缓存条目是 `Copy` 小结构，
    不使用 `RefCell`/`unsafe`；
- **U2b 调用帧复用**：`CALL` 直接传调用者寄存器切片，不再 `to_vec()`；
  `FramePool` 以 LIFO 复用帧，`acquire` 时 `clear` + `resize` 重置；
  参数守卫在取帧前完成，执行后用 `release` 归还（错误路径帧被 drop，
  不泄漏但不复用）；
- 未做 U2c（连续寄存器栈/预解码）；未改 `.obc`、`TypedValue` 与语义；
- 验证：Rust 单测 13 passed（新增全局解析、帧池复用）；typed differential
  六例全过；
- 测量（exec 口径，同一轮）：Rust **fib(20) 1.4 ms / loop 20000 0.4 ms**；
  U1 为 4.7 / 0.9 ms，kind=0 VM 为 400.3 / 251.5 ms。fib 约 3× 改善，
  符合“调用路径”预期；loop 变化小（调用少）。
- **U2a/U2b 分离 A/B**（40 次交错，exec 中位数）：fib(20) U1 **5.28**、
  U2a **2.60**、U2b-only **3.44**、U2a+U2b **1.47 ms**；loop 差异在噪声内。
  结论：U2a 单独约 2×，U2b 单独约 1.5×，组合约 3.6×。
- **版本化缓存开销**（80 次交错，fib20）：U2a+U2b **1.605 ms** vs 加版本检查
  **1.655 ms**，约 3%，在噪声范围内；保留版本化失效机制。
- **U2a 不限制 `.obc` 格式**：预解析发生在 VM 加载阶段，文件仍携带名字常量；
  若未来 kind=1 加入可变全局/`STORE_G`，应由 VM 失效缓存或改用版本化查找，
  而不是修改格式。当前 typed 子集无全局写，因此预解析是安全且可逆的实现
  选择。

### 扩展计划：String 与集合（2026-11-23）

按堆值复杂度分阶段，每阶段都保持差分可执行：

| 阶段 | 范围 | 状态 |
|---|---|---|
| **S1 String** | `IrType.STRING`；`ADD_S`/`EQ_S`/`*_S`；`len` native；`TypedValue::Str(Rc<str>)`；kind=1 **v3** | **已完成** |
| **S2 List / Tuple** | 递归类型描述 + 类型表；`NEW_LIST`/`NEW_TUPLE`/`GET_ITEM`/`LEN`；`for` 迭代；Tuple 不可变；List 可变（语言表面待开放） | **已完成（S2a + S2b）**；`SET_ITEM` 因核心检查器限制只预留 opcode |
| **S3 Set / Dict** | `NEW_SET`/`NEW_DICT`、Dict 下标读取、`len`、深相等、`for` 迭代；键相等用线性查找，不实现哈希 | **已完成（不可变集合）**；写入/`in`/集合运算受核心语言表面限制 |
| **S4 ADT** | 构造器/`match`/布局；依赖集合与类型表的稳定 | **S4a 完成；S4b 完成（reified 泛型 + 复杂模式）**；S4c 优化待做；见 [design 18](18-typed-adt.md) |

泛型类型表示的跨语言调研与 Oort 取舍见
[design 03 §2.5](03-type-system-design.md)。S2/S3 只存具体类型；
`TypeParam`/`Forall`/`App(Nominal, args)` 等到实现泛型时再进类型表。
跨方言调用与 FFI 的设计见 [design 17](17-boundary-ffi.md)；ADT 的 typed
方案见 [design 18](18-typed-adt.md)。

**内存回收（S2/S3）**：List/Tuple/Set/Dict 在当前类型系统下是有限的——没有
递归名义类型、没有 typed 闭包，结构容器无法引用自身；Rust typed VM 继续用
`Rc`/`RefCell`，依靠引用计数释放，**不需要 GC**。当 S4（类/递归 ADT）或
typed 闭包引入后，`Rc` 环会泄漏，必须在 Rust VM v2 / design 01 的值表示
设计中一并决定 GC（tracing 或 cycle collector），不要在 S2/S3 临时引入。
动态 kind=0 Rust VM 已存在环泄漏，属于 spike 限制。

S1 的约束与实现：

- Python 参考实现使用 `OortString`（boxed），Rust 使用 `Rc<str>`（非 `Copy`，
  寄存器/帧改为 `Clone`）；转换只发生在 `print`/`len` 与主结果边界；
- `len` 是 native 调用，返回字符数（Rust `chars().count()`，与 Python 一致）；
- 格式 v3 只新增类型 tag 6 与字符串 opcode，寄存器类型表仍是每寄存器一字节；
- String 索引/切片暂不做（需要 `GET_ITEM`/`BUILD_SLICE`，留到 S2 一并设计）；
- 集合阶段需要把类型表从“每寄存器一字节”升级为**递归类型描述表**，届时
  再提升 kind=1 version。

### S2 实现状态：List / Tuple（2026-11-23）

- **类型表 v4**：`TypedProto` 增加 `types`（后序、去重）、寄存器/参数/返回的
  类型 ID；`ContainerType` 表示 `List[T]`/`Tuple[...]`；kind=1 `version=4`；
- **Python**：`OortList`/`OortTuple`；`NEW_LIST`/`NEW_TUPLE`/`GET_ITEM`/
  `EQ_LIST`/`NE_LIST`/`EQ_TUPLE`/`NE_TUPLE`；深相等复用运行时
  `values_equal`；`len` 对 String/List/Tuple 生效；
- **Rust**：`TypedValue::List(Rc<RefCell<Vec<TypedValue>>>)`、
  `TypedValue::Tuple(Rc<[TypedValue]>)`；`Value::Tuple` 用于主结果转换；
  深相等、下标（含负索引）、`len`、`print` 格式对齐 Python；
- **S2a 范围**：List/Tuple 字面量、下标读取、`len`、深相等、打印；
- **S2b 范围**：List/Tuple（元素齐次）/String 的 `for` 迭代；新增
  `IrType.ITERATOR`、类型 tag 11、`OPEN_ITER`/`ITER_NEXT`（opcode 66/67）；
  迭代器是快照，与动态运行时的 `OortIterator` 语义一致；
- **`SET_ITEM`（opcode 68）只预留、不发出**：`oort-core` 核心检查器目前
  禁止下标赋值（“只有普通名字和类槽可赋值”），List 原地修改需要单独的语言
  表面决策/提案，不能由 typed 路径偷偷放宽。Rust/Python typed VM 已实现该
  opcode 的解释，便于提案通过后直接接入；
- **类型/降低细节**：共享 HIR 的 `_lower_for` 分配的迭代器/元素寄存器不经过
  `_lower_expr`，typed lowerer 在降低后做一次控制寄存器类型推断
  （`OpenIterator` → `Iterator`，`IteratorNext` → 元素类型）；
- 验收样本 `examples/08_core/08_16_typed_collections.ort`（`-t tvm` 与 `-t vm`
  输出一致）；typed differential 新增 `typed_iteration`（List/Tuple/String）；
  Python typed 单测 28 passed；Rust 单测 14；ruff/mypy/mkdocs 通过。

### S3 实现状态：Set / Dict（2026-11-23）

- **类型表**：`ContainerType` 支持 `Set[T]`/`Dict[K,V]`，复用 v4 的 tag 8/9；
  `TypedType`/`ContainerType` 的递归描述保持不变；
- **Python**：`OortSet`/`OortDict`；`NEW_SET`/`NEW_DICT`（opcode 69/70）、
  Dict `GET_ITEM`、`EQ_SET`/`NE_SET`/`EQ_DICT`/`NE_DICT`（71–74）；深相等复用
  `values_equal`；`len`、`for`、`print` 复用运行时语义；
- **Rust**：`TypedValue::Set(Rc<RefCell<Vec<TypedValue>>>)`、
  `TypedValue::Dict(Rc<RefCell<Vec<(TypedValue, TypedValue)>>>)`；键查找与去重
  用 `typed_equal` **线性扫描**；`Value::Set`/`Value::Dict` 仅用于主结果转换；
- **顺序语义**：**Dict 保证插入顺序**（与 Python dict、现有打印测试一致）；
  Set 的迭代/打印顺序不属语言保证。Rust Set 当前按插入顺序存储，但不把它写成
  契约；
- **不做 `std::HashMap`**：裸 `HashMap` 丢失 Dict 插入顺序，且要求键满足
  `Eq + Hash`；Oort 键语义包含 Float/NaN、Tuple 结构相等与后续的 ADT/类键，
  不能无损压成 `Eq`。S3 以语义对齐为先，使用有序 `Vec` + 线性查找；未来若
  基准证明需要 O(1)，再换 `IndexMap` 或“Vec 顺序 + 自建哈希索引”，并单独定义
  规范化键与 NaN 规则；
- **范围**：Set/Dict 字面量、Dict 下标读取、`len`、深相等、`for` 迭代（Set
  元素、Dict 键）、`print`；空字面量沿用检查器要求类型标注；
- **未做**：`d[k] = v`/Set 增删（核心检查器仍禁止下标赋值）、`in`/集合交并差
  （核心语言表面尚未支持）、ADT/类作为键（S4）、切片；
- 验收样本 `examples/08_core/08_17_typed_sets_dicts.ort`；typed differential
  新增 `typed_sets_dicts`；Python typed 单测覆盖 OBC round-trip；Rust 单测
  覆盖插入顺序、键去重与无序相等。

## 9. 风险与开放问题

1. **类型来源漂移**：若 lowering 重新推断或解析字符串，规则必然与检查器分叉。
   必须单点来源（T1/T2）。
2. **双路径维护**：typed HIR/解释器/字节码会增加维护面。对策：子集严格、
   共享前端与 HIR 结构、定期用差分测试钉住语义。
3. **子集蔓延**：每加一个特性（String→集合→ADT→类）都会引入布局/GC/ABI
   决策。对策：每个扩展单独提案，先定表示再扩语法。
4. **泛型**：擦除 vs 单态化（design 03 §2 已倾向静态单态化 + 动态擦除）；
   typed IR 先不做泛型，避免过早绑定。
5. **边界与健全性**：动态↔静态的守卫、装箱与 blame 是独立研究项；v0 不碰。
6. **未装箱整数**：Smi 范围、溢出到 HeapInt/BigInt、与 `==` 语义的交互
   （design 01 §3）。
7. **调试信息**：typed 字节码的行号/寄存器映射需要新的调试表设计。
8. **`.obc` ABI**：`kind=1` 的稳定性、版本策略、与 Rust VM 的兼容窗口。
9. **执行策略选择**：M2 是否值得做 typed 解释器，还是直接降级到现有字节码
   并只做验证？前者便于测语义，后者代码少；需 M1 后评估。
10. **`-t` 目标命名**：已定 M1 增加 `-t hir` 与 `-t thir`；`-t tbc` 待 M3。

## 10. 结论与建议

- **推荐路线**：A（typed HIR，受限标量子集）→ B（typed 字节码 `kind=1`）→
  C（静态 SSA/原生），与性能路线图阶段 B/C 对齐；D（动态 IC）独立推进。
- **第一版只做 M1**：typed HIR 模型 + 验证器 + dump，不改执行路径。它是所有
  后续工作的地基，也是检验“类型来源唯一”的最小实验。
- **成功标准**：M1 能对子集程序产出可校验的 typed HIR，子集外显式拒绝，现有
  擦除路径与测试零回归；M2 差分一致并能解释性能差异。
- **失败/转向信号**：若 M1 发现必须重写 HIR 控制流、或检查器无法单点提供
  结构化类型，则应先修检查器/IR 基础，而不是继续扩展 typed 路径。

## 11. 参考资料

Oort 内部：

- [spec 12：HIR、字节码与寄存器 VM](../spec/12-hir-bytecode-vm.md)
- [spec 13：字节码序列化（`.obc`）](../spec/13-bytecode-serialization.md)
- [spec 11：oort-core 薄探针](../spec/11-core-probe.md)
- [design 01：运行时值表示](01-runtime-value-representation.md)
- [design 02：字节码 VM 设计](02-bytecode-vm-design.md)
- [design 03：类型系统设计](03-type-system-design.md)
- [design 13：HIR 设计](13-hir-design.md)
- [design 14：oort-core 类型检查与推断](14-core-typechecking.md)
- [OP 0005：类型系统](../proposals/0005-type-system.md)
- [OP 0022：泛型 ADT](../proposals/0022-generic-adts.md)
- [OP 0023：完整模式匹配](../proposals/0023-full-pattern-matching.md)

外部（阅读清单）：

- Rust MIR：<https://rustc-dev-guide.rust-lang.org/mir/index.html>
- Swift SIL：<https://github.com/swiftlang/swift/blob/main/docs/SIL.rst>
- Dart Kernel：<https://github.com/dart-lang/sdk/tree/main/pkg/kernel>
- MLIR：<https://mlir.llvm.org/>
- Cranelift：<https://github.com/bytecodealliance/wasmtime/tree/main/cranelift>
- LLVM Language Reference：<https://llvm.org/docs/LangRef.html>
- Typed Racket：<https://docs.racket-lang.org/ts-guide/>
- mypyc：<https://mypyc.readthedocs.io/>
- Cython：<https://cython.readthedocs.io/>
- Numba：<https://numba.pydata.org/>
- Dart 类型系统：<https://dart.dev/language/type-system>
- Hack 类型系统：<https://docs.hhvm.com/hack/types/type-system>
- V8 博客（IC/Sparkplug/Turbofan）：<https://v8.dev/blog>
- PyPy：<https://www.pypy.org/>
- LuaJIT：<https://luajit.org/>
- Tobin-Hochstadt & Felleisen, *The Design and Implementation of Typed Scheme*
  (POPL 2008)；Vitousek et al., *Design and Evaluation of Gradual Typing for
  Python* (DLS 2014)；Würthinger et al., *One VM to Rule Them All* (Onward! 2013)。
