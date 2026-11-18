# 01 - 运行时值表示（Runtime Value Representation）

> **文档状态**：设计决策记录（2026-07）
> **来源**：两轮聊天讨论的综合整理

---

## 1. 概述

Oort 是一门**渐近类型**（gradual-typing）编程语言：动态类型优先，支持模块级静态类型迁移。这一设计哲学对运行时值表示提出了特殊要求：

- 动态模块需要高效的类型判断与装箱/拆箱
- 静态模块期望零开销的原生操作
- 两种模块之间的互操作必须低摩擦

本文档记录围绕这些目标所做的设计决策，涵盖：值表示方案、整数层级、边界机制，以及与主流语言的对比。

---

## 2. 值表示：64 位 Tagged Pointer

### 2.1 核心方案

采用 **64 位宽、2 位标签**的 Tagged Pointer：

```
64-bit word: [ tag:2 | payload:62 ]
```

| 标签 | 含义 | 说明 |
|------|------|------|
| `00` | Heap Pointer | 指向 GC 堆上的对象 |
| `01` | Smi（Small Integer） | 内联 62 位有符号整数 |
| `10` | Immediate Value | bool、null 等即时值 |
| `11` | Reserved | 保留（未来扩展） |

### 2.2 设计理由

**为什么是 64 位而非 32 位？**

- 现代系统上指针为 64 位，32 位 tag 方案需要压缩指针（如 V8 Pointer Compression），引入额外复杂度
- 62 位 Smi 范围（约 ±4.6×10¹⁸）足以覆盖绝大多数整数运算，减少溢出到堆分配的概率

**为什么是 2 位标签而非 3 位？**

- 3 位标签将 Smi 压缩到 61 位，收益不大
- 2 位标签保留 4 种分类，已足够区分指针、整数、即时值和未来扩展
- 多数主流实现（Dart、早期 V8）采用类似粒度

### 2.3 Smi 编码细节

```
Smi 值范围: [-2^61, 2^61 - 1]
编码方式: 值左移 1 位（低位补 0），再与 tag 01 或运算

解码: 算术右移 1 位即可恢复原值
判型: value & 0b11 == 0b01  即判断为 Smi
```

### 2.4 堆对象表示

- 堆指针（tag `00`）指向的对象头含类型信息，供 GC 和动态类型检查使用
- 采用**统一堆**（unified heap）：无论动态模块还是静态模块分配的对象均在同一堆上
- 静态模块使用 **write barrier** 维护 GC 正确性，不引入独立内存管理

---

## 3. 整数类型层级

### 3.1 三层阶梯

```
SafeInt（默认）
  │  溢出时 trap（可调试）或自动升级
  ▼
FastInt（显式 opt-in）
  │  溢出时 wrap-around（未定义行为）
  ▼
BigInt（大整数）
     任意精度，堆分配
```

| 层级 | 底层实现 | 溢出行为 | 使用场景 |
|------|----------|----------|----------|
| SafeInt | Smi → HeapInt64 → HeapBigInt | trap / 自动升级 | 默认整数运算 |
| FastInt | Smi 或裸 Int64 | wrap-around | 性能关键代码 |
| BigInt | HeapBigInt（GMP 风格） | 无溢出 | 密码学、大数运算 |

### 3.2 Smi → HeapInt64 → HeapBigInt 阶梯

SafeInt 的内部升级路径：

1. **Smi**：值在 62 位范围内，直接内联表示
2. **HeapInt64**：运算结果超出 62 位但仍可用 64 位表示，堆分配
3. **HeapBigInt**：超出 64 位，任意精度堆分配

编译器通过**范围推断**（range inference）尽量将运算保持在 Smi 层，减少堆分配：

```python
# 编译器推断 x 始终在 Smi 范围内
x = 42
y = x + 1    # 直接 Smi 加法，无需溢出检查
```

### 3.3 编译器指令（Escape Hatch）

为性能敏感代码提供显式控制：

```python
@ensure_smallint
def hash(key: str) -> int:
    # 编译器验证：返回值保证在 Smi 范围内
    # 否则编译期报错或插入运行时检查
    ...

@unchecked
def tight_loop():
    # 关闭 SafeInt 的溢出 trap，使用 wrap-around 语义
    # 类似 Rust 的 wrapping_add
    ...
```

### 3.4 静态模块中的固定宽度类型

`Int32`、`Int64` 等固定宽度整数类型**仅在静态模块中可用**：

```python
# 静态模块（.oort 文件中声明 `module static`）
module static

def process(data: Int32) -> Int32:
    return data + 1   # 溢出时编译错误或插入检查
```

动态模块中只有 `int`（对应 SafeInt 层级），不暴露宽度细节。

### 3.5 逃逸分析驱动的拆箱

借鉴 PyPy 的逃逸分析思路：

- 若整数值**不逃逸出当前作用域**，编译器可将其拆箱为裸寄存器值
- 逃逸分析结果决定：内联 Smi、拆箱寄存器、还是堆分配
- 对程序员透明，无需手动标注

---

## 4. 边界机制（动态 ↔ 静态互操作）

### 4.1 核心理念：Boundary Thunk

借鉴 **Racket 的边界哲学**（contracts at module boundaries），但实现上不同：

- Racket：使用 wrapper 函数包裹跨边界调用，运行时检查合约
- Oort：使用 **boundary thunk**——编译器生成的小型适配函数

```
动态模块调用静态模块函数:
  1. 编译器在静态模块的导出点生成 thunk
  2. thunk 负责：类型检查 + 值转换（如 Smi → Int32 拆箱）
  3. 调用方（动态模块）无需感知转换细节

静态模块调用动态模块函数:
  1. 编译器在静态模块的导入点生成 thunk
  2. thunk 负责：返回值类型验证 + 装箱（如 Int32 → Smi）
  3. 静态模块内部代码保持原生性能
```

### 4.2 为什么不用 Racket-style Wrapper？

- Wrapper 需要在运行时动态创建闭包，增加 GC 压力
- Thunk 是编译期生成的静态函数，可被内联优化
- Thunk 的错误信息更友好（包含边界位置和类型期望）

### 4.3 边界处的整数转换

| 来源 | 目标 | 转换 |
|------|------|------|
| Smi (动态) | Int32 (静态) | 范围检查 + 拆箱 |
| Int32 (静态) | Smi (动态) | 装箱（通常零开销） |
| HeapInt64 (动态) | Int32 (静态) | 范围检查 + 拆箱（可能 trap） |
| BigInt (动态) | Int64 (静态) | 范围检查 + 拆箱（可能 trap） |

---

## 5. 与其他语言的对比

### 5.1 Dart

| 方面 | Dart | Oort |
|------|------|------|
| int 语义 | AOT: 64 位有符号（非任意精度）；Web: JS double | SafeInt 三层阶梯，支持 BigInt 升级 |
| 值表示 | 64 位 Tagged Pointer（AOT） | 类似方案，但增加 BigInt 层级 |
| 静态/动态 | 全静态（sound null safety） | 渐进类型，动态优先 |

**注意**：Dart 的 `int` 在 AOT 编译下不是任意精度——溢出行为为 wrap-around。dart2js（Web）编译到 JavaScript，所有数字均为 double。Oort 选择默认 safe（trap on overflow）是有意区别于 Dart。

### 5.2 Racket

| 方面 | Racket | Oort |
|------|--------|------|
| 类型系统 | Gradual typing (Typed Racket) | 类似哲学，模块级粒度 |
| 边界机制 | Runtime contract wrappers | 编译期 boundary thunks |
| 整数 | 自动提升（fixnum → bignum） | 三层阶梯 + 显式控制 |

**借鉴**：Racket 在模块边界处强制执行合约检查的理念。Oort 采用相同哲学，但用编译期 thunk 替代运行时 wrapper 以提升性能。

### 5.3 V8 / JavaScript

| 方面 | V8 | Oort |
|------|-----|------|
| 值表示 | Pointer Compression（32 位压缩指针 + 外部指针） | 64 位 Tagged Pointer（传统方案） |
| Smi | 31 位（64 位系统上） | 62 位 |
| 整数 | 所有数字均为 double（BigInt 为独立类型） | 整数有独立层级 |

**注意**：V8 的 "Pointer Compression" 与传统 Tagged Pointer 不同——它将 64 位指针压缩到 32 位以节省内存，但需要 "cage"（4GB 内存区域）配合。Oort 不采用此方案，因为：
- 增加内存布局复杂度
- 对堆大小施加 4GB 硬限制
- Oort 作为新语言无需兼容现有 32 位生态

### 5.4 Python (CPython)

| 方面 | CPython | Oort |
|------|---------|------|
| 值表示 | 所有对象均为堆指针（PyObject*） | Tagged Pointer + Smi 内联 |
| 整数 | 任意精度（PyLongObject） | 三层阶梯，Smi 热路径优化 |
| 性能 | 引用计数 + 全局锁 | GC + write barrier |

**对比**：CPython 的整数运算始终涉及堆分配和虚方法调用，Oort 的 Smi 内联表示可大幅减少这一开销。

### 5.5 Lua (LuaJIT)

| 方面 | LuaJIT | Oort |
|------|--------|------|
| 值表示 | NaN-boxing（64 位 IEEE 754 NaN 空间复用） | 2 位 Tagged Pointer |
| 整数 | Lua 5.3+ 区分 integer/double | 三层整数阶梯 |
| FFI | 内置 FFI | 静态模块充当类型安全边界 |

**对比**：NaN-boxing 可表示更多即时类型（double、指针、bool 均内联），但实现复杂且调试困难。Oort 选择更直观的 Tagged Pointer 方案。

---

## 6. 开放问题

### 6.1 NaN-boxing 是否值得考虑？

- NaN-boxing 可在 64 位中同时内联 double 和指针，对数值密集代码有优势
- 但实现复杂度高，与 GC 的交互更困难
- **当前决策**：暂不采用，留作未来优化备选

### 6.2 Smi 范围溢出时的 trap 策略

- 开发环境：trap 并打印详细信息（值、操作、操作数）
- 生产环境：是否提供 "release mode" 自动升级为 HeapInt64 而非 trap？
- **倾向**：默认 trap，`@unchecked` 显式 opt-in wrap-around

### 6.3 BigInt 的互操作性能

- HeapBigInt 与 Smi 之间的混合运算如何高效处理？
- 是否需要在编译器层面做 BigInt 字面量的范围推断以降级为 Smi？
- **待定**：需要 benchmark 数据

### 6.4 32 位平台支持

- 64 位 Tagged Pointer 方案在 32 位平台上 Smi 仅 30 位
- 是否需要独立的 32 位值表示？
- **倾向**：不支持 32 位平台（2026 年已非常规）

### 6.5 WebAssembly 目标

- WASM 的值类型为 i32/i64/f32/f64，如何映射 Oort 的 Tagged Pointer？
- WASM GC 提案可能改变堆管理策略
- **待定**：作为第二阶段目标

---

## 7. 参考资料

1. **Dart VM 源码** — `runtime/vm/object.h`、`runtime/vm/raw_object.h`（Tagged Pointer 实现）
2. **V8 Blog: Pointer Compression** — <https://v8.dev/blog/pointer-compression>
3. **Racket Contracts** — *Gradual Typing for Functional Languages* (Siek & Taha, 2006)；Typed Racket 边界机制
4. **PyPy Escape Analysis** — PyPy 项目的逃逸分析与拆箱优化
5. **LuaJIT Source** — NaN-boxing 实现参考
6. **CPython Internals** — `Objects/longobject.c`（PyLongObject 实现）
7. **Crafting Interpreters** — 值表示章节（Lox 的 tagged union 方案）
