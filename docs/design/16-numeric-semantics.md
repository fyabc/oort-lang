# 数值语义设计（Int / Float）

> **状态**：设计决策（2026-11-22，D1–D6 已定；实现随 M4 U1 推进）。
> 本文定义语义与实现约束，不改变当前已实现的行为；
> [spec 11](../spec/11-core-probe.md) 仍是已实现行为的规范。
> 关联：[design 01](01-runtime-value-representation.md) 的整数阶梯、
> [design 15](15-typed-ir.md) 的 typed 字节码与 M4、[spec 13](../spec/13-bytecode-serialization.md)
> 的常量编码。

## 1. 问题

当前实现里，`Int` 的含义在不同层并不一致：

- **Python 前端/解释器/VM**：`Int` 是宿主 Python 整数——**任意精度**；
  `Float` 是 IEEE-754 binary64。
- **`.obc` 常量池**：`Int` 目前编码为 **i64**（spike 限制）。
- **Rust VM spike**：`Int` 是 **i64**，溢出报错；`Float` 是 f64。
- **typed 字节码**：混合 `Int`/`Float` 运算先 `TO_FLOAT`，因此混合比较
  目前也按转换后的 float 比较。

于是产生三个必须回答的问题：

1. `Int` 是否溢出？溢出时 trap、wrap、还是升级为大整数？
2. `Float` 的精度、NaN/Inf、除零与显示如何定义？
3. 动态方言 `oort-object` 与静态方言 `oort-core` 是否共享同一套数值语义？
   后端（Python/Rust）的差异是语义还是实现？

## 2. 先行研究

| 语言 | `Int` 模型 | 溢出行为 | `Float` | 混合 Int/Float 比较 |
|---|---|---|---|---|
| Python | 任意精度 | 无 | binary64 | 按数学值精确比较 |
| Ruby | 任意精度（Fixnum/Bignum 已统一） | 无 | binary64 | 按数学值比较 |
| Scheme / Racket | 精确整数任意精度 + 非精确 flonum | 无 | binary64 | exact/inexact 层级规则 |
| Clojure | 默认 long，`BigInt` 显式 | long 溢出报错/升级 | binary64 | 数值比较 |
| Java | `int`/`long` 固定宽度 | 回绕 | binary64 | 先提升到共同类型 |
| Go | `int`/`int64` 固定宽度 | 确定性回绕 | binary64 | 需显式转换 |
| Rust | `i64` 等固定宽度 | debug trap / release wrap（可配置） | binary64 | 无混合算术 |
| Swift | 机器字 `Int` | trap | binary64 | 需显式转换 |
| Lua 5.4 | 64 位整数 + float | 整数按 2^64 回绕 | binary64 | 按数值比较（有精度边界） |
| JavaScript | `Number` 即 double；`BigInt` 显式 | 无（BigInt） | binary64 | Number 内无区分 |
| TypeScript | `number` 即 double；`bigint` 显式 | 无（bigint） | binary64 | number 内无区分 |
| Zig | 固定宽度整数 | 默认 trap，显式 wrapping 算子 | binary64 | 需显式转换 |

**提炼**：

- **任意精度 Int 是动态语言的主流**（Python/Ruby/Scheme）；固定宽度是
  系统语言的主流（Java/Go/Rust/Swift/Zig）。
- 固定宽度语言把溢出行为做成语言契约（trap 或 wrap），并要求显式类型；
  任意精度语言把宽度藏进实现（Smi/堆整数/BigInt）。
- Oort 同时有动态方言与静态方言。若让两个方言的 `Int` 语义不同，跨方言
  边界与用户心智都会变复杂；若统一为任意精度，Python 后端天然正确，Rust
  后端需要整数阶梯，但语义简单。

### 2.1 渐进类型 / typed-Python 的先例

这是与 Oort 最接近的一类系统：它们同时面对“Python 式任意精度 int”和
“原生固定宽度整数”两种世界。

| 系统 | 做法 | 结果 |
|---|---|---|
| **Typed Racket** | `Integer` 任意精度，`Fixnum` 是子类型；模块边界用 contract | 跨 typed/untyped 保持数值语义，边界检查有成本 |
| **Reticulated Python** | Python 语义 + cast/guard；整数仍是 Python 任意精度 | 语义一致，运行时检查成本 |
| **mypyc** | 默认把 Python `int` 保持为 CPython int 对象（boxed），优先语义 | 需要显式/受限的原生整数优化 |
| **Cython** | Python `int`（对象，任意精度）与 `cdef int`（固定宽度 C 类型）并存；固定宽度是显式选择 | 语义由用户选择的类型决定；C 溢出行为需自行承担 |
| **Numba** | nopython 模式把 Python `int` 统一成 `int64`，不支持任意精度 | 性能好，但超出 int64 的值与 Python 语义分叉（警示案例） |
| **Dart** | `int` 原生为 64 位有符号；`BigInt` 独立类型；Web 上 `int` 是 double | 平台间宽度不同，大整数必须显式 |
| **PHP** | `int` 为平台宽度；算术溢出转为 float | 宽松但类型会“跳变”，不利于静态推理 |
| **Kotlin / Java / C#** | `Int`/`Long` 固定宽度，`BigInteger` 独立 | 类型清晰，默认没有任意精度 |
| **Clojure** | 默认 `long`（溢出抛错），`BigInt` 显式 | 动态语言也把“大整数”设为显式选择 |
| **Julia** | `Int` 默认 64 位，`BigInt` 独立 | 数值计算性能优先；大整数不是默认语义 |
| **Nim** | 固定宽度整数 + `range` 子界类型，越界检查 | 子界检查可表达“有界整数”，与 `Int<N>` 思路相近 |

**关键观察**：

1. **typed-Python 编译器要么保留 Python int 的 boxed/任意精度语义
   （mypyc、Reticulated），要么接受固定宽度带来的语义分叉（Numba）**。
   前者一致但慢，后者快但危险。
2. **显式固定宽度类型是主流折中**（Cython、Kotlin、Julia、Clojure）：
   默认 `Int` 保持简单语义，需要性能时再选 `Int32`/`Int64`。
3. **渐进边界不能静默改变数值语义**：Typed Racket/Reticulated 的核心教训是
   边界必须检查并归责（blame），而不是把大整数悄悄截断。
4. Oort 的方案应避免 Numba 式“默认把所有 int 变成 int64”；`Int` 的语义
   保持任意精度，固定宽度作为**显式类型**出现。

## 3. 提议的语义模型（方言无关）

### 3.1 数值塔

- **`Int`**：精确、无界整数。语言层**没有溢出**；实现可以用
  Smi → HeapInt64 → HeapBigInt 阶梯（design 01 §3），但阶梯是表示细节，
  不是语义。
- **`Float`**：IEEE-754 binary64。
- 两者是不同的静态类型；不隐式互相赋值（spec 11 已有）。

### 3.2 运算规则

- `Int op Int` → `Int`（精确）；`+ - * // %` 不产生 Float。
- 任一操作数为 `Float` → 结果为 `Float`（`Int` 按 binary64 转换，允许舍入）。
- `/` 总是 `Float`（spec 11 已定）。
- 整数除法与取模采用**向下取整**语义（Python/Rust spike 已实现）；
  取模符号随除数。`Int` 无界，因此没有 `MIN / -1` 溢出问题。
- 除零是运行时错误（当前行为），不产生 Inf/NaN。

### 3.3 相等与排序（混合数值）

- `Int` 与 `Float` 的 `==`/`<` 等按**数学值精确比较**；
  例如 `2**53 + 1 == float(2**53 + 1)` 为 false（float 已舍入），
  而不是把整数也舍入成 float 后比较。
- `NaN` 与任何值（包括自身）的 `==` 为 false；排序比较为 false。
- `Inf`/`-Inf` 按 IEEE 排序；`Inf == Inf` 为 true。
- 该规则与 Python 一致，便于把 Python 实现作为语义 oracle。

### 3.4 显示

- `Int`：十进制，无前导零。
- `Float`：采用“最短可回读”表示，整数值补 `.0`，指数形式与 Python
  `repr(float)` 对齐；`nan`/`inf`/`-inf` 小写。
- 显示是跨后端差分测试的一部分（见 §5）。

### 3.5 字面量与 `.obc`

- 源码 `Int` 字面量无界；`Float` 字面量解析为 binary64。
- `.obc` 常量池当前只有 i64 标签；在声称完整语义前必须增加大整数编码
  （字符串/limbs 或十进制串）。kind=1 的 `version` 在需要时提升。
- 源码中的超范围整数字面量不得静默截断。

### 3.6 `Int` 与 `Int<N>` 的区分

- **`Int`** 是语义类型：任意精度、无溢出；两个方言共享。
- **`Int<N>`**（`Int8`/`Int16`/`Int32`/`Int64`）是**显式固定宽度类型**，
  只在静态方言 `oort-core` 中可用（与 design 01 §3.4 一致）；语义是
  “恰好 N 位、补码”的整数。
- 固定宽度类型的溢出行为：**默认检查并报错（trap）**，不静默回绕；
  若将来需要性能，提供显式的 wrapping 运算（类似 Rust `wrapping_add`），
  但那是独立操作，不改变 `+`。
- **转换**：
  - `Int<N>` → `Int`：总是安全（精确），隐式或显式均可，倾向显式；
  - `Int` → `Int<N>`：**检查收窄**，越界报错（静态/运行时取决于能否证明）；
  - `Int<M>` → `Int<N>`：检查收窄/扩展规则明确；
  - 不做隐式数值提升；`Int64 + Int32` 需要显式类型或同名宽度。
- **渐进边界**：
  - 动态 `Int` → 静态 `Int`：语义相同，直接传递（必要时装箱/拆箱）；
  - 动态 `Int` → 静态 `Int64`：边界检查范围，失败按 blame 归责调用方；
  - 静态 `Int64` → 动态 `Int`：安全拓宽为任意精度；
  - 静态 `Int` → 动态 `Int`：安全。
- **为什么分开**：把性能选择交给显式类型，而不是改变 `Int` 的默认语义。
  这接近 Cython 的 `int` vs `cdef int`、Julia/Kotlin 的 `Int` vs 固定宽度，
  也避免 Numba 式“默认 int64”的语义分叉。
- **命名**：先提供具体的 `Int8/16/32/64` 别名；更一般的 `Int<N>` 语法与
  常量表达式留到类型系统支持时。`UInt<N>` 暂不设计。

## 4. 方言与后端

### 4.1 方言

- `oort-object` 与 `oort-core` **共享同一套数值语义**（§3）。
- 静态方言只在**类型规则**上更严格（无隐式转换、集合参数化等），
  不改变数值本身的行为。
- 固定宽度类型（如 `Int32`/`Int64`）若将来引入，应是**独立类型**
  （design 01 §3.4），而不是 `Int` 的语义。

### 4.2 后端

| 后端 | `Int` 实现 | 状态 |
|---|---|---|
| Python 解释器/VM | 宿主任意精度整数 | 已符合语义 |
| Python typed VM | 宿主整数（boxed） | 已符合语义 |
| Rust typed VM（当前） | `i64` + 溢出报错 | **spike 限制，不完整** |
| Rust typed VM（目标） | Smi → HeapInt64 → HeapBigInt | 未实现 |

Rust spike 的 i64 不得被当作最终语义：在实现整数阶梯前，typed differential
必须避开溢出输入；遇到溢出应显式报错（而不是静默 wrap）。

### 4.3 typed 字节码的当前偏差

`EQ_F`/`LT_F` 等混合比较目前由编译器插入 `TO_FLOAT` 后执行，因此对大整数
不满足 §3.3 的精确比较。两种修正：

- **M4-U1**：新增 `EQ_MIXED`/`CMP_MIXED`（或运行时 helper），按精确值比较；
- 或暂时在 typed 子集中拒绝混合比较（但与 spec 11 冲突，不推荐）。

本文建议前者，并在 U1 的验收中加入 `2^53` 边界测试。

## 5. 测试与门禁

新增数值语义差分套件（Python 语义为 oracle）：

1. 大整数：`2**53`、`2**63`、`2**64` 附近的加减乘与显示；
2. 溢出边界：Rust i64 路径必须显式报错，不能 wrap；Python 路径无溢出；
3. 混合比较：`2**53 + 1 == 2.0**53`、大整数与 float 的 `<`/`>`；
4. 除法/取模：正负组合、`-7 // 2`、`-7 % 2` 等；
5. 浮点显示：`2.0`、`-0.0`、`0.06`、`1e20`、`1e-20`、`inf`、`-inf`、`nan`；
6. 除零错误：Int 与 Float 都按当前运行时错误处理。

门禁：eval / vm / typed-hir / typed-bc / Rust typed 五路输出一致（除已知
Rust i64 限制外）。

## 6. 决策记录（2026-11-22）

| 编号 | 决策 | 状态 |
|---|---|---|
| D1 | `Int` 统一任意精度（两方言共享）；固定宽度另设 `Int<N>` | **已定** |
| D2 | 混合比较按数学值精确；新增 `EQ_MIXED`/`CMP_MIXED`，提升 kind=1 `version` | **已定** |
| D3 | 允许 IEEE NaN/Inf；除零仍是运行时错误；显示按 §3.4 | **已定** |
| D4 | Float 显示以 Python `repr(float)` 为 canonical，Rust 对齐 | **已定** |
| D5 | Rust i64 spike 溢出显式报错；不宣称语义 parity | **已定** |
| D6 | `Int`（任意精度）与 `Int<N>`（固定宽度、显式、检查收窄）分离；`Int<N>` 仅静态方言 | **已定** |

## 7. 对 M4-U1 的影响

- **U1 只做 Rust unboxed typed VM**；Python typed VM 保持 boxed，作为差分
  baseline（解装箱在 Python 上没有意义）；
- Rust `TypedValue` 使用 `Int(i64)` 作为 spike 表示；溢出显式报错（D5）；
- 混合比较精确化（D2）在 U1 一并做：新增 `EQ_MIXED`/`CMP_MIXED` 并提升
  typed 字节码 `version`；Python typed VM 也需实现这两个 opcode（仍 boxed）；
- Float 显示与 Python `repr(float)` 对齐（D4），否则差分测试会暴露差异；
- BigInt 表示、`.obc` 大整数常量、Rust 整数阶梯属于后续 ABI/性能工作；
- `Int<N>` 的实现不在 U1：先定语义与 ABI，等类型系统支持固定宽度类型时再做。
