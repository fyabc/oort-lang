# oort-core 类型检查与推断算法

> **状态**：as-implemented 参考（2026-11-22，含函数返回类型推断第一切片）。
> 本文描述 `oort-core` 静态检查器**当前实现**的双向检查与局部推断算法，作为
> [OP 0005](../proposals/0005-type-system.md) 主线后续切片（泛型、ADT、FFI）的
> 算法基线。

## 0. 文档分工

| 文档 | 角色 |
|------|------|
| 本文（14） | **已实现算法**：双向检查、局部推断、返回推断的机制与规则 |
| [spec 11](../spec/11-core-probe.md) | 规范性语言参考：哪些构造合法、诊断是什么 |
| [implementation 09](../implementation/09-core-typechecker.md) | 检查器代码结构：visitor、作用域、模块导入、诊断管线 |
| [design 03](03-type-system-design.md) | **未来**完整类型系统：渐进类型边界、泛型、Phase-2 HM |
| [OP 0017](../proposals/0017-oort-core-thin-probe.md) | 薄探针决策：为什么选局部双向检查而非 HM |

本文与 design 03 的分工：design 03 描绘远期（全程序 HM、泛型单态化、健全
边界）；本文只描述**已经落地的局部版本**。二者不重复。

## 1. 局部双向检查

检查器采用**双向类型检查**（bidirectional typing）的局部版本，两个方向：

- `check(expr, expected)`：已知期望类型，验证表达式符合它；
- `infer(expr)`：无期望类型，从表达式推出类型。

实现上二者统一在 `CoreTypeChecker._check_expr(node, expected)`：
**`expected = UnknownType` 即 infer 模式**。对 `if`/块/`match` 等分支构造，
expected 非 Unknown 时下推到各分支（`_check_if_expected` /
`_check_block_expected` / `_check_match`）；否则走合成（infer）路径，用
`join_types` 合并分支类型。

取舍依据（OP 0017 已引）：Pierce & Turner 的 *local type inference* 与
Dunfield & Krishnaswami 的 *bidirectional typing* 综述都支持「局部双向检查
足以覆盖实用场景，无需全程序 HM」。Oort 不做全程序 HM：签名边界清晰、错误
信息可定位、模块化编译简单；HM 留作 design 03 的 Phase-2 可选扩展。

## 2. 类型格与合并

静态类型独立于运行时 `OortType`（`semantics/core/types.py`）：

- `PrimitiveType`：`Int`/`Float`/`Bool`/`String`/`Unit`；
- 集合：`ListType`/`SetType`/`DictType`/`TupleType`（结构相等）；
- `FunctionType(params, ret)`（frozen）、`ClassType`/`AdtType`（名义相等，
  注册后填充以支持递归）、`ModuleType`；
- **`UnknownType`**：错误恢复类型，与任何类型双向兼容（`is_assignable` 恒真），
  用于抑制级联诊断；
- **`NeverType`**：底类型（bottom），表示不能正常落到的表达式（`return`、
  `break`、`continue`）。

两个关键运算：

- `is_assignable(expected, actual)`：Unknown 双向兼容；Never 可赋给任何类型；
  其余 Primitive **严格相等，无 Int→Float 提升**；函数类型逐参数/返回递归比较。
- `join_types(left, right)`：分支/返回类型的最小上界（LUB）。Unknown 吸收一切、
  Never 是单位元、相等取自身、**其余（含 Int/Float）返回 None 表示不兼容**。
  不做数值提升、不做子类型 join——混合分支报错而非隐式转换。

## 3. expected-type 传播

期望类型从这些位置下推：变量标注、赋值 RHS、`return` 值、函数体尾表达式、
调用实参、槽初始化器。下推目标是分支构造的最后表达式：

- `if` 两分支、块最后一条语句、`match` 各 arm 体；
- 空集合字面量（`[]`/`{:}`/`{.}`）必须靠期望类型定元素类型，否则报
  `Cannot infer the element type of an empty List; add a type annotation.`。

只作用于**最后一条语句**：`_check_statements_expected` 对非尾部语句纯 infer。
`NeverType` 一旦出现（某路径 return），后续语句不再贡献类型（`saw_never`），
整块类型为 Never——这是「所有路径返回」检测的基础。

## 4. 局部推断

- `val x = expr` 无标注时 infer `expr`；`Unknown` 静默（错误恢复），
  `Never`/`Module`/`Unit` 不能作为变量推断类型（`Unit` 只能做函数返回）。
- 推断类型写入 `node.metadata["type"]`，供 `-t astm` 展示。
- 函数签名在检查函数体**之前**安装，因此自递归调用可解析；顶层按源码顺序
  可见，**不支持前向引用/互递归**（spec 11）。

## 5. 函数返回类型推断（2026-11-22）

**范围**：顶层 `def`、`do` lambda 与**类方法**可省略返回标注；`__init__` 固定
Unit。参数仍强制标注。顶层 def/lambda 为第一切片，类方法为第二切片（依赖序推断）。

**算法**（`_build_signature` / `_check_function_body` / `visit_return_expr`）：

1. 缺标注时以 `ret = Unknown` 占位建签名并先 declare（自递归 lookup 需要），
   进入 infer 模式；压一个 `_ReturnInfer` 帧到 `_infer_stack`（与函数体嵌套
   平行，lambda 嵌套时内层遮蔽外层）。
2. 以 `expected = Unknown` 检查函数体；`visit_return_expr` 把每个 `return`
   表达式的类型收进帧（bare return 记 Unit）。
3. 收尾：候选 = 收集到的 return 类型 +（体类型非 Never 时的尾表达式类型），
   用 `join_types` 折叠。
   - 体期间已有错误 → ret=Unknown，不追加诊断（级联抑制）；
   - join 冲突 → `The return types of function 'f' are incompatible: X and Y.`；
   - 空体/Unit 尾 → Unit；全路径 return → 只用 return 集合。
4. `FunctionType` frozen，故**重建**签名并回填 `NameInfo.type` 与
   `node.metadata["type"]`；`module_exports` 在模块末尾快照，推断结果自动
   正确跨模块导出。

**lambda 期望下推**：`val f: (Int) -> Int = do(x: Int) { x }` 中，期望函数类型
的返回分支经 `_build_signature` 的 `default_return` 挂钩传入（check 模式）；
无期望时 lambda 与 def 一样从体推断。

**自递归仍需标注**：推断期间递归调用拿到占位 Unknown，会经算术/join 吸收导致
推断坍缩，无法可靠定类型。因此检测到自引用（`_mark_recursive_call` 命中正在
推断的帧）且缺标注时报：
`Recursive function 'f' requires a return type annotation in oort-core; add '-> T'.`
前向/互递归本就被拒，无需处理。

### 5.1 类方法：依赖序（拓扑）推断

方法与顶层 def 的关键差异：**方法前向/互调用合法**（类两遍检查先把全部签名装入
`class_type.methods`，再查体），没有顶层「源码顺序可见」那层保护。若朴素按源码
顺序推断，方法 A 调用尚未推断的方法 B 会拿到 Unknown 占位，经算术/join 吸收导致
**A 的推断静默坍缩**（无诊断）。为此方法采用**依赖序推断**
（`_infer_and_check_methods` / `_method_dependencies`）：

1. 第一遍对缺标注方法以 `infer_return=True` 建 Unknown 占位签名。
2. **依赖扫描**：遍历每个缺标注方法体，收集引用到的同类方法名（`this.m()`、
   其他实例上的调用、方法作值；按属性名保守匹配）。
3. **拓扑排序**（Kahn）：被调方法先推断；每推断一个就回填 `class_type.methods`
   （可变元组重赋值，`this` 共享同一 ClassType 对象，立即全局可见）与
   `stmt.metadata["type"]`。拓扑序保证推断时不碰 Unknown 占位。
4. **递归环**（含自环=自递归）无法拓扑排序 → 这些方法报
   `Recursive method 'C.m' requires a return type annotation in oort-core; add '-> T'.`
   再以占位签名查体（保留其他错误检查）。
5. 已标注方法与 `__init__` 最后查体，调用点类型不陈旧。

`__init__`（forced Unit）、构造器类型、确定赋值分析、槽初始化器均不受影响。

## 6. 跨语言对比：返回推断与递归标注

| 语言 | 函数返回推断 | 递归函数是否需显式返回类型 |
|------|--------------|----------------------------|
| Rust | 否（命名函数须写 `-> T`，省略即 `()`） | 恒需标注 |
| Swift | 是（从体推断） | 复杂递归有时需要 |
| Kotlin | 是（单表达式/从体） | **是**（递归/互递归需显式） |
| Scala | 是（从体） | **是**（`recursive method needs result type`） |
| TypeScript | 是 | 否（可推断，有限制） |
| **Oort** | **是（def + lambda + 类方法）** | **是（递归函数/方法需 `-> T`）** |

Oort 的递归规则对齐 Kotlin/Scala。共同根因：推断靠分析函数体，而递归调用的
类型又依赖函数自身返回类型，形成循环依赖——编译器以「要求显式标注」解开。
这正是本切片用「占位 Unknown + 检测自引用」而非定点迭代/占位类型变量的原因：
贴合 OP 0017 局部推断哲学，避免 HM 式复杂度。

依据：
- [Kotlin 官方文档 · Functions](https://kotlinlang.org/docs/functions.html)：
  递归/互递归函数应显式写返回类型；
- [Why does Scala require a return type for recursive functions?](https://stackoverflow.com/questions/3739133/why-does-scala-require-a-return-type-for-recursive-functions)
  与 [Scala Type Inference](https://www.geeksforgeeks.org/scala/scala-type-inference/)：
  递归方法无法推断结果类型。

## 7. 边界与后续

- **泛型 / ADT / Result·Option / 完整模式匹配 / FFI 边界**：OP 0005 后续切片，
  建立在本文的双向检查 + 局部推断基线上。
- **方法依赖扫描的保守性**：按属性名匹配同类方法（不看 receiver 类型），可能给
  「调用其他类同名方法」多加一条依赖约束——只会更保守（偶尔多要求标注），不会
  不健全。精确化需 receiver 类型信息，留作后续。
- **全程序 HM**：design 03 Phase-2 可选扩展，当前不做。
