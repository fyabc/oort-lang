# OP 0026: 静态接口（interface）

- **状态**：Implemented（2026-11-22）
- **作者**：fyabc
- **创建日期**：2026-11-22
- **相关提案**：[OP 0005](0005-type-system.md)（类型系统主线）、
  [OP 0025](0025-static-object-model.md)（单继承与跨模块类型）、
  [OP 0007](0007-oort-object-object-model.md)（动态对象模型）
- **相关设计**：[design 04](../design/04-class-object-model.md)（类对象模型与
  trait 方案）、[design 14](../design/14-core-typechecking.md)（静态检查算法）、
  [spec 11](../spec/11-core-probe.md)

## 摘要

为 `oort-core` 增加**名义接口**：

- `interface I { def m(x: Int) -> Int }` 声明只有方法签名、没有状态与构造器的
  契约。
- `class C < Base, I1, I2`：至多一个类基类，其余为接口；类必须实现接口方法。
- 接口可继承多个接口：`interface J < I1, I2`。
- 接口是**纯静态类型**，没有运行时对象/类型值；接口基类在 HIR 降低时被过滤，
  后端与 `.obc` 不变。

本切片只做**抽象方法接口**。默认方法、属性访问器、泛型接口、`Self` 类型、
结构化 conformance 均留后续；属性访问器另立提案。

## 动机

1. 单继承解决了复用，但无法表达“横切能力”：一个类只能有一个类基类，而
   `Comparable`、`Serializable`、`Drawable` 等契约应可组合。
2. 跨模块类型标注（OP 0025 A）已经能导出类/enum 类型；缺少接口时，标准库与
   用户库只能导出具体类，调用方被迫依赖实现。
3. 运行时已有完整方法分派与 MRO；接口不需要额外状态或方法表，静态检查后即可
   擦除，这是成本最低的“多类型”支持。
4. 把接口与属性访问器拆开，可以先固定“方法契约 + 多重子类型”的语义，再单独
   评审访问器语法与运行时行为。

## 设计

### 1. 声明

```oort
interface Comparable {
    def compare(other: Int) -> Int
}

interface Named {
    def name() -> String
}

interface NamedComparable < Comparable, Named {
    def rank() -> Int
}
```

- `interface` 是新的模块顶层声明；`interface` 成为保留字（见“向后兼容”）。
- 接口体只允许**方法签名**：`def m(参数: 类型, ...) -> 返回类型`。
  参数与返回类型都必须显式标注；本切片文法不接受方法体（默认方法留后续），
  写成方法体会得到语法错误。
- 接口不能声明槽/属性、`__init__`、类方法、运算符方法、扩展方法或嵌套声明。
- 接口可继承多个接口；继承列表中的名字必须都是接口。接口继承图禁止循环。
- 本切片接口不能带类型参数、上界或默认类型实参；`interface Box[T]` 报
  “Generic interfaces are not supported yet.”

### 2. 类实现

```oort
class Point {
    val x: Int
    val y: Int

    def __init__(x: Int, y: Int) {
        this.x = x
        this.y = y
    }

    def compare(other: Int) -> Int { this.x - other }
    def name() -> String { "point" }
}

class RankedPoint < Point, Comparable, Named {
    def rank() -> Int { 1 }
}
```

- 类声明的基础列表沿用 `<`：
  - **至多一个类基类**，且如果出现，必须是列表第一项；
  - 其余项必须是接口；没有类基类时，可以只列接口。
  - `class C < I1, Base` 报“class base must appear first”；
  - `class C < A, B, I`（两个类）报“only one class base”；
  - 非类非接口（enum、集合、标量）报专用诊断。
- 类直接列出的接口记录在 `ClassType.interfaces`；基类已实现的接口由子类
  继承（`Derived` 也是 `I` 的子类型），不需要重复列出。
- 类必须实现所有直接接口（含接口继承链）的方法：
  - 参数元组必须与接口签名**精确一致**；
  - 返回类型允许协变（`is_assignable(interface_ret, class_ret)`）；
  - 缺方法、签名不符均定位到类名/方法名。
- 同一个类重复列出同一接口、或接口列表中出现重复名字报错。
- 两个接口要求同名方法时，一个类方法若同时满足两边签名即可；否则按各自
  要求报告冲突。接口自身继承时，如果父接口的同名方法签名不同，在接口声明处
  报冲突（没有默认方法可消解）。
- 类可以额外定义方法；接口方法通过接口类型调用，运行时按现有类方法分派。

### 3. 类型模型与子类型

新增名义 `InterfaceType(origin, name, interfaces, methods)`：

- 相等/哈希按 `(origin, name)`；方法表与父接口在注册后填充。
- `InterfaceType` 可沿 `interfaces` 查找方法；接口继承是名义的，多个父接口的
  同签名方法合并。
- `ClassType` 增加 `interfaces: tuple[InterfaceType, ...]`（直接实现）。
- `is_assignable` 新增：
  - `InterfaceType` ← `InterfaceType`：实际接口继承期望接口；
  - `InterfaceType` ← `ClassType`：类直接实现或经基类/接口继承实现期望接口；
  - `ClassType` ← `InterfaceType`：**不允许**（接口没有具体布局，不能自动
    向下转为某个类）。
- `join_types` 仍只沿类基类链取 LUB；不从多个共同接口猜一个 LUB（否则
  `A`、`B` 同时实现 `I1`/`I2` 时选择不确定）。分支若需要接口类型，用显式
  标注/期望类型下推。
- 接口类型可用于参数、变量、返回值、槽类型、集合元素与 ADT 载荷；接口值在
  运行时仍是对应类实例，因此身份相等/键语义与类一致。
- `print` 仍不接受类实例（包括接口静态类型的值）。`is` 仍不存在。

### 4. 方法与 `super`

- 接口没有默认实现，因此接口不进入类 MRO；`super` 仍只沿类基类链工作。
- 接口类型的表达式调用方法时，检查器从 `InterfaceType` 方法表取签名；运行
  时对象是对应类实例，沿用现有方法分派。
- 类实现接口的方法可以被基类提供；派生类覆盖时按普通方法覆盖规则检查，
  并继续满足接口签名。
- 本切片不引入 `super<I>.m()`、默认方法或接口静态方法。

### 5. 模块导出与导入

- 接口与类/enum 共享**类型命名空间**，参与重名检查；接口没有值命名空间。
- 模块类型导出快照包含本地声明的接口；导入方：
  - 类型标注可用 `m.I`；
  - `class C < m.I` 可用；
  - `from "m" import I` 与 enum 类型名一致，**显式拒绝**：
    `'I' is a type-only export; use 'm.I' to name the type.`。
- 接口类型导出/再导出遵循 OP 0025 的规则：只导出本模块声明，导入类型不自动
  再导出。
- 跨模块类实现接口时，类类型导出携带 `interfaces`，第三方模块对派生类的
  接口子类型判断仍成立。

### 6. 运行时与擦除

- 接口声明**不产生运行时值**；检查后完全擦除。
- 类声明的 HIR 降低只保留类基类表达式，接口项由检查器标记并从基类列表中
  过滤；`BuildClass` 的 bases 不含接口。接口不进入运行时 MRO。
- 接口类型标注、函数签名与槽类型不进入 HIR/字节码；`.obc` 格式不变。
- eval/vm 差分重点：类实现接口后的方法分派、跨模块接口标注、子类继承接口、
  接口值作为参数/返回值。

### 7. 跨方言

- 本切片接口只在 `oort-core` 可用；`oort-object` 中出现 `interface` 声明报
  `Interfaces are only supported in oort-core yet.`。
- 跨方言导入仍被拒绝；接口不会成为 FFI 边界的一部分。

### 8. 诊断

- `Interfaces are only supported in oort-core yet.`
- `Interface declarations are only allowed at module top level in oort-core.`
- `Generic interfaces are not supported in oort-core yet.`
- `Generic interface methods are not supported in oort-core yet.`
- `Duplicate member 'm' in interface 'I'.`
- `Interface base must be an interface, got C.`
- `Interface 'I' inherits interface 'A' more than once.`
- `Interface 'I' redeclares inherited method 'm' with a different signature.`
- `Interface method 'I.m' requires a return type annotation.`
- `Interface method 'I.m' cannot be named '__init__'.`
- `Interface 'J' inherits conflicting signatures for method 'm'.`
- `Class base must appear first in the base list; other entries must be interfaces.`
- `Only one class base is allowed; other base-list entries must be interfaces.`
- `Class 'C' does not implement interface 'I' method 'm'.`
- `Method 'C.m' does not match interface 'I.m'; expected (...) -> T.`
- `Class 'C' implements interface 'I' more than once.`
- `Interface 'I' has no runtime value; use it only in type positions.`
- 类型名用作值、缺失类型导出沿用 OP 0025 的模块诊断。

### 9. 明确不在本切片

- **默认方法**与 `super<I>.m()`（Kotlin/C#/Rust 的默认实现需要冲突消解）。
- **属性访问器**（`get`/`set`）与接口属性要求；另立提案。
- **泛型接口**、`Self` 类型、关联类型。
- **结构化 conformance**（Go/TypeScript 式“方法集匹配即实现”）。
- **单独 `impl I for C`** 语法、孤儿规则与跨模块一致实现。
- 接口的运行时反射/`is`/向下转型。
- 多类继承。

## 跨语言对比

| 语言 | 声明 | 类实现语法 | 接口数量 | 默认方法 | 状态 |
|------|------|-----------|---------|---------|------|
| Java | `interface I` | `class C extends B implements I1, I2` | 多个 | 支持 | 无实例字段 |
| Kotlin | `interface I` | `class C : B(), I1, I2` | 多个 | 支持 | 接口属性无 backing field |
| Swift | `protocol P` | `class C: B, P1, P2` | 多个 | 支持（协议扩展） | 无存储属性 |
| C# | `interface I` | `class C : B, I1, I2` | 多个 | 支持 | 无实例字段 |
| Rust | `trait T` | `impl T for C` | 多个 | 支持 | 无字段 |
| Go | `interface I` | 隐式（方法集） | 多个/嵌入 | 无 | 无字段 |
| **Oort** | **`interface I`** | **`class C < B, I1, I2`** | **多个** | **本切片不支持** | **无槽** |

依据：

- Java 只允许单类继承、通过接口获得多类型，并明确说明接口变量可以引用任意
  实现类实例：
  <https://docs.oracle.com/javase/tutorial/java/IandI/multipleinheritance.html>。
- Kotlin 接口可声明抽象方法与默认实现、不能保存状态，类可列多个接口：
  <https://kotlinlang.org/docs/interfaces.html>。
- Swift 类只有一个超类，但可遵从任意多个协议；有超类时必须列在协议之前：
  <https://docs.swift.org/swift-book/documentation/the-swift-programming-language/protocols/>。
- C# 接口定义方法/属性契约，类可列多个接口，接口不能有实例字段/构造器：
  <https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/types/interfaces>。
- Rust trait 只定义行为与方法默认实现，数据属于实现类型；多 trait 通过多个
  `impl` 组合：
  <https://doc.rust-lang.org/book/ch10-02-traits.html>。
- Go 接口按方法集结构化实现，不需要显式声明：
  <https://go.dev/ref/spec#Interface_types>。

## 替代方案

1. **`class C < B implements I1, I2`**：显式区分类与接口，但引入新关键字并让
   子类型列表有两种语法；本提案沿用 `<`，由检查器按类型种类校验。若后续
   认为 `<` 列表不够显式，可加 `implements` 作为可选写法。
2. **`impl I for C {}`（Rust 式）**：把实现移出类，需要孤儿规则与跨模块
   一致性检查；与当前类体两遍检查模型冲突，留作未来扩展。
3. **结构化接口（Go/TypeScript）**：不需要声明实现，但静态检查需全局方法集
   搜索，且意外 conformance 与名义设计冲突；拒绝。
4. **接口作为抽象类/带空槽的类**：会引入实例化、状态与构造顺序问题；拒绝。
5. **先支持默认方法**：需要接口进入 MRO、`super<I>` 与冲突消解；先做纯契约，
   避免与单继承 MRO 耦合。
6. **接口与属性访问器一起做**：访问器涉及动态对象模型与运行时属性分派，耦合
   过大；拆分评审。

## 向后兼容

- 新增保留字 `interface`：现有源码中若把 `interface` 用作变量/函数/参数名会
  失效。这是有意的破坏性语法变更，提案阶段需确认；备选是上下文软关键字，
  但会使声明规则更隐式。
- 现有类声明 `class C < B` 语义不变；`class C < A, B` 过去直接拒绝，现在若
  B 是接口则支持，否则仍报“only one class base”。
- `ClassType` 增加 `interfaces` 字段，默认空；已有类型模型/测试不受影响。
- 接口不改变运行时、HIR 指令或 `.obc` 版本。

## 实现计划

1. **A 语法与 AST（已实现）**：文法新增 `interface` 关键字、`interfaceDef` 与
   接口方法签名；AST `InterfaceDef`/`InterfaceMethod`；pass1 顶层/方言检查；
   类 base 列表保留 `ClassDef.bases`。
2. **B 类型模型与检查器（已实现）**：`InterfaceType`、`ClassType.interfaces`、
   assignability、接口继承与方法冲突、类实现检查；类型导出/导入复用
   OP 0025 类型表；值位置专用诊断。
3. **C 后端（已实现）**：检查器标记接口 base，HIR 降低与解释器执行都过滤
   接口项；eval/vm 差分通过；`.obc` 格式不变。
4. **D 文档/测试（已实现）**：spec 11/06、design 04/14、implementation 09、
   OP 0005/0025/roadmap/README/CHANGELOG；示例 `08_14_interfaces.ort`；
   跨模块接口、类实现、接口继承、冲突与误用测试。

## 未解决问题

- `interface` 是否接受硬关键字（本提案默认）还是上下文软关键字？
- 接口是否应允许默认方法（会引入接口 MRO 与 `super<I>`）；若允许，冲突规则
  采用 Kotlin 式显式消解还是 Java/C# 式覆盖？
- 接口方法是否需要显式的 `this`/`Self` 类型；本切片不引入 `Self`。
- 同名接口方法不同签名时，是否允许类用显式 `I.m` 实现消解（C# 式）；本切片
  暂不支持。
- 接口是否应参与 `join_types` 的 LUB 推断（当前拒绝，避免多接口歧义）。
- 属性访问器（`get`/`set`）的语法、运行时表示与接口属性要求，另立提案。
