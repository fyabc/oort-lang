# OP 0024: ADT 相等与槽对象相等

- **状态**：Implemented
- **作者**：fyabc
- **创建日期**：2026-11-22
- **相关提案**：[OP 0005](0005-type-system.md)（类型系统主线）、
  [OP 0007](0007-oort-object-object-model.md)（动态对象模型：身份相等）、
  [OP 0016](0016-equality-protocol.md)（统一相等性协议）、
  [OP 0022](0022-generic-adts.md)（泛型 ADT）、[OP 0023](0023-full-pattern-matching.md)
- **相关设计**：[design 14](../design/14-core-typechecking.md)、
  [spec 11](../spec/11-core-probe.md)

## 摘要

为 `oort-core` 补上 P6 的相等性缺口：

- **ADT（enum）采用结构化值相等**：同 enum 类型、同构造器、载荷递归相等；
  可用于 `==`/`!=`、容器相等、`in`，以及作为 `Dict`/`Set` 的键（键语义
  按 OP 0016：Bool/Int 严格、Int/Float 键不同）。
- **静态类实例（槽对象）采用身份相等**：`c == c` 为真，不同实例为假，与
  动态方言/OP 0007 一致；可用于相等、容器相等与键。
- 相等性检查在 checker 侧前置拒绝不可比较的载荷（函数）与不可作键的 ADT
  （含 List/Dict/Set/函数载荷）。

## 动机

1. `oort-core` 当前显式拒绝 `A == A` 与 `c == c`，用户只能手写 `match` 比较；
   `Option`/`Result` 已内建，不能比较使常见值语义（缓存键、去重、集合成员）
   无法表达。
2. ADT 是数据值：两个 `Some(1)` 应可互换；OP 0005 把 ADT 定位为“用于数据”，
   类“用于行为/动态派发”。这正好对应 Kotlin/Scala/Swift 的 data/case/value
   vs 普通类的身份语义。
3. OP 0016 已定义值相等与键相等的分层；ADT/槽对象是该协议尚未覆盖的两类值。
4. 容器相等、`in`、Dict/Set 已在 OP 0016 下统一；ADT 相等可直接接入同一递归
   实现，而不是新增特例。

## 设计

### 1. ADT 值相等

- 两个 ADT 值 `a == b` 为真当且仅当：
  - 同一 enum 类型（名义类型；泛型实参已由静态检查保证一致）；
  - 同一构造器（variant）；
  - 载荷个数相同，且逐位按 **Oort 值相等**递归比较。
- Bool 与 Int 严格不等；Int 与 Float 保留数值相等（`Some(1) == Some(1.0)`
  为真，只要静态类型允许比较——实际静态类型不同会被拒绝，见 §3）。
- 嵌套 ADT/List/Tuple/Dict/Set 载荷按各自既有值相等规则递归。
- `!=` 为 `==` 的否定。
- 例：

```oort
val a: Option[Int] = Some(1)
val b: Option[Int] = Some(1)
val c: Option[Int] = None
print(a == b, a == c)          # true false
print([Some(1)] == [Some(1)])  # true
```

### 2. 槽对象（静态类实例）身份相等

- 静态类实例 `c == d` 为真当且仅当 `c` 与 `d` 是同一实例（`c is d`）。
- 不同实例即使槽值完全相同也不相等；这与动态方言的用户类默认语义一致
  （OP 0007/0016），也避免可变 `var` 槽导致结构相等/哈希不稳定。
- 类实例可用于容器相等（逐元素身份比较）与 `Dict`/`Set` 键（身份哈希）。
- 类实例仍不可 `print`（打印与相等是两件事）。

### 3. 静态检查规则

- `==`/`!=` 要求两侧静态类型相同：
  - ADT：`Option[Int]` 只能与 `Option[Int]` 比较；不同实参或不同 enum 报
    `Operator '==' requires both operands to have the same type...`。
  - 类：同一名义类。
- ADT 的结构相等要求载荷可值比较：若任一构造器载荷含函数（或其他不可比较
  类型），该 ADT 的 `==` 显式拒绝：
  `Equality is not supported for enums containing functions in oort-core yet.`
  递归 ADT（`MyList[Int]`）通过 seen 集合收敛。
- 容器相等继续使用 `_supports_value_equality` 递归；ADT/类加入支持集合。
- Dict/Set 键：ADT 要求所有构造器载荷（按泛型实参代换后）都是键类型：
  Int/Float/Bool/String、Tuple（元素键类型）、嵌套 key-safe ADT、类实例
  （身份）。含 List/Dict/Set/函数载荷的 ADT 作为键显式拒绝。类实例作为键
  允许（身份哈希）。
- 动态方言不受影响：`oort-object` 的 `==` 仍由对象协议/用户运算符决定。

### 4. 键语义与哈希

ADT 作为 `Dict`/`Set` 键使用 **键相等**（OP 0016 D2）：

- Bool 与 Int 区分、Int 与 Float 键不同（即使值相等）；
- 嵌套 ADT 递归键相等；Tuple 逐元素键相等；
- 哈希与键相等一致：同键值必须同哈希；
- 类实例按键为身份。

运行时 `OortADT.__eq__`/`__hash__` 实现键语义，供 Python Dict/Set 使用；
`==` 的**值相等**由解释器 `values_equal` 单独实现，二者可不同（与
`1 == 1.0` 但键不同一致）。

### 5. 跨模块类型身份

运行时 enum 类型对象按模块创建；预置 `Option`/`Result` 各模块各有一份。
ADT 相等/键比较按 **enum 类型名 + variant + 载荷** 判断，使跨模块的
`Option[Int]` 值相等。静态检查已按固定 origin 保证同名预置类型同一；用户
同名但不同模块的 enum 在静态类型上不同，checked 代码无法直接比较。
（若未来运行时要更精确，可在 `EnumSpec` 中加入 origin；本提案不扩展 `.obc`。）

## 正交性检查

- **与 OP 0016**：复用值/键两层协议；不改 Bool/Int 严格性与 Int/Float
  值相等规则。
- **与 ADT/match**：相等是值语义，不影响穷尽性或模式匹配；`Some(1)` 仍按
  variant 匹配。
- **与泛型**：静态类型实参必须一致；运行时擦除，比较载荷值。
- **与类/对象**：静态类身份相等与动态类一致；不引入槽结构比较。
- **与后端**：解释器与 VM 走同一 `apply_binary` 回退；`.obc` 无变化。
- **与打印**：类仍不可打印；ADT 打印不变。

## 跨语言对比

| 语言 | ADT/值类型相等 | 普通类相等 | 键/哈希 |
|------|----------------|------------|---------|
| Rust | `#[derive(PartialEq, Eq)]` 结构化；`Hash` 派生 | 需手动实现 | Eq+Hash 才可作键 |
| Kotlin | `data class` 结构化（主构造属性） | 默认身份 | `equals`/`hashCode` 一致 |
| Scala | `case class` 结构化 | 默认身份 | `hashCode` 派生 |
| Swift | enum/struct 可合成 `Equatable`/`Hashable` | class 默认身份 | 合成 `hash(into:)` |
| Java | `record` 结构化 | 默认身份 | record 自动 `hashCode` |
| OCaml | 结构相等（含可变值，需谨慎） | 同左 | 结构哈希（`Hashtbl`） |
| **Oort** | **ADT 结构化** | **身份** | **ADT 结构键（key-safe）；类身份键** |

依据：

- Rust derive（`PartialEq`/`Eq`/`Hash` 逐字段，`Eq` 要求字段可 `Eq`，
  `Hash` 与 `Eq` 一致）：<https://doc.rust-lang.org/stable/reference/attributes/derive.html>。
- Kotlin data class 按主构造属性生成 `equals`/`hashCode`；普通类默认身份：
  <https://livebook.manning.com/learn/concepts/equals-method--api-element/kotlin-in-action-second-edition>。
- Scala case class 生成结构 `equals`，普通类默认引用相等：
  <https://docs.scala-lang.org/tour/case-classes.html>。
- Swift 在字段/关联值满足条件时合成 `Equatable`/`Hashable`：
  <https://developer.apple.com/documentation/swift/hashable>。
- Java record 自动结构 `equals`/`hashCode`（JLS/Java API）。

## 替代方案

1. **槽对象也做结构相等**：可变 `var` 槽会使哈希不稳定，且与动态方言默认
   身份冲突；拒绝。
2. **ADT 只做身份相等**：`Some(1)` 不相等违背数据值直觉；拒绝。
3. **ADT 只做值相等、不做键**：可行但失去缓存/去重的常用场景；本提案按
   key-safe 载荷提供键语义，不安全载荷显式拒绝。
4. **运行时用 enum origin 精确类型身份**：需要扩展 `EnumSpec`/`.obc`；
   当前静态检查已保证 checked 代码不混淆同名用户 enum，故先按类型名。

## 向后兼容

- `oort-core` 中原本被拒绝的 `A == A`、`c == c` 变为合法；这是新增能力。
- ADT 作为 Dict/Set 键：原先运行时按身份，现将按键/值语义；checked 程序中
  只影响 ADT 键的可观察行为（属于本提案修正）。
- 含函数载荷的 ADT 相等、含不可键载荷的 ADT 作键：显式拒绝。
- `.obc` 不变；Rust spike 不受影响。
- 动态方言不变。

## 实现计划

> **进度（2026-11-22）**：ADT 结构相等/键与静态类身份相等已实现，覆盖
> `==`/`!=`、容器相等、ADT/类键、跨模块预置 Option；checker 前置拒绝函数
> 载荷与不可键 ADT。运行时 `OortADT.__eq__`/`__hash__` 为键语义，`values_equal`
> 与 `apply_binary` 为值语义。

1. **Checker**：`_check_equality` 接受同类型 ADT/ClassType；
   `_supports_value_equality` 增加 ADT（递归载荷，seen 收敛）与 ClassType；
   `_is_valid_key_type` 增加 key-safe ADT 递归与 ClassType；诊断。
2. **运行时**：`OortADT.__eq__`/`__hash__` 键语义；`values_equal` 增加 ADT
   值语义（memo 防递归）；`apply_binary` 在 `==`/`!=` 对双 ADT 走值相等。
   类实例继续使用 Object 的默认身份 `==`/哈希。
3. **测试**：ADT 相等/不等、嵌套/泛型/内建 Option/Result、容器、跨模块；
   ADT 键（Scalar/Tuple/嵌套 ADT）与非法键；类身份相等/容器/键；差分
   eval/vm；`.obc` 无关。
4. **文档**：spec 11/06、design 14、implementation 09、OP 0005/0016/roadmap/
   README/CHANGELOG、examples。

## 未解决问题

- 用户自定义 ADT 相等（`operator "=="`）是否允许；本提案只定义结构相等。
- 含浮点 `NaN` 的 ADT：`NaN != NaN` 使 `Eq` 不成立；Oort 值相等已有浮点
  规则（`NaN` 与自身不等），本提案沿用。
- 未来若运行时要区分同名跨模块 enum，需在 `EnumSpec`/`.obc` 加 origin。
