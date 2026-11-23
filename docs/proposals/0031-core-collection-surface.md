# OP 0031: `oort-core` 集合表面（成员、下标写入、切片、集合代数）

- **状态**：Implemented（C1–C4）
- **作者**：Oort 设计讨论
- **创建日期**：2026-11-24
- **相关**：[OP 0016](0016-equality-protocol.md)、[OP 0013](0013-iterator-protocol.md)、[OP 0017](0017-oort-core-thin-probe.md)、[OP 0022](0022-generic-adts.md)、[spec 11](../spec/11-core-probe.md)、[spec 14](../spec/14-typed-bytecode.md)

## 摘要

把 `oort-object` 已支持、而 `oort-core` 仍显式拒绝的常用集合操作逐步引入
静态方言：`in`/`!in`、List/Dict 下标写入、List/Tuple/String 切片读、
Set 代数（`| & - ^`）。排序与列表拼接等需要“可排序”契约的操作留到后续。

## 动机

typed core 的 List/Set/Dict 目前只读：

```oort
print(2 in [1, 2])          # Operator 'in' is not supported in oort-core yet.
val xs = [1, 2]
xs[0] = 9                   # Only plain names and class slots can be assigned ...
print(xs[1:3])              # Slices are not supported in oort-core yet.
print({. 1 .} | {. 2 .})    # Operator '|' is not supported in oort-core yet.
```

而同一程序在 `oort-object` 下都可运行。结果：

- 计数器、DP、去重、查表等常见程序必须绕开核心集合；
- 两个方言在同一语言内提供不同能力，迁移需要重写；
- 类型化后端已经有 List 深相等、Set/Dict 键相等、迭代快照等基础，缺的是表面。

## 设计

### D1：成员测试 `in` / `!in`

- `x in expr` 返回 `Bool`；`!in` 为取反，不新增求值路径；
- 支持类型：

| 容器 | 元素/键类型 | 语义 |
|---|---|---|
| `List[T]` / `Tuple[..., T]` | `T` | 值相等（OP 0016） |
| `Set[T]` | `T` | 键相等/哈希 |
| `Dict[K, V]` | `K` | 键相等/哈希，不检查值 |
| `String` | `String` | 子串包含（与动态一致） |

- 类型规则：操作数必须与元素类型兼容；不做隐式数值转换（`1 in [1.0]` 是
  类型错误，除非显式转换）；
- 求值顺序：先求容器，再求被查值？固定为**从左到右**（与二元运算符一致）；
- 复杂度：List/Tuple 线性，Set/Dict 平均 O(1)，String 子串搜索；不承诺
  具体算法，但不得改变语义。

### D2：下标写入

- `container[index] = value` 返回 `Unit`；
- 允许：
  - `List[T]` + `Int`：原地替换，返回 Unit；
  - `Dict[K, V]` + `K`：插入或替换；
- 禁止：Tuple/String（不可变）、Set（无下标语义）；
- 索引规则与读取一致：`Int`，负索引从末尾计；越界是运行时错误，**不自动扩容**；
- Dict 键使用键相等/哈希；Dict 插入顺序仍不是语言保证（spec 09）；
- 别名语义：写入通过别名可见；迭代器仍是快照（OP 0013）；
- 赋值目标只能是下标表达式或简单名字/槽，不引入多重赋值。

### D3：切片读取

- `xs[start:end]` 支持 `List[T]`、`Tuple[...]`、`String`；
- 省略 `start`/`end` 表示两端；负索引按 Python 语义从末尾计并夹取；
- 结果：List/Tuple 为新容器，String 为新字符串；不与原容器共享可变状态；
- 首版只支持步长 1：`xs[a:b:c]` 显式拒绝（“slice steps are not supported
  in oort-core yet”）；
- 边界：
  - `start`/`end` 必须是 `Int`；
  - 夹取规则采用 Python（`[1:100]` 取到末尾，`[3:1]` 为空），与动态一致；
- 切片赋值（`xs[1:3] = ys`）不在本提案短期范围。

### D4：Set 代数

- 运算符：`|`（并）、`&`（交）、`-`（差）、`^`（对称差）；
- 两侧必须是同一元素类型的 `Set[T]`；结果为新 `Set[T]`；
- 元素身份使用键相等（OP 0016）；
- 不修改操作数；
- 比较运算符（子集/超集 `< <= > >=`）留到后续，避免与 List 字典序比较
  混淆。

### D5：排序与列表拼接（后续）

- `sorted`、List `+`、字典序 `<` 在动态方言已存在，但静态核心需要：
  - `T` 的“可排序”契约（trait/bound 或内建可排序类型集合）；
  - 比较函数/闭包支持（typed 函数值仍在 B2）；
- 因此不在短期范围；等 OP 0005 的上界/接口或内建 `Ordered` 机制落地后，
  作为 C5 单独提案。

### 边界与限制

- 不引入迭代器协议自定义、闭包、泛型函数；
- 不实现切片赋值、步长切片、稀疏/无限序列；
- 不承诺 Set/Dict 顺序；
- 不改变动态方言行为；只把已存在的动态能力带入 core；
- 不引入隐式数值提升或跨类型比较。

## 正交性检查

- **相等性**：全部复用 OP 0016 的值相等/键相等，不新增比较协议。
- **迭代器**：写入不改变快照语义；`for` 期间的写不影响当前迭代。
- **类型系统**：所有操作在静态类型上可判定；结果类型明确。
- **ADT/模式匹配**：切片/成员不引入新模式；`match` 不受影响。
- **模块/ABI**：新增指令需要 kind=1 版本提升；artifact/缓存按版本失效。
- **边界（B1）**：容器仍按值复制；core 内原地写入不会穿透到动态侧。
- **方言**：动态已有对应操作，语义对齐；不新增方言开关。

## 参考与对照

| 语言 | 成员 | 下标写入 | 切片 | 集合代数 |
|---|---|---|---|---|
| Python | `x in s`（List 值、Dict 键、String 子串） | `s[i] = v`，越界错误 | `s[a:b]`，负索引、夹取 | 并/交/差/对称差 |
| Rust | `contains`，无 `in` | `IndexMut`，越界 panic；`get_mut` 返回 Option | `&s[a..b]`，越界 panic | `BitAnd/Bitor/Sub` 等 trait |
| Kotlin | `x in s` | `s[i] = v` | `slice(a..b)`；区间语义显式 | `union/intersect/subtract` |
| Swift | `contains` | `s[i] = v` | `s[a..<b]`；Range 类型 | `union/intersection/subtracting` |
| Ruby | `include?` | `s[i] = v`，可扩容 | `s[a, len]` / `s[a..b]` | 并/交/差/对称差 |
| JavaScript | `x in obj` 检查**键** | 数组可越界扩容 | `slice(a, b)` | `Set` 操作需方法 |
| Go | 无运算符，手写循环 | 越界 panic | `s[a:b]`，越界 panic | 无内建 |

设计取舍：

- 采用 Python 的**运算符 + 冒号切片**，与动态方言和现有语法一致；
- 拒绝 JavaScript 的“`in` 查键/数组自动扩容”语义：`in` 在 Oort 中对
  List/Tuple 查值、对 Dict 查键，类型决定，避免同名不同义；
- 切片的夹取采用 Python/Ruby 风格；下标写入越界采用错误而不是扩容；
- Set 代数采用 Python/Ruby 的运算符；不引入 trait/接口约束，先限定
  “两侧同一 `Set[T]`”。

## 替代方案

1. **只提供方法**（`xs.contains(x)`、`xs.set(i, v)`、`xs.slice(a, b)`）：
   表面积更大、与动态不一致；运算符更贴近现有语法，放弃。
2. **Rust 风格范围**（`xs[1..3]`）：需要新 token/语法，且动态已用冒号；
   放弃。
3. **越界自动扩容**（JS/稀疏数组风格）：隐藏错误、类型系统更难；放弃，
   保持越界错误。
4. **持久化不可变集合**：语义更纯，但与动态方言和性能预期冲突；放弃。
5. **一次引入排序/拼接/切片赋值**：范围过大且依赖排序契约；拆分。

## 向后兼容

- 这些程序目前是显式拒绝，因此不会破坏现有 core 代码；
- 动态方言保持不变；
- 新指令/格式提升 kind=1 版本；旧 artifact 显式拒绝，缓存按版本自然失效；
- 未实现的步长切片、切片赋值继续显式拒绝。

## 实现计划

### 短期（C1–C4）

| 阶段 | 内容 | 验收 |
|---|---|---|
| C1（已实现） | `in`/`!in`：List/Tuple/Set/Dict/String；类型检查；HIR/字节码/VM | 与动态差分一致；类型错误显式 |
| C2（已实现） | List/Dict 下标写入；负索引/越界；别名与迭代快照测试 | `xs[i] = v`、`d[k] = v` 与动态一致；Tuple/String/Set 拒绝 |
| C3（已实现） | List/Tuple/String 切片读；Python 夹取；步长显式拒绝 | 差分覆盖空/负/越界切片 |
| C4（已实现） | Set 并/交/差/对称差；类型一致；结果新集合 | 与动态差分一致；混合元素类型拒绝 |

C1–C4 一次性提升 kind=1 v7 / artifact v9 / linked bundle v2，并补 Python/Rust 差分；缓存按版本自然失效。

### 长期（C5+）

- C5：排序（`sorted`、List 字典序、List `+`），依赖可排序契约/函数值；
- C6：切片赋值与步长切片（若确有必要）；
- C7：Set 子集/超集比较；
- 性能：Set/Dict 的哈希表实现与切片复制优化在 Rust VM 阶段处理，不改变语义。

## 未解决问题

- 字符串 `in` 是子串还是单字符（当前动态为子串，建议保持）；
- `List`/`Tuple` 的异构 Tuple 与成员测试的类型规则；
- Set 代数的类型参数变型/子类型交互；
- 排序契约放在类型系统（bound/trait）还是内建函数；
- 切片是否允许省略两端以外的形式（`[:]`、`[:n]`、`[n:]` 建议支持）；
- 写入是否应提供显式错误位置/键信息以改善诊断。
