# OP 0029: Int / Float 数值语义

- **状态**：Accepted（D1–D6 已定；实现分后端推进）
- **作者**：Oort 设计讨论
- **创建日期**：2026-11-23
- **相关**：[design 16](../design/16-numeric-semantics.md)、[design 01](../design/01-runtime-value-representation.md)、[spec 13](../spec/13-bytecode-serialization.md)

## 摘要

统一 `oort-object` 与 `oort-core` 的数值契约：`Int` 任意精度，`Float`
IEEE-754 binary64，混合比较按数学值精确，Float 显示以 Python `repr` 为
canonical；Rust 的 i64 只是 spike 表示，不定义语言语义。

## 动机

不同层当前使用不同整数表示：

- Python 前端/解释器/VM：任意精度；
- `.obc` 常量池：i64；
- Rust VM spike：i64，溢出报错；
- typed 混合比较曾先转 Float，可能丢失精度。

如果这些差异进入公开语义，会导致方言/后端不一致和跨边界错误。

## 设计

### D1：Int 任意精度

- 两个方言共享 arbitrary-precision `Int`；
- 溢出不是语言错误；实现可分层为 Smi/堆整数；
- Rust 最终实现需要大整数路径，不能把 i64 溢出当作 Int 语义。

### D2：混合 Int/Float 比较

- `==`/`!=`/`<`/`<=`/`>`/`>=` 对不同数值类型按**数学值精确比较**；
- 不先转换成 Float；
- 例：`2**53 + 1 == 2.0**53` 为 false；
- typed 字节码使用 `*_MIXED` 指令。

### D3：Float 与特殊值

- `Float` 是 IEEE-754 binary64；
- 允许 NaN/Inf；
- NaN：`==` false、`!=` true、排序比较 false；
- 除零是运行时错误，不产生 Inf；
- `-0.0` 与 `0.0` 数值相等，但显示保留符号。

### D4：Float 显示

- 以 Python `repr(float)` 为 canonical；
- Rust VM 必须对齐，不能直接使用默认 `Display`；
- 这保证差分测试和 REPL 输出一致。

### D5：Rust spike 限制

- Rust typed VM 当前使用 i64；
- 溢出显式报错；
- 这是表示层限制，不是语言语义；
- 差分测试避免溢出输入；
- 正式 Rust VM 必须实现 D1。

### D6：Int 与 Int<N>

- `Int`：任意精度，默认整数类型；
- `Int<N>`：固定宽度、显式、静态方言可用；
- 收窄必须显式检查；
- 不把固定宽度溢出规则混入 `Int`；
- `Int<N>` 的具体语法/ABI 留后续实现。

## 正交性检查

- **类型系统**：`Int`/`Float` 严格区分，不隐式提升；混合算术按既有规则。
- **集合/ADT**：NaN 键/相等沿用 D3；Nullable ADT 与 Float 交互不引入特例。
- **模块/边界**：跨边界 `Int` 语义一致；`Int<N>` 边界需显式收窄。
- **宏**：不涉及。
- **特例**：不按后端改变可观察结果。

## 替代方案

1. **Int 固定 64 位、溢出 trap/wrap**：系统语言常见，但与 Python 动态语义冲突。
2. **Int 默认 f64**：JS 风格，破坏大整数和键语义。
3. **两方言不同 Int 语义**：跨方言边界/心智复杂。
4. **Float 显示用 Rust 默认**：与 Python 差分不稳定。

## 向后兼容

- Python 实现大多已符合 D1–D4，主要是规范固化；
- Rust spike 继续显式标注 i64 限制；
- `.obc` 常量 i64 是格式限制，未来需要大整数常量编码；
- `Int<N>` 是新增静态能力，不改变 `Int`。

## 实现计划

1. 把 D1–D6 写入 spec 11/13（或在 spec 中交叉引用本提案）。
2. typed 字节码已实现 `*_MIXED`；保持。
3. Rust VM v2 实现大整数阶梯、Float 显示和除零规则。
4. `Int<N>` 作为独立静态提案/切片。

## 未解决问题

- `.obc` 大整数常量的编码（varint/长度前缀/池）；
- Smi→堆整数升级阈值；
- `Int<N>` 的语法、溢出行为和 ABI；
- 跨边界大整数的复制/共享策略。
