# OP 0023: 完整模式匹配

- **状态**：Implemented（语义已实现；决策树编译作为性能切片待做）
- **作者**：fyabc
- **创建日期**：2026-11-22
- **相关提案**：[OP 0005](0005-type-system.md)（类型系统主线；§4 ADT 与模式匹配）、
  [OP 0017](0017-oort-core-thin-probe.md)（单态 ADT 第一切片）、
  [OP 0022](0022-generic-adts.md)（泛型 ADT、变型与内建 ADT）
- **相关设计**：[design 14](../design/14-core-typechecking.md)（已实现算法基线）、
  [spec 11](../spec/11-core-probe.md)（语言参考）、
  [spec 12](../spec/12-hir-bytecode-vm.md)、[spec 13](../spec/13-bytecode-serialization.md)

## 摘要

把 `oort-core` 的 `match` 从「`_` / 绑定 / 构造器」第一切片扩展为完整模式：

- **字面量模式**（Int/Float/String/Bool，负数）；
- **元组模式**（`()`、`(p)`、`(p1, p2)`）；
- **或模式** `p1 | p2`；
- **守卫** `pattern if cond => body`；
- **嵌套穷尽性**（Maranget usefulness），用具体 witness 报告缺失模式。

语义先落地（解释器 + VM + `.obc` 表示），**决策树编译作为后续性能切片**。
不含范围模式、集合字面量模式、`@` 绑定、冗余 arm 警告。

## 动机

1. 现有 `match` 只能按构造器解构，无法写 `0 => ...`、`(x, y) => ...` 或
   `1 | 2 => ...`；判空/枚举手写 `if` 链或嵌套 match，丢失穷尽性保证。
2. 穷尽性只做顶层构造器覆盖：`Some(Some(_))` 与 `Some(None)` 漏掉
   `None` 时无法报告具体缺失；嵌套模式必须靠 `_` 兜底。
3. OP 0005 §4 已把字面量/元组/守卫/或模式列为 ADT 的组成；OP 0022 完成后
   类型层已具备泛型与内建 `Option`/`Result`，模式语法是下一个自然缺口。
4. 决策树是编译期优化，语义正确性不依赖它；先固定模式语义与穷尽性，
   再做决策树可以分别验证（项目原则「先语义后性能」）。

## 语法

```oort
match value {
    0 => "zero",
    1 | 2 | 3 => "small",              # 或模式
    (x, y) => x + y,                    # 元组模式
    Some(v) if v > 0 => "positive",     # 守卫
    Some(_) => "non-positive",
    None => "missing",
}
```

### match arm

```text
matchArm
    : pattern (IF expression)? FATARROW expression
    ;
```

- 守卫用 `if`，作用于**整个** arm 的 pattern（`1 | 2 if c` 等价于
  `(1 | 2) if c`），与 Rust 的优先级一致。
- arm 仍用 `,` 或换行分隔。

### pattern

```text
pattern
    : patternPrimary (BIT_OR patternPrimary)*
    ;

patternPrimary
    : patternLiteral
    | LPA patternList? RPA              # Tuple / grouping
    | identifier LPA patternList? RPA   # ConstructorPattern
    | identifier                        # NamePattern / wildcard
    ;
```

- **字面量**：整数（十/二/八/十六进制）、浮点、字符串、`true`/`false`；
  数字前可有 `-`。
- **元组**：`()` 空元组、`(p1, p2)` 元组；`(p)` 视为**分组**，不是一元组
  （一元组模式 `(p,)` 本切片不支持）。
- **或模式**：`|` 分隔，`|` 只出现在 pattern 位置（core 不实现位运算）。
- **组**：`(p)` 与 `p` 完全等价。

## 语义

### 类型检查

- 每个 pattern 针对**期望类型**检查（scrutinee 类型、元组元素类型、
  构造器载荷类型）。
- **字面量模式必须与期望类型精确一致**：`Int` 字面量只匹配 `Int`，
  Float 只匹配 Float，Bool/String 同理。虽然运行期 `1 == 1.0`，
  静态模式不允许跨数值类型（与 `val x: Float = 1` 拒绝一致）。
- **元组模式**要求期望是 `TupleType`，元数相同；子模式按元素类型递归。
- **或模式**的每个分支都按同一期望类型检查；所有分支必须绑定**完全相同
  的名字集合与类型**（双向可赋值，`Unknown` 参与错误恢复）。绑定不可变。
  一个分支里绑定、另一个不绑定是错误。
- **绑定名**（裸标识符）不可反驳，绑定整个值；若裸名命中当前 enum 的零参
  构造器，则按构造器模式处理（现有规则）。
- **守卫**表达式在 arm 作用域中检查，必须为 `Bool`；可引用该 pattern
  绑定的名字。守卫不改变 pattern 的可反驳性。

### 匹配顺序与绑定

- arms 自上而下尝试；第一个 pattern 匹配且守卫为真（或没有守卫）的 arm 生效。
- 守卫失败时继续下一个 arm，**不回溯尝试或模式的其他分支**（与 OCaml
  左到右、Rust 整体 or-pattern + guard 的语义一致）。因此 `p1 | p2 if g`
  中若 `p1` 先匹配但 `g` 为假，不会再用 `p2` 的绑定求值 `g`。
- 守卫可能有副作用（调用函数）；求值次数取决于前面 arm 的匹配情况。
- 运行时未命中任何 arm 仍是错误（`No match arm matched value ...`）。

### 可反驳性与穷尽性

- 不可反驳：`_`、绑定名、元组（元素全不可反驳）、唯一构造器的 enum
  （子模式全不可反驳）、至少一个分支不可反驳的或模式。
- 字面量模式与多构造器 enum 的构造器模式可反驳。
- **穷尽性**用 Maranget 的 usefulness 算法（`U(P, q)`）：
  - 构造器签名：ADT 用其构造器集合；`Bool` 用 `{true, false}`；元组视为
    单构造器（元数即元素数，总是完整）；Int/Float/String 的字面量集合
    **永不完整**（无限域），必须由 `_`/绑定覆盖。
  - 或模式按分支展开成 pattern 矩阵的多行。
  - **守卫 arm 不计入覆盖**：任意守卫都可能为假，与 OCaml/Scala 的保守处理
    一致；若所有 arm 都带守卫，报非穷尽。
  - 缺失时报告首个 witness，例如 `Match is not exhaustive; missing: None.`、
    `... missing: Some(None).`、`... missing: (false, _).`
- 冗余 arm 警告本切片不做（当前诊断管线没有 warning 语义；留作后续）。

## 嵌套穷尽性算法

归一化为内部 `Pattern`（checker 侧）：

| 源码 | 归一化 |
|------|--------|
| `_` / 绑定 | `Wild` |
| `true` / `false` | `Ctor("true"/"false", 0)` |
| `1`、`"a"` | `Literal`（无限签名） |
| `(p1, p2)` | `Ctor("tuple", 2, [p1, p2])` |
| `Some(p)` | `Ctor("Some", 1, [p])` |
| `p1 \| p2` | 展开为两行 |

`U(P, q)` 递归：候选首列为构造器时 specialize；为 wildcard 时，若矩阵首列
构造器集合对类型完整则逐一 specialize，否则 default。witness 生成取
缺失构造器的字段 wildcard。矩阵中出现全 wild 行时直接视为覆盖——这同时也是
递归 ADT（如 `MyList`）上搜索的终止条件。

## 决策树编译（后续切片）

语义正确性由顺序匹配保证。决策树编译（Maranget 2008 的 good decision
trees）作为**独立性能切片**：把 arm 矩阵编译成「列测试 → 子矩阵」的树，
共享失败路径，减少重复的构造器/字面量测试。本提案不改变现有
`Match` 指令的语义，只预留归一化 pattern 结构。

## 运行时与后端表示

- **解释器**：`_match_pattern` 递归扩展 literal/tuple/or；`visit_match_expr`
  在 pattern 匹配后、执行 body 前求值守卫，失败则继续下一个 arm。
- **HIR**：`Pattern` 描述符增加 `literal_int`/`literal_float`/
  `literal_string`/`literal_bool`/`tuple`/`or`；`MatchArm` 增加
  `guard_index: int | None`（守卫编译为独立函数，参数为 pattern 绑定）。
- **字节码**：`PatternSpec` 增加 `value`（tagged 常量）以承载字面量；
  `MatchArmSpec` 增加 `guard_index`。`.obc` **version 升到 2**；v1 读取仍
  支持（无 guard 字段、旧 kind），写出统一 v2。Rust spike 需接受 v2 并对
  新 kind 给出明确错误（其 7 个差分用例不涉及新模式）。
- **擦除**：模式匹配仍完全在运行时按值/标签执行；类型参数不进入描述符。

## 跨语言对比

| 语言 | 字面量 | 元组 | 或模式 | 守卫 | 穷尽性 |
|------|--------|------|--------|------|--------|
| Rust | 是（含范围） | 是 | `\|`（1.53+） | `if` | 非穷尽报错，嵌套 |
| Scala | 是 | 是 | `\|` | `if` | sealed 层次给警告 |
| OCaml | 是 | 是 | `\|` | `when` | 警告；守卫不建立覆盖 |
| Haskell | 是 | 是 | 多方程/no or-pattern | `\|` guard | 警告 |
| Swift | 是 | 是 | `case p1, p2` | `where` | enum 穷尽 |
| C# | 是 | 位置模式 | `or`/`and` | `when` | 警告 |
| **Oort** | **是** | **是** | **`\|`** | **`if`** | **非穷尽报错 + witness** |

依据：

- Rust 模式与 or-pattern 语义、guard 优先级：
  <https://rust-lang.github.io/fls/patterns.html>、
  <https://doc.rust-lang.org/book/ch18-00-patterns.html>。
- Scala 模式/守卫与穷尽性（sealed 层次、守卫不被推理）：
  <https://docs.scala-lang.org/scala3/reference/other-new-features/runtimeChecked.html>。
- OCaml 守卫使穷尽性检查保守、or-pattern 左到右取首个匹配绑定：
  <https://fplaunchpad.org/ocaml_nptel/M05-L04-guards.html>。
- 穷尽性算法：Maranget, *Warnings for pattern matching*, JFP 2007,
  <https://www.cambridge.org/core/journals/journal-of-functional-programming/article/warnings-for-pattern-matching/3165B75113781E2431E3856972940347>。
- 决策树：Maranget, *Compiling pattern matching to good decision trees*,
  ML 2008, <https://dl.acm.org/doi/10.1145/1411304.1411311>。

## 边界与限制

- 不做范围模式（`1..=5`）、集合/列表字面量模式、字符串插值模式；
- 不做 `@` 绑定、引用模式、类型测试模式（静态方言没有运行时类型测试；类虽有
  名义子类型，也不能用模式测试实例类型）；
- 不做一元组模式 `(p,)`；`(p)` 是分组；
- 不做冗余 arm 警告（只做穷尽性错误）；
- 守卫不建立覆盖，且或模式不因守卫失败而回溯；
- 本切片不做决策树编译，仅保留归一化结构。

## 正交性检查

- **与类型系统**：pattern 检查复用 `_check_pattern`/expected-type；字面量
  精确匹配；或模式绑定做双向可赋值比较；不改 `is_assignable`。
- **与泛型 ADT**：构造器载荷先 `_instantiated_payload` 代换，再按新
  pattern 递归；元组/字面量模式与类型参数无交互。
- **与内建 Option/Result**：`match` 的嵌套穷尽性直接用于 `Option`/`Result`
  的全部常用形状（`Some(_) | None` 等）。
- **与后端**：顺序匹配语义不变，Match 指令扩展描述符；`.obc` v2。
- **与 `for`/块**：无交互；pattern 绑定仍是 arm 独立作用域。

## 替代方案

1. **只做语法糖展开为 if 链**：会失去嵌套穷尽性与具体 witness；拒绝。
2. **守卫失败后回溯或模式其他分支**：绑定可能不同，语义复杂且与 OCaml/
   Rust 不一致；拒绝。
3. **立即实现决策树**：语义与优化同时改，难以定位差分；拆成后续切片。
4. **字面量跨数值类型匹配（`1` 匹配 `1.0`）**：与静态严格性冲突；拒绝。

## 向后兼容

- 现有 pattern（`_`、绑定、构造器）语义不变；`match` 的 arm 列表语法不变。
- 新增 `|`、字面量、元组、`if` 守卫语法；`|`/`if` 原本不能出现在 pattern
  位置，不破坏现有程序。
- `.obc` 写出版本升到 2；读取 v1 保持兼容。Rust spike 需同步接受 v2。
- 旧诊断 `Match is not exhaustive; missing: A, B.` 改为带 witness 的新措辞；
  更新相关测试。

## 实现计划

> **进度（2026-11-22）**：语义切片已实现——字面量/元组/或/守卫、嵌套穷尽性
> witness、解释器 + VM + `.obc` v2 全部落地；决策树编译（步骤 6）待做。

1. **A1 前端**：文法（literal/tuple/or/guard）、AST 节点（`LiteralPattern`、
   `TuplePattern`、`OrPattern`、`MatchArm.guard`）、AST builder、Pass1
   绑定声明（or 分支去重）。
2. **A2 检查器**：pattern 类型检查、绑定一致性、守卫 Bool 检查、
   Maranget usefulness + witness；替换顶层构造器穷尽性。
3. **A3 解释器**：literal/tuple/or 匹配与守卫求值；未命中错误。
4. **A4 HIR/字节码/VM**：Pattern 描述符扩展、guard 函数、`.obc` v2
   读/写、VM 匹配与守卫、Rust spike 接受 v2。
5. **A5 文档/测试**：spec 11/06、design 14、implementation 09、
   OP 0005/roadmap/README/CHANGELOG、examples；差分（eval/vm）与穷尽性矩阵。
6. **B 决策树**（后续）：按 Maranget 2008 编译，基准对比。

## 未解决问题

- 冗余 arm 是警告还是错误？当前诊断管线只有错误；倾向后续引入 warning。
- 或模式绑定类型：要求双向可赋值还是精确相等？倾向双向可赋值（`Unknown`
  恢复），与 `is_assignable` 一致。
- 决策树的共享/启发式选择（Maranget 必要的 heuristics）与现有 Match
  指令的兼容方式。
- 字面量模式的浮点 `nan`/`-0.0`：源码字面量不含 nan/inf，`-0.0` 与 `0.0`
  在 Oort 相等协议下相等；按值相等匹配。
