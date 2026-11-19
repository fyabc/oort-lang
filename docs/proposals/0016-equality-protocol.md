# OP 0016: 统一相等性协议

- **状态**：Proposed（2026-11-20）
- **作者**：Oort 设计讨论
- **相关**：[OP 0007](0007-oort-object-object-model.md)、
  [OP 0012](0012-standard-library.md)、
  [规范：表达式](../spec/02-expressions.md)、
  [规范：类](../spec/05-classes.md)

## 摘要

当前 Oort 的相等性由三套互不一致的规则决定：

1. `==` 对 List/Tuple/Dict/Set 使用 **HOST 投影**（Python 容器的相等），
   嵌套的 `true`/`1` 被当作相等；
2. `in` 在**顶层**用 `_strict_equal` 区分 Bool/Int，嵌套层又退回 HOST 相等；
3. Dict/Set 的键查找使用 Oort 对象的 `__eq__`/`__hash__`，与 `==` 无关。

结果是 `[true] == [1]` 为真而 `true in [1]` 为假；`{: true: 1 :}` 与
`{: 1: 1 :}` 相等，但用 `1` 取键失败；集合代数把 `true` 与 `1` 合并。

本提案定义**值相等**与**键相等**两层协议，让 `==`、`in`、Dict/Set 相等、
集合代数与键查找在所有嵌套层级上使用同一套规则。

## 跨语言调研

| 语言 | 值相等 | 键相等/哈希 | 可变容器作键 | 数字跨类型 |
|---|---|---|---|---|
| Python | `==`，容器递归 | `__eq__` + `__hash__` | 不可哈希 | `1 == 1.0`，同一字典键 |
| Ruby | `==` | `eql?` + `hash`（Hash/Set） | 不可作为键 | `1 == 1.0`，但 `eql?` 为假 |
| Java/Kotlin | `equals`（数组除外） | `equals` + `hashCode` | 可变对象可作键但不安全 | 包装类型不跨类型相等 |
| Go | `==`，仅可比较类型 | 同一 `==` | slice/map 不可比较 | 无隐式跨类型 |
| Rust | `PartialEq` | `Eq + Hash` | 需实现 `Hash` | 无隐式跨类型 |
| JavaScript | `===`；对象按身份 | Map 用 SameValueZero | 对象按身份 | `true !== 1` |

来源：

- Python <https://docs.python.org/3/reference/datamodel.html#object.__eq__>
- Ruby <https://docs.ruby-lang.org/en/master/Object.html#method-i-eql-3F>、
  <https://docs.ruby-lang.org/en/master/Hash.html>
- Kotlin <https://kotlinlang.org/docs/equality.html>
- Go <https://go.dev/ref/spec#Comparison_operators>
- Rust <https://doc.rust-lang.org/std/cmp/trait.PartialEq.html>
- JavaScript <https://developer.mozilla.org/en-US/docs/Web/JavaScript/Equality_comparisons_and_sameness>

结论：

- Python/Java/Kotlin/Rust 要求“相等 ⇒ 哈希相同”，但 Oort 还没有用户级哈希
  协议；若直接采用单层模型，定义 `operator "=="` 的类会破坏 Dict/Set。
- Ruby 把 `==` 与 `eql?`/`hash` 分开：值相等不自动等于键相等。这与 Oort
  当前“用户类默认身份键”的现状最接近，也给未来 `hash` 协议留出空间。
- Bool/Int 严格区分是 Oort 已有决策；协议必须在**所有嵌套层级**保持它。

## 决策

### D1：值相等 `==`

- List/Tuple：长度相等，逐元素用 Oort `==` 比较（可调用用户运算符）。
- Dict：键用 D2 的**键相等**匹配；对应值用 Oort `==` 比较。
- Set：用 D2 的键相等比较元素（无序）。
- String：逐码点相等；Null 只等于 Null。
- Bool 与 Int **永不相等**，嵌套在容器中同样如此。
- Int 与 Float 保留数值相等：`1 == 1.0` 为真，`[1] == [1.0]` 也为真。
- 用户类：使用其 `operator "=="`；未定义时用身份。
- `!=` 默认是 `==` 的取反；显式 `operator "!="` 仍然优先。
- 身份短路：`a is b` 直接视为相等；循环容器用“已比较对象对” memo，
  对已访问的 `(a, b)` 返回真（共归纳/双模拟语义）。

### D2：键相等与哈希

Dict 键、Set 元素以及 Tuple 的键哈希使用**键协议**，与值 `==` 分离：

| 类型 | 键相等 | 哈希 | 备注 |
|---|---|---|---|
| Null | 仅 Null | 固定 | |
| Bool | 同值 | `hash(bool)` | Bool/Int 严格 |
| Int | 同值 | `hash(int)` | Int 与 Float **不**键相等 |
| Float | 同值 | `hash(float)` | 与 Int 不键相等 |
| String | 同内容 | 字符串哈希 | |
| Tuple | 逐元素键相等 | 逐元素键哈希 | 元素必须可哈希 |
| Type/Function/Module/用户实例 | 身份 | 身份哈希 | 用户 `==` 不影响键身份 |
| List/Dict/Set | — | 不可哈希 | 不能作键/集合元素 |

- **值相等与键相等可以不同**：`1 == 1.0` 为真，但 `{1: "a"} != {1.0: "a"}`，
  `1 in {. 1.0 .}` 为假。这是 Ruby `eql?` 模型的刻意选择，用于保证键查找
  与哈希稳定；未来引入用户 `hash` 协议后再讨论是否放宽。
- Dict 相等：键集合按键相等一致，值用 `==`。
- Set 相等与 `& | ^ -`：全部按键协议；结果保留原始键对象。
- 用户类自定义 `==` 后仍以身份作为键；文档明确“值相等不隐含键相等”。
  未来 `operator "hash"()` 提案负责自定义键相等/哈希。

### D3：成员测试 `in`

- List/Tuple/String：逐元素用 `==`（元素在左，查询值在右；与 Python
  `PyObject_RichCompareBool` 的元素顺序一致）。
- Dict：按键协议查键。
- Set：按键协议查元素。
- `!in` 是 `in` 的取反；用户容器显式定义 `operator "in"` 时优先。
- 因此：
  - `[true] == [1]` 与 `true in [1]` 都为假；
  - `1 in [1.0]` 为真（值相等），但 `1 in {. 1.0 .}` 为假（键相等）。

### D4：实现方式

- 不再用 `host_value` 投影实现相等、成员测试或集合代数。
- List/Tuple 的 `==` 与 `in` 改为 **CONTEXT** 原生运算符，通过
  `NativeContext.binary("==", ...)` 递归调用 Oort 运算符；这使容器中的
  用户类 `==`、扩展运算符与错误传播都走正常分派。
- Dict 相等：按键协议匹配键，值用 `ctx.binary("==")`；Dict/Set 的
  `in` 直接使用底层 Oort 键容器（Python dict/set 已按键协议哈希）。
- Set 相等与 `& | ^ -` 直接操作底层 Oort 集合，不做 HOST 投影。
- `OortTuple.__eq__`/`__hash__` 保留为键协议实现；嵌套 Tuple 递归。
- 循环相等在递归辅助函数中维护 `(id(left), id(right))` 集合；只影响
  值相等，键协议不接受可变容器。
- `host_value` 继续用于宿主边界与打印，但**不再定义语言相等**。

### D5：兼容性与版本

- 这是语义修正，会改变可观察行为（嵌套 Bool/Int、Dict/Set 相等）。
  按 0.x 规则放在下一个 minor（0.4.0）发布，并在 CHANGELOG 标注。
- 现有程序若依赖 HOST 投影相等，需要按新协议调整。
- `is`/`!is` 仍是身份比较，不参与本协议。

## 替代方案

1. **Python 单层模型（`==` + 用户 `__hash__`）**：语义最统一，但必须先有
   用户哈希协议；否则自定义 `==` 的类作键会破坏 Dict/Set。留作后续。
2. **保持 HOST 投影相等，只把 `in` 改成投影**：实现最小，但 Bool/Int
   严格性会在嵌套层丢失，违背既有语言决策。放弃。
3. **让 Int 与 Float 键相等**：更接近 Python，但当前 Oort 对象哈希/相等
   需要额外规范化；先采用 Ruby 式键区分，等哈希协议统一后再评估。
4. **禁止可变容器参与相等**：会破坏 List/Dict 的实用比较；放弃。

## 测试计划

- 值相等矩阵：Bool/Int 在 List/Tuple/Dict/Set 的所有嵌套组合；
  Int/Float 数值相等；String/Null。
- `in`：List/Tuple/String 的值相等；Dict/Set 的键相等；`!in`；
  嵌套容器与用户类 `==`。
- Dict：键/值相等、键查找与相等一致、Tuple 键、Int/Float 键区分。
- Set：相等、`& | ^ -`、Bool/Int 与 Int/Float 键区分、用户实例身份键。
- 循环 List/Dict 的相等与身份短路。
- 用户类 `operator "=="` 在容器元素中生效；显式 `!=` 优先。
- REPL/脚本、扩展运算符与既有集合助手回归。
- 基准：嵌套 1000 元素的 `==`/`in`，确认不再深拷贝投影。

## 非目标

- 用户自定义哈希（`operator "hash"`）与可变键协议；另立提案。
- 重载 `is`/`!is`。
- 跨类型数值键统一、NaN 的特殊键语义（先沿用宿主哈希/相等）。
- 序列化、规范化哈希或持久化字典键。
