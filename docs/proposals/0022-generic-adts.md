# OP 0022: 泛型 ADT 与内建 `Option` / `Result`

- **状态**：Implemented
- **作者**：fyabc
- **创建日期**：2026-11-22
- **相关提案**：[OP 0005](0005-type-system.md)（类型系统主线；§3.1 变型、§4 ADT、§5 错误处理）、
  [OP 0017](0017-oort-core-thin-probe.md)（薄探针与局部双向检查）、
  [OP 0004](0004-bytecode-vm.md)（字节码 VM）
- **相关设计**：[design 14](../design/14-core-typechecking.md)（已实现算法基线）、
  [design 03](../design/03-type-system-design.md)（远期泛型策略）、
  [spec 11](../spec/11-core-probe.md)（语言参考）、
  [spec 12](../spec/12-hir-bytecode-vm.md)（类型擦除后端）

## 摘要

实现 P6 的泛型 ADT 切片：`oort-core` 的**泛型 tagged union**，包含

- 声明 `enum Option[T] { Some(value: T), None }`，类型应用 `Option[Int]`；
- 构造器的类型参数**只由期望类型或实参类型确定**（不引入 HM）；
- `match` 时按 scrutinee 的实参代换构造器载荷类型；
- 声明处变型 `[out T]` / `[in T]` 的语法与声明处健全性检查；
- 内建 `Option[out T]` 与 `Result[out T, out E]`，构造器 `Some`/`None`/`Ok`/`Err`。

类型参数在 HIR/字节码之前擦除，共享后端（解释器、VM、`.obc`）**零改动**。
上界 `T: Bound`、泛型类/函数/lambda、`?` 传播糖、嵌套穷尽性、ADT 相等均不在
本切片。

## 动机

1. **类型系统不对称**。`List[T]`/`Dict[K, V]` 等内建容器已参数化，用户 ADT
   却只能单态。任何“包一层”的数据建模都要为每种载荷类型复制一遍
   （`OptionInt`、`OptionString`…），ADT + `match` 的表达力在容器场景塌陷。
2. **`Option`/`Result` 是 OP 0005 §5 的核心承诺**。没有泛型就无法给它们写出
   类型；错误处理只能用异常或哨兵值，违背“显式优于隐式”。
3. **后端条件已满足**。spec 12 已确认 ADT 降低只需“构造器名 + 元数”，类型参数
   属于检查层。泛型 ADT 是对“类型擦除后端”论断的第一次真实检验：若后端需要
   改动，说明 spec 12 的抽象选错了。
4. **与现有类型哲学一致**。design 14 §2 论证了 oort-core 没有顶类型、没有
   union：`if c { 1 } else { "s" }` 不能合并成 `Object`，正确表达是
   `enum IntOrStr { I(Int), S(String) }`。`Option[T]` 正是这个方向的自然延伸。

## 设计

### 1. 语法

```oort
enum Option[out T] {
    Some(value: T),
    None
}

enum Result[out T, out E] {
    Ok(value: T),
    Err(error: E)
}

enum MyList[out T] {
    Cons(head: T, tail: MyList[T]),
    Nil
}

def find(xs: MyList[Int], target: Int) -> Option[Int] {
    if target == 0 { Some(0) } else { None }
}

val a: Option[Int] = Some(1)
val b: Option[List[Int]] = Some([])   # 期望类型把 T 定为 List[Int]，空字面量可检查
val c = Some("x")                     # 推断为 Option[String]
val d: Result[Int, String] = Err("boom")
```

- 类型参数 `[T]` / `[T, E]`；可选变型前缀 `out` / `in`（见 §5）。
- 类型应用复用现有下标语法 `Name[...]`，与 `List[T]` 等一致，不引入尖括号。
- 构造器仍按**位置**绑定；字段名只作文档（与单态 enum 一致）。
- 类型参数约定大写，但不强制——Oort 不靠命名规则承载语义。

### 2. 类型表示：模板与实例

泛型声明必须区分“类型构造器”与“应用后的类型”：

```text
TypeParameterType(name)                        # 声明体内引用参数的刚性变量
AdtTemplate(origin, name, params, constructors) # 声明（类型构造器）
AdtType(template, args)                        # 应用，如 Option[Int]
ForallType(params, body)                       # 构造器的多态类型方案
```

- `AdtTemplate` 在解析字段**之前**注册，因此 `MyList[T]` 自递归直接引用模板；
  递归位置写成 `AdtType(template, (TypeParameterType("T"),))`。
- 模板的构造器载荷只含本模板的 `TypeParameterType`；嵌套泛型一律以已应用的
  `AdtType` 表示（`Option[B]` 是 `AdtType(option, (B,))`），因此代换不会发生
  变量捕获。
- 名义性 = `template.origin + name`；参数逐个结构比较。
  `Option[Int] != Option[String]`。
- 单态 enum 统一成 `params=()` 的模板，用户可见语义不变。

### 3. 构造器是多态值

`Some` 的类型方案是 `forall T. (T) -> Option[T]`；`None` 是
`forall T. Option[T]`。类型参数只能由两处信息确定：

**check 模式**（期望类型是 `AdtType` 且模板相同）：用期望的实参直接绑定参数，
再把实参按代换后的载荷类型检查。这让 design 14 §3 的期望类型传播自然扩展：

```oort
val xs: Option[List[Int]] = Some([])      # T = List[Int]，[] 有期望
val ys: MyList[Int] = Cons(1, Nil)       # Nil 在 MyList[Int] 期望下实例化
```

**infer 模式**（无期望的调用）：先推断各实参类型，再用最小一阶合一求解模板
参数。求不出的参数是**硬错误**，不是 Unknown：

```oort
val x = None          # Cannot infer type argument 'T' of constructor 'None'
val r = Ok(1)         # Err 的 E 无法确定，同样报错
```

这与 Rust 一致：`let x = None;` 触发 E0282 “type annotations needed”。故意不把
未绑定参数默认为 Unknown——那会把错误推迟到使用点，违背“错误就地归责”。

**冲突**：同一参数被实参推出互不兼容的类型时报诊断（例如两处约束都对同一
`T`）。不同参数各自约束（`Pair(1, "s")`）合法。

**一等值**：裸泛型构造器只有在期望是函数类型时才可实例化：

```oort
val f: (Int) -> Option[Int] = Some   # 可
val g = Some                          # 拒绝：没有一等多态
```

零参泛型构造器（`None`）作为值同理需要期望类型；在 `match` 模式中不受影响，
因为模式由 scrutinee 的类型驱动。

### 4. `match`

- scrutinee 必须是 `AdtType`；按“模板参数 → 实参”代换构造器载荷后检查子模式。
  在 `Option[Int]` 上 `Some(v)` 把 `v` 绑定为 `Int`；在
  `Result[Int, String]` 上 `Err(e)` 绑定 `String`。
- 穷尽性仍按模板的构造器名集合；嵌套穷尽性仍是后续切片（现有行为不变）。
- 运行时**不感知类型参数**：variant 名 + payload（spec 12）。`Some(1)` 与
  `Some("x")` 在运行时同构，匹配只看 variant。这正是类型擦除的含义。
- 未来的穷尽性/冗余检查沿用 Maranget 的 usefulness 算法
  （`U(P, q)`：候选模式是否覆盖了此前矩阵未覆盖的值），它天然支持泛型载荷与
  嵌套构造器；本切片不实现。

### 5. 变型（声明处）

语法来自 OP 0005 §3.1：`[out T]` / `[in T]`，缺省不变型。

**软关键字**。`in` 已是保留字（`for ... in`），`out` 不是。为避免把 `out` 升为
全局关键字（破坏 `val out = 1` 这类合法代码），文法用两个独立标签：

```text
typeParameter
    : (in_variance=IN | out_variance=identifier)? name=identifier
      (qualifier=(COLON | LT | GT) typeExpr=expression)? (ASSIGN defaultValue=expression)?
```

ANTLR 不允许同一标签混用 token 与 rule（`variance=(IN | identifier)` 会报
`RULE_LABEL != TOKEN_LABEL`）。两个标签在 AST builder 中合并为 `VarianceKind`；
`out` 仍是普通标识符（`val out = 1` 合法），非法变型文本报
`Expected 'in' or 'out' before type parameter ...`。

**声明处健全性检查**。enum 的载荷是构造器**产出**的数据，处于协变位置；
极性规则：

| 类型形状 | 参数极性 |
|----------|----------|
| 直接出现 `T` | 协变 |
| `List[T]` / `Set[T]` / `Tuple[...]` | 协变（core 集合不可变，spec 11） |
| `Dict[K, V]` | 键、值均协变（同上） |
| `(P1, ...) -> R` | 参数翻转，返回不变 |
| `F[A1, ...]`（泛型 ADT） | 按 `F` 声明的变型逐参复合；不变型不约束 |

`out T` 只允许出现在协变位置，`in T` 只允许逆变，不变型不受限：

```oort
enum Bad[out T] { B(f: (T) -> Int) }   # 拒绝：T 在逆变位置
```

**为什么现在检查一个“不可观察”的性质**：本提案落地时静态模型没有顶类型、
继承或接口，任意两个不同实参类型之间没有子类型关系，因此变型关系暂时无法
改变可赋值性。（后续 [OP 0025](0025-static-object-model.md) 增量 B 已加入类
单继承，变型在类实参之间可观察。）本切片仍强制声明处检查，因为：

- OP 0005 §3.1 已接受该语法，“解析但静默忽略”违反显式拒绝原则；
- 继承/接口切片到来时需要立刻启用健全性检查，届时再补会把不健全的声明留在
  代码库里；
- 检查成本低（只遍历 payload 类型），且为未来 typed IR 的单态化提供合法性前提。

`is_assignable` 对同模板 `AdtType` 按变型逐参比较；在子类型出现前，这一规则
退化为相等（`Unknown` 参与错误恢复时除外）。

**跨语言依据**：

- Kotlin 在**声明处**用 `out` 表示“只生产”、`in` 表示“只消费”，并检查成员中
  的使用位置（`Source<out T>`、`Comparable<in T>`）：
  <https://kotlinlang.org/docs/generics.html>。
- C# 同样用 `out`/`in`，但只允许出现在接口/委托上，类实现保持不变型：
  <https://learn.microsoft.com/en-us/dotnet/CSharp/programming-guide/concepts/covariance-contravariance/creating-variant-generic-interfaces>。
- Scala 用 `+A` / `-A`，编译器检查协变参数只能出现在返回位置：
  <https://docs.scala-lang.org/tour/variances.html>。
- 形式化：Emir、Kennedy、Russo、Yu 把变型标注的健全性做成对成员类型的
  极性判定（“variance and generalized constraints for C# generics”）；
  Kennedy & Pierce 进一步研究带变型的名义子类型的可判定性，并指出必须拒绝
  不健全的声明：<https://www.cs.cmu.edu/~aldrich/FOOL/FOOLWOOD07/program/kennedy-abstract.html>。

Oort 取同一极性规则，范围限于 enum 载荷；泛型类出现后再扩展。

### 6. 上界与默认值：本切片显式拒绝

文法已能解析 `T: Bound`（COLON qualifier）与 `T = Default`（ASSIGN）。本切片
在检查器中显式拒绝：

```text
Type parameter bounds are not supported in oort-core yet; oort-core has no
traits/interfaces to use as bounds.
Type parameter defaults are not supported in oort-core yet.
```

依据：Rust 的 `T: Trait`、Kotlin 的 `T : Comparable<T>`、C# 的
`where T : ...` 都依赖类型类/接口约束；oort-core 的继承、接口与 trait 化运算符
仍在 P6 后续。没有约束目标时实现上界只能产生一个没有意义的构造。

类型参数名不得与已知类型名或 `in`/`out` 冲突（避免 `enum E[Int]` 这类遮蔽）；
重复参数名报错。

### 7. 擦除与后端

**检查器内的“单态化”**。OP 0005 §3.3 说“内部单态化 + 边界擦除”。在当前的
类型擦除后端上，单态化只发生在检查器的抽象域：类型参数被实参代换，不生成按
类型特化的代码。真正的代码单态化属于 typed IR/LLVM 阶段；这与 design 03 的
三阶段规划一致。

- **HIR**：`_lower_enum_def` 只发射 `(构造器名, 元数)`，忽略 `type_params`；
  无新指令。
- **`.obc`**：格式不变（spec 13）；逐字节 round-trip 测试不受影响。
- **运行时**：解释器与 VM 的 `EnumDef`/`BuildEnum` 不读类型参数；构造器名 +
  payload 即全部语义。
- **边界擦除**：跨方言导入仍显式拒绝；未来 trampoline 落地时，泛型实参不越过
  边界，动态侧只看到不透明 ADT 值（tag + payload）。本切片**不做** reified
  泛型或运行时类型实参。

跨语言对照：

| 语言 | 泛型实现 | 运行时是否保留类型实参 |
|------|----------|------------------------|
| Rust | 单态化（编译期为每个实参生成代码） | 是（体现在特化代码中） |
| Java | 类型擦除 | 否 |
| C# / .NET | 具体化（reified） | 是 |
| OCaml | 统一表示 + 类型擦除 | 否（`'a option` 运行时无参数） |
| **Oort（本切片）** | **检查器代换 + 后端擦除** | **否** |

参考：Rust Book ch10 与 rustc-dev-guide 对单态化的描述
（<https://doc.rust-lang.org/book/ch10-01-syntax.html>、
<https://rustc-dev-guide.rust-lang.org/backend/monomorph.html>）；Oracle 的
Java 擦除教程（<https://docs.oracle.com/javase/tutorial/java/generics/erasure.html>）；
OCaml `Option` 模块（<https://ocaml.org/manual/5.5/api/Option.html>）。

### 8. 内建 `Option` / `Result`

目标定义：

```oort
enum Option[out T] {
    Some(value: T),
    None
}

enum Result[out T, out E] {
    Ok(value: T),
    Err(error: E)
}
```

构造函数名的选择对齐主流：Rust/OCaml 的 `Some`/`None`、`Ok`/`Err`（OCaml 用
`Error`，Swift 用 `.success`/`.failure`）。Oort 采用 `Some`/`None` 与
`Ok`/`Err`，最短且与 OP 0005 §4 的示例一致。

**实现方式：预置源码注入**。把上面的定义解析成 AST，拼在每个 `oort-core`
模块正文之前，使 Pass1、检查器、解释器和 VM 共用同一条普通 enum 路径：

- 优点：Option/Result 就是普通的泛型 enum，检查器与两个后端无需任何特判；
  预置代码本身可读、可测试。
- **固定名义 origin**：注入的 enum 使用 `"<core-prelude>"` 作为名义 origin
  （`EnumDef` 增加 `declaration_origin` 字段）。否则每个模块各有一份
  `Option` 模板，跨模块返回 `Option[Int]` 的函数签名在调用方会出现名义性
  分裂。固定 origin 后，任何模块里的 `Option[Int]` 在静态类型上相等。
- **保留名**：类型 `Option`/`Result`，构造器 `Some`/`None`/`Ok`/`Err`。
  模块顶层重定义报专用诊断（“……is declared in the core prelude”）；
  内层作用域可按普通遮蔽规则局部遮蔽（与 `print` 一致）。
  代价是用户不能声明 `enum Foo { Some(Int) }`，这是显式代价，写进规范。
- **导出**：预置构造器不进入模块导出；导入方各自持有同一份预置。AST dump 以
  `synthetic` 标记注明来源。

**替代方案（B 计划）**：检查器预声明静态模板 + 解释器/VM 各自预安装内建 ADT。
少一层 AST 拼接，但要在两个后端各写一份内建类型初始化，且 Option/Result 无法
用普通 enum 源码表达。保留为 B 计划。

**迁移路径**：跨模块类型导出（P6“跨模块类类型标注”）落地后，可把预置源码迁到
随包分发的 core stdlib 模块；用户可见的名字与类型不变。

**实现（2026-11-22）**：`semantics/core/prelude.py` 用 AST 节点构造两段声明；
`Compiler._run_input` 与 `compile_unit_details` 在语义分析前对 core 模块调用
`inject_core_prelude`（`-t ast` 不注入）。注入节点 `synthetic=True`，AST dump
跳过；`declaration_origin="<core-prelude>"` 固定名义 origin。检查器把预置构造器
标为 `from_prelude`，模块导出过滤它们；用户重定义类型/构造器/顶层名报
`... is declared in the core prelude.`。运行时每个模块照常执行注入的 enum，
构造器绑定存在于模块环境，但静态导出已过滤，检查后的代码不可达。

### 9. 诊断

| 场景 | 诊断 | 类别 |
|------|------|------|
| 泛型 enum | 不再拒绝（删除 `Generic enums are not supported...`） | — |
| 裸泛型类型名 | `Type 'Option' requires 1 type argument(s); write Option[...].` | TypeCheckError |
| 实参个数错误 | `Type 'Option' expects 1 type argument(s), got 2.` | TypeCheckError |
| 单态 enum 加实参 | `Enum 'Shape' does not take type arguments.` | TypeCheckError |
| 参数无法推断 | `Cannot infer type argument 'T' of constructor 'None'; add a type annotation.` | TypeCheckError |
| 参数冲突 | `Type parameter 'T' of constructor 'Pair' is inferred as both Int and String.` | TypeCheckError |
| 构造器作值 | `A generic constructor cannot be used as a value without an expected function type.` | TypeCheckError |
| 变型误用 | `Type parameter 'T' is declared covariant ('out') but appears in a contravariant position in constructor 'B'.` | TypeCheckError |
| 上界 / 默认值 | 见 §6 | UnsupportedSyntax |
| 预置名重定义 | `Type 'Option' is declared in the core prelude.` / `Constructor 'Some' is declared in the core prelude.` | TypeCheckError |
| 泛型类/函数/lambda | 保持现有拒绝（本切片不放开） | UnsupportedSyntax |

## 边界与限制

明确**不**包含：

- 泛型类、泛型函数、泛型 lambda、泛型方法/扩展（继续显式拒绝）；
- 上界、`where` 子句、类型参数默认值、高阶类型（`F[_]`）；
- 一等多态与显式类型应用（无 `Some::<Int>` 式语法）；实例化只来自期望类型或
  实参；
- reified 泛型、运行时类型实参、泛型相等（ADT 相等仍是后续切片）；
- 嵌套穷尽性与决策树编译（沿用顶层构造器覆盖）；
- `?` 传播糖（单独提案；本提案只保证它能降级为 `match`）；
- 跨模块**类型名**导入（本提案落地时；预置 origin 是唯一例外）。该限制已由
  [OP 0025](0025-static-object-model.md) 增量 A 解除：类可 `from` 导入类型，
  enum 类型名用 `m.E`。

## 正交性检查

- **与类型系统**：复用双向检查与局部推断（design 14），只为一个受限场景引入
  一阶合一——构造器调用求解，不做 let 泛化、不做全程序 HM。
- **与类/对象**：`ClassType` 不变；泛型类仍拒绝；`ForallType` 的结构为未来泛型
  类/函数预留。
- **与函数/闭包**：`FunctionType` 不变；lambda 的期望下推不变。
- **与模块**：本提案落地时 enum 类型名不导出；预置 enum 用固定 origin 解决跨
  模块类型统一。后续 OP 0025 增量 A 增加独立类型导出（`m.E` / `from` 类）。
- **与宏/编译期**：无交互。
- **与后端**：HIR/字节码/VM/`.obc` 均无改动，由差分测试验证。
- **是否引入特例**：三处，全部显式记录——(1) 预置注入与保留名，(2) `out` 软
  关键字，(3) 构造器多态方案。没有隐式例外。

## 替代方案

1. **只做运行时擦除，不做静态泛型**（Java 式）：实现最省，但 oort-core 的价值
   就在编译期检查，放弃检查等于回到动态方言。
2. **现在就在后端单态化**：没有 typed IR，共享后端是动态值；先做会为不存在的
   优化付出复杂度。
3. **字典传递 / 类型类**：正好为上界铺路，但本切片没有约束目标；留到 trait/
   接口切片。
4. **使用处变型**（Java 通配符 `? extends`）：OP 0005 §3.1 已拒绝；变型决策应
   留在声明处。
5. **单态 Option 族 / nullable / union**：design 14 §2 已论证 oort-core 没有顶
   类型与 union；ADT 是正确表达。
6. **显式 import stdlib 模块**：被“跨模块类型导出未实现”阻塞；作为 §8 的迁移
   路径保留。

## 向后兼容

- 单态 enum 的源码语义不变；内部表示改为零参模板。
- `oort-core` 新增保留名 `Option`/`Result`/`Some`/`None`/`Ok`/`Err`，以及软关键字
  `out`；`oort-object` 完全不受影响。
- `enum E[T]` 从显式拒绝变为支持，需同步 spec 11 与 conformance 06 的拒绝清单。
- `.obc` 格式不变，旧字节码可继续读取。
- 现有枚举测试应全部通过；涉及 `AdtType` 构造表示的测试可能需要跟进。

## 实现计划

> **进度（2026-11-22）**：增量 A（泛型 ADT）、B（声明处变型）与 C
> （内建 `Option`/`Result`）均已实现，由 spec 11/06、design 14、
> implementation 09 与测试覆盖。

分三个可独立评审的增量：

### 增量 A：泛型 enum（无变型、无预置）

1. 前端：AST/文法已解析类型参数与 `X[...]`，A 阶段无需改动。
2. `semantics/core/types.py`：`TypeParameterType`、`ForallType`、`AdtTemplate`、
   `AdtType(template, args)`；代换、受限合一、`describe_type`、
   `is_assignable`、`join_types`。
3. `checker.py`：泛型 enum 声明（先注册模板再解析载荷、自递归）；类型应用注解；
   构造器方案；check 模式的 Call/Name 期望绑定；infer 模式的合一与诊断；
   `match` 载荷代换；删除泛型 enum 拒绝。
4. 测试与示例；VM/eval 差分。
5. 文档：spec 11、conformance 06、design 14、implementation 09、OP 0005、
   roadmap。

### 增量 B：变型

1. 文法软关键字与 AST builder 校验；`TypeParameter.variance`。
2. 声明处极性检查与诊断；`is_assignable` 的变型逐参比较。
3. 测试：合法协变/逆变、函数位置的误用、嵌套泛型复合极性。

### 增量 C：预置 `Option`/`Result`

1. 预置源码、AST 注入点（所有 core 编译路径）、`declaration_origin`、
   `synthetic` 标记、导出过滤。
2. 保留名诊断；示例与文档（spec 11、spec 08 的 core 部分或新页面）。
3. 测试：构造/推断/match/跨模块返回 Option/Result/重定义拒绝。

### 测试矩阵

- 声明：多参数、重复参数、参数遮蔽、自递归 `MyList[T]`、空 enum、非顶层。
- 注解：`Option[Int]`、嵌套 `Option[List[Int]]`、元数错误、裸名、单态 enum 加
  实参。
- 构造：`Some(1)` 推断、期望驱动 `Some([])`、`None`/`Ok(1)` 未绑定报错、参数
  冲突、构造器作值。
- match：`Option[Int]`/`Result[Int, String]` 绑定类型、嵌套构造器模式、零参泛型
  构造器、穷尽性、跨构造器错误。
- 模块：函数返回 `Option[Int]` 跨模块可用（固定 origin）；用户泛型 enum 的类型名
  在本提案落地时不可导入（后续由 OP 0025 增量 A 以 `m.E` 支持）。
- 变型：`Option[out T]`/`Result[out T, out E]` 通过；函数反转极性拒绝；`in` 的
  对称用例。
- 后端：同一批 ADT 程序在 `-t vm` 与 `-t eval` 下结果一致；`.obc` round-trip
  不变。
- 负面：泛型类/函数/lambda 仍拒绝；上界/默认值报 UnsupportedSyntax。

## 未解决问题

1. **预置实现 A/B**（§8）：AST 注入 vs 检查器 + 双后端预安装。倾向 A，待增量 C
   启动前用一个小原型验证注入点覆盖所有编译路径。
2. **未绑定类型参数**：硬错误 vs `Unknown` + 警告。倾向硬错误（Rust E0282 先例，
   错误就地归责）；若实际使用中 `Err("x")` 过吵，再评估。
3. **变型检查时点**：本切片启用 vs 推迟到子类型切片。倾向启用（§5 理由），
   但若增量 B 阻塞主线，可拆出。
4. **显式类型应用**（turbofish 等价物）：`Some::<Int>` 或 `Some<Int>`？与现有
   文法如何共存？留到泛型函数切片统一设计。
5. **一等多态构造器**：`map(Some, xs)` 这类用法需要类型实参下推或高阶类型，
   不在本切片。
6. **`Result` 的错误上界**（Swift 的 `Failure: Error`）：需要 Error trait/
   接口，随类型类一起设计。
7. **局部遮蔽预置构造器**：允许内层作用域遮蔽（与 `print` 一致），但模块顶层
   保留。是否需要更严格的全局保留，待实现反馈。
