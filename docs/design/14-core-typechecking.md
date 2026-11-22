# oort-core 类型检查与推断算法

> **状态**：as-implemented 参考（2026-11-22，含函数返回类型推断与泛型 ADT 增量 A/B/C）。
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

### 为什么 join 不合并到 Object？

直觉上 `if c { 1 } else { "s" }` 类似乎可以推成「Object」，但当前刻意不这么做：

- **静态模型没有顶类型，也没有子类型**。类型只有上述那些，没有一个可持有/使用的
  静态 `Object`/`Any`；`is_assignable` 对 Primitive 是严格相等、对类/ADT 是名义相等，
  不做子类型判断（运行时虽有 `object_type` 作为类继承的根，但静态检查器不建模它）。
  没有子类型，「最小上界」就只剩「相等」一种情形，故只能返回 None。
- **即便推出 Object 也是死胡同**。静态子集没有向下转型/类型测试/按类型匹配，
  Object 值既不能调 Int 也不能调 String 的方法，什么都做不了；只会把错误从分支处
  推迟到使用处（`v + 1` 才报「Object 不支持 +」），更难定位。在分支处直接报
  「Int 和 String 不兼容」更符合「错误就地归责」（blame）。
- **与「显式优于隐式」一致**。连 Int→Float 都不偷偷提升，合并到 Object 属隐式向上
  宽化，同样拒绝。
- **「Int 或 String」的正确表达是和类型/ADT**，而非 Object：
  `enum IntOrStr { I(Int), S(String) }` + `match` 取用，显式、类型安全、可消费。
  Object/any 是跨方言动态边界的逃生舱，不是静态合并工具。

跨语言对照：这是**没有 union 类型的语言的共同选择**——Rust/Haskell 同样报错、
引导用 enum；TypeScript 因有 union 才推出 `number | string`。待 Oort 引入 union
或更依赖 ADT，此规则再议。

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

## 7. 泛型 ADT、变型与内建 ADT（增量 A/B/C，2026-11-22）

泛型 `enum E[T]` 与声明处变型的已实现算法。设计取舍见
[OP 0022](../proposals/0022-generic-adts.md) §2–§5；此处只记录落地形态。

**表示**。声明与应用分离：`AdtTemplate(origin, name, params, constructors)`
是类型构造器，`AdtType(template, args)` 是应用（`Option[Int]`）。模板在解析
载荷前注册，所以 `MyList[T]` 的自递归载荷直接引用同一模板；载荷里只出现本模板的
`TypeParameterType`，嵌套泛型一律写成已应用类型（`AdtType(option, (B,))`），
`substitute()` 因此不会被内层参数捕获。单态 enum 是 `params=()` 的特例。

**构造器方案**。每个构造器是 `ForallType(params, body)`：有载荷时 body 为
`(payload...) -> AdtType(template, params)`，零参时为 `AdtType(...)`。

**实例化**。只有两处信息来源，不做 HM：

- check 模式：`_check_expr` 在期望是**同模板** `AdtType` 时拦截 Call/Name，
  用期望实参建立参数绑定，再以代换后的载荷检查实参——空字面量因此有期望
  （`Some([])`、`Cons(1, Nil)` 在 `MyList[Int]` 标注下可用）。
- infer 模式：`_check_generic_call` 先推断实参类型，再用 `unify()` 做受限
  一阶合一求解参数；未绑定参数报硬错误（对齐 Rust E0282），冲突报
  “同一参数被推断为 X 与 Y”。`unify` 只在构造器与实参类型之间工作，不泛化、
  不做 occurs check（本切片不会产生无限类型）。

裸泛型构造器作值只在期望是函数类型时实例化（`val f: (Int) -> Option[Int] =
Some`）；否则 `visit_name` 报“无法推断类型实参”。

**match**。`_instantiated_payload` 把 scrutinee 的实参代入构造器载荷后再
检查子模式；穷尽性仍按模板的构造器名集合。运行时完全擦除：variant 名 +
payload，解释器与 VM 均不读类型参数。

**声明处变型（增量 B）**。`TypeParameterType` 带 `Variance`（不变/协变/逆变）。
文法用两个独立标签
`(in_variance=IN | out_variance=identifier)? name=identifier`：ANTLR 不允许同一
标签混用 token 与 rule，且 `out` 保持普通标识符（`val out = 1` 合法）；其他
变型文本由 AST builder 报错。声明解析完 payload 后 `_check_enum_variance`
做极性检查：payload 起始极性 +1（构造器产出数据）；`FunctionType` 参数取反、
返回不变；内建集合（不可变）保持极性；嵌套 `AdtType` 按
`AdtType.variance_at(i)` 复合（协变保持、逆变取反、不变型把极性压成 0）。
`_variance_violation` 返回第一个非法出现的极性：`out` 要求 +1，`in` 要求 −1，
0 表示不变位置（对两者都非法）。`is_assignable` 对同模板实参按变型逐参比较
（协变正向、逆变反向、不变双向）；当前没有子类型，关系实际退化为相等，但
检查已启用，为继承/接口落地预置健全性。

**与内建容器的关系（非显然）**。`List[T]`/`Set[T]`/`Dict[K, V]`/`Tuple[...]`
**不是**这套模板机制的实例：它们是 `ListType` 等硬编码的结构化静态类型，
由 `_resolve_container_type` 按名字白名单特判。泛型 ADT 走
`AdtTemplate`/`AdtType`，两者不共用实现。运行时的 `List` 等也只是每种容器一个
无参数的 `OortType`（`type_system.py`），类型参数只存在于检查器抽象域。
未来若统一，属于类型系统重构，不在增量 A 范围内。

**内建 Option / Result（增量 C）**。`semantics/core/prelude.py` 用 AST 节点
构造 `Option[out T]` 与 `Result[out T, out E]`；`Compiler._run_input` 与
`compile_unit_details` 在语义分析前注入（`-t ast` 不注入）。注入节点
`synthetic=True`，AST dump 跳过；`declaration_origin="<core-prelude>"` 固定
名义 origin，使跨模块的 `Option[Int]` 相等。检查器把预置构造器标为
`from_prelude`：模块导出过滤它们，用户重定义类型/构造器/顶层名报 prelude
诊断。运行时照常执行注入的 enum；模块环境仍含这些绑定，但静态导出过滤后
检查器不允许访问。

**至此 OP 0022 的 A/B/C 全部落地**；后续是对象模型与 FFI。

## 8. 完整模式匹配（OP 0023，2026-11-22）

**语法**：字面量（Int/Float/String/Bool，可带 `-`）、元组（`()`、`(p1, p2)`；
`(p)` 是分组）、或模式 `p1 | p2`、守卫 `pattern if cond => body`。`match` 的
scrutinee 可为 enum、`Bool`、`Int`、`Float`、`String` 或 `Tuple`。

**检查**。`_check_pattern` 按期望类型递归：字面量要求类型精确一致；元组要求
`TupleType` 且元数相同；或模式各分支必须绑定相同的名字集合与双向可赋值的
类型；守卫在 arm 作用域内按 Bool 检查。每个 `PatternResult` 返回绑定、归一化
alternatives 与 failed。

**嵌套穷尽性**。归一化为 `_NormPattern`（wild / ctor / literal）。
`_missing_witness` 是 Maranget usefulness 的 witness 版本：

- 完整签名：ADT 构造器集合、`Bool` 的 `{true, false}`、元组的单构造器；
  Int/Float/String 是无限域，字面量集合永不完整。
- 或模式在 alternatives 中展开为矩阵多行；**守卫 arm 不入矩阵**（守卫可能为假，
  与 OCaml/Scala 的保守处理一致）。
- 矩阵含全 wild 行时直接视为覆盖；这也是递归 ADT 上搜索的终止条件。
- 缺失时报告 witness：`Some(false)`、`(false, _)`、`_`。

**后端**。HIR `Pattern` 增加 `literal_*`/`tuple`/`or` 与 `value`；`MatchArm` 增加
`guard_index`（守卫编译为独立函数，参数为 pattern 绑定）。`.obc` 写出 v2
（字面量值 + guard 字段），读取仍兼容 v1。VM 逐 arm 匹配；守卫失败继续下一个
arm（不回溯或模式其他分支）；解释器同语义。决策树编译（Maranget 2008）留作
独立性能切片，当前使用顺序匹配。

## 9. 相等（OP 0024，2026-11-22）

- **ADT**：结构值相等（同 enum 类型名、同构造器、载荷递归值相等）；键语义按
  `OortADT.__eq__`/`__hash__`（Bool/Int 严格、Int/Float 键不同）实现，值语义由
  `values_equal` 单独实现。
- **静态类实例**：身份相等（Object 的默认 `==`/哈希），可用于容器与键。
- **checker 前置**：`_supports_value_equality` 递归允许 ADT/类并拒绝函数载荷；
  `_is_valid_key_type` 对 ADT 递归检查 key-safe 载荷；同类型要求由
  `_check_equality` 校验。
- 跨模块预置 `Option` 按 enum 类型名比较，checked 代码不会混淆同名用户 enum。

## 10. 边界与后续

- **决策树编译 / 对象模型 / FFI 边界**：OP 0005/0023 后续切片，建立在本文的
  双向检查 + 局部推断基线上。
- **方法依赖扫描的保守性**：按属性名匹配同类方法（不看 receiver 类型），可能给
  「调用其他类同名方法」多加一条依赖约束——只会更保守（偶尔多要求标注），不会
  不健全。精确化需 receiver 类型信息，留作后续。
- **全程序 HM**：design 03 Phase-2 可选扩展，当前不做。
