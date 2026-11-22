# OP 0025: 静态对象模型——单继承与跨模块类型标注

- **状态**：Implemented（2026-11-22，增量 A/B）
- **作者**：fyabc
- **创建日期**：2026-11-22
- **相关提案**：[OP 0005](0005-type-system.md)（类型系统主线）、
  [OP 0007](0007-oort-object-object-model.md)（动态对象模型）、
  [OP 0016](0016-equality-protocol.md)（相等协议）、
  [OP 0017](0017-oort-core-thin-probe.md)（薄探针）、
  [OP 0022](0022-generic-adts.md)、[OP 0024](0024-adt-and-slot-equality.md)
- **相关设计**：[design 03](../design/03-type-system-design.md)、
  [design 04](../design/04-class-object-model.md)、
  [design 14](../design/14-core-typechecking.md)、
  [spec 05](../spec/05-classes.md)、[spec 11](../spec/11-core-probe.md)

## 摘要

P6 静态对象模型的前两块：

- **跨模块类型标注**：导入模块的类型用 `m.Type` 引用，类型导出与值导出分离；
  类型标注只在检查期存在，运行时不新增类型值。
- **单继承**：`class Derived < Base`；子类沿基类链继承槽/方法，支持覆盖、
  `super` 与子类型赋值；多基类显式拒绝。

接口（interface）与属性访问器（getter/setter）语法尚未确定，留作后续提案；
泛型类、多继承、元类仍不在本切片。

## 动机

1. `oort-core` 已支持固定槽、方法、确定赋值与身份相等，但类之间不能复用；
   任何共享行为只能靠扩展方法或复制。
2. 跨模块类型名目前不可标注：函数/值可以导出，但调用方无法写
   `def area(s: shapes.Shape) -> Int`。这是模块化静态代码的基本缺口，也是
   接口/标准库类型的前置。
3. 运行时与 HIR/VM **已经**支持 C3 MRO、继承槽初始化与 `super`；本切片
   主要是把检查器/类型模型补齐，后端改动很小。
4. 先做单继承与类型标注，可以把「继承语义」和「接口/属性语法」分开评审，
   避免一次引入过多表面语法。

## 设计

### 1. 跨模块类型标注（实体导入 + `m.Type`）

#### 原则：一个实体，两个命名空间

Oort 的模块导出的是**实体**；每个实体可以占值命名空间、类型命名空间，或两者：

| 声明 | 值命名空间 | 类型命名空间 |
|------|-----------|--------------|
| `val` / `def` | 值 | — |
| `class C` | 构造器值 | 类类型 |
| `enum E { A, B }` | 构造器 `A` / `B` | 类型 `E` |
| 预置 `Option`/`Result` | 构造器 | 类型（全局可见，不从模块导出） |

**导入规则：`import` 导入实体；实体在哪些命名空间存在，就在哪些命名空间可用。**

- `import "./m" as m`：`m.Name` 在值位置解析值命名空间，在类型位置解析类型命名空间。
- `from "./m" import C`（类）：同时绑定构造器值与类类型。类声明本身就有两个命名空间，导入的是这个实体（Python/Rust 式）。
- `from "./m" import Red`（enum 构造器）：只绑定值。
- `from "./m" import E`（enum 类型名）：**显式拒绝**——enum 类型名没有运行时值；诊断提示用 `m.E`。
- `from "./m" import type E`：本切片不引入；作为未来显式 type-only 语法保留（TypeScript `import type` 先例）。
- 类型标注中的 `m.E` / `m.C` 始终可用；泛型 enum 写 `m.Tree[Int]`。

#### 语法

```oort
# shapes.ort
#lang oort-core

class Shape {
    val name: String

    def __init__(name: String) {
        this.name = name
    }
}

enum Color { Red, Green }

enum Tree[T] {
    Leaf(value: T),
    Branch(left: Tree[T], right: Tree[T])
}
```

```oort
# main.ort
#lang oort-core

import "./shapes" as shapes
from "./shapes" import Shape

val s: shapes.Shape = shapes.Shape("box")
val t: Shape = Shape("box")              # 类导入同时带入构造器与类型
val c: shapes.Color = shapes.Red         # enum 类型用模块限定
def paint(shape: Shape, color: shapes.Color) -> String {
    shape.name
}

# 不允许：enum 类型名没有运行时值，需写 m.E。
# from "./shapes" import Color
```

- 类型引用复用现有**点号表达式语法**：`模块别名.类型名`。
- 泛型 enum 可写：`shapes.Tree[Int]`、`shapes.Pair[Int, String]`。
- `import "./shapes"` 未写 `as` 时，模块别名按现有规则从文件名派生（`shapes`）。
- `from` 导入类时同时建立类型别名；enum 类型名只能通过模块限定引用。

#### 类型导出与导入绑定

- 检查器在模块结束时把该模块**自己声明**的类与 enum 模板快照到
  `CoreModuleInfo.type_exports` / `ModuleType.type_exports`，与值导出
  （`exports`）分开。
- 不导出预置 `Option`/`Result`（它们在每个 core 模块隐式可见）；
  不自动再导出从其他模块导入的类型。
- `from "m" import C` 在检查器中绑定两个别名：值（构造器）与类型
  （`ClassType`）；检查器维护模块级 `imported_types` 映射，供
  `resolve_annotation(Name)` 使用。值位置仍查值作用域。
- `from "m" import E`（enum 类型名）在值导出中不存在、在类型导出中存在：
  报 `'E' is a type-only export; use 'm.E' to name the type.`，不建立值绑定。
- 值命名空间与类型命名空间仍然独立：
  - 值表达式 `shapes.Shape` 解析为构造器值（现有导出）；
  - 类型标注 `shapes.Shape` 解析为 `ClassType`；
  - enum 类型名只存在于类型空间；`shapes.Red` 是构造器值，不能当类型；
  - 值表达式 `shapes.Color` 报错（没有运行时值）。

#### 运行时与擦除

- 类型标注、函数签名、槽类型在检查后擦除；`m.Type` **不会**在运行时求值，
  因此不需要把类型名导出为运行时值，也不需要“类型导入擦除/跳过”机制。
- 普通 `from` 导入仍是值导入：类构造器本来就有运行时值；enum 类型名本来就
  没有。`from "m" import Color` 在检查器即被拒绝，不会进入运行时。
- 基类子句是例外：`class C < shapes.Shape` 中的 `shapes.Shape` 是运行时
  表达式，取模块里的类对象（现有值导出）。检查器在基类位置解析类型表，
  HIR 仍按普通属性表达式降低；两边一致。

#### 跨方言行为

| 场景 | oort-object | oort-core |
|------|-------------|-----------|
| `from "m" import C`（类） | 绑定构造器值（今天的行为） | 绑定构造器值 + 类类型 |
| `from "m" import Red`（enum 构造器） | 不存在 enum | 绑定构造器值 |
| `from "m" import E`（enum 类型） | 不存在 enum | 显式拒绝，提示 `m.E` |
| 标注中的 `m.C` / `m.E` | 标注被忽略，不求值 | 类型检查，运行时擦除 |
| 值表达式 `m.C` | 模块里的类对象 | 构造器值（类型表不参与） |
| 值表达式 `m.E` | 模块里没有该值 | 错误（enum 类型名不是值） |

关键点：类型标注永远不参与运行时求值，所以 `m.E` 只在 core 检查器里存在；
object 方言根本不碰它。普通 import 的运行时语义不变。

#### 诊断

- `Unknown module 'shapes' in a type annotation.`
- `Module 'shapes' does not export type 'Shape'.`
- `Module 'shapes' exports 'Red' as a value, not a type.`
- `'Color' is a type-only export; use 'shapes.Color' to name the type.`
- `Type 'shapes.Tree' requires 1 type argument(s); write shapes.Tree[...].`
- 对非泛型类型加实参沿用 “does not take type arguments”。
- 类型名作值：沿用值导出的 `Module ... does not export 'Color'` / 专用类型值诊断。

#### 为什么采用实体导入

- 类在本地声明时既是构造器值又是类型；如果 `from` 只导入值，会出现
  “本地类能当类型、导入类不能”的不对称，这是最大的惊讶点。
- Python/Rust/Kotlin/Scala 的 `from`/`use`/`import` 都按实体导入，类名在
  两种位置都可用；TypeScript 的普通 import 也带入类型，`import type` 只是
  显式优化。
- enum 类型名没有运行时值，强行让 `from` 导入会需要运行时跳过或占位；
  用模块限定的 `m.E` 与 Go 的 `pkg.Type` 一致，且不引入隐藏规则。
- 运行时不需要“类型导入擦除”机制：普通 import 仍是值导入，enum 类型名
  在检查器即被拒绝，`m.Type` 只出现在被擦除的标注中。

### 2. 单继承

#### 语法与类型模型

```oort
class Base {
    val id: Int

    def __init__(id: Int) {
        this.id = id
    }

    def describe() -> String {
        "base"
    }
}

class Derived < Base {
    val extra: Int

    def __init__(id: Int, extra: Int) {
        super.__init__(id)
        this.extra = extra
    }

    def describe() -> String {
        super.describe() + "+derived"
    }
}
```

- 仅允许**一个**基类；`class C < A, B` 显式拒绝（多继承留后）。
- `ClassType` 增加 `bases: tuple[ClassType, ...]`；`slot()`/`method()` 沿基类
  链查找（运行时仍用完整 C3 MRO）。
- 名义相等仍按 `(origin, name)`；子类化不改变相等。
- **子类型**：`Derived` 可赋给 `Base`（沿 bases）；反向不可。
- `join_types(Base, Derived)` 返回 `Base`，使 `if` 两分支可合并。
- 函数类型参数改为**逆变**（这是引入子类型后的必要修正，见 §4）。

#### 槽与构造

- 子类不得重新声明基类槽（固定布局，禁止遮蔽）。
- 基类槽初始化器在**每个实例**构造时先于派生类初始化器执行（运行时已按
  MRO 基类优先执行）；派生类 `__init__` 只负责基类未初始化槽与自身槽。
- 派生类 `__init__` 若基类存在未初始化槽，必须通过 `super.__init__(...)`
  或直接赋值覆盖；确定赋值分析纳入继承槽，并把 `super.__init__(...)`
  视为“已初始化基类未赋值槽”（基类 `__init__` 自身已通过检查）。
- 无 `__init__` 的派生类：基类槽必须全部有初始化器，否则报错；若继承的
  构造器带参数，也要求显式声明 `__init__`（运行时 `Class()` 会沿 MRO 调用
  继承构造器，静态构造签名必须一致）。
- `super.__init__(...)` 只允许在派生类 `__init__` 中；参数按基类
  `__init__` 签名检查。

#### 方法覆盖与 `super`

- 子类可覆盖基类方法：参数类型必须与基类完全一致；返回类型允许协变
  （`is_assignable(base_ret, derived_ret)`）。
- 不加 `override`/`open` 关键字：Oort 的小型语法不做访问修饰；动态方言
  也允许直接覆盖。若未来需要显式意图，可另提案。
- `super` 只在子类方法/`__init__` 中合法：
  - `super.method(...)` 从基类解析方法（跳过子类覆盖）；
  - `super.__init__(...)` 解析基类构造器；
  - 基类不存在或方法不存在时给专用诊断。
- `this` 的类型仍是派生类；方法体内可访问继承槽/方法。

#### 运行时/HIR

- 运行时 `OortType` 已有 bases/C3、`slot_definitions()` 基类优先、
  `initialize_instance_slots` 与 `check_instance_slots`；HIR `BuildClass`
  已传 bases，VM 已支持 `SUPER`。预计**无需修改**后端，只补差分测试。
- 静态类实例相等保持身份（OP 0024）；继承不引入槽结构相等。

### 3. 明确不在本切片

- **接口**：需要新关键字/语法与“只有签名、无状态”的类型规则；另立提案。
- **属性访问器**：`get`/`set` 语法未定；另立提案。
- **多继承**：运行时支持，但静态槽布局、确定赋值、接口混用复杂；先拒绝。
- **泛型类、元类、抽象方法、按需虚派发优化**。

### 4. 子类型引入后的必要修正

本提案落地前 `is_assignable` 对函数参数是**协变**比较（没有子类型时等价于
相等）。引入类子类型后已改为：

- 参数：**逆变**（`is_assignable(actual_param, expected_param)`）；
- 返回：协变（`is_assignable(expected_ret, actual_ret)`）。

否则 `(Derived) -> R` 会被误判为可赋给 `(Base) -> R`。容器保持协变
（core 容器不可变）；`_is_same_container` 仍要求双向可赋值，因此
`List[Derived] == List[Base]` 仍为假。

## 正交性检查

- **与类型系统**：新增名义子类型；相等仍按名义；`join_types` 增加 LUB。
- **与 ADT**：enum 不参与继承；`match` 不受影响。
- **与模块**：类型导出与值导出分表；导入类型只在检查期；基类表达式仍走
  值导入。
- **与相等/键**：类实例身份相等/键不变；子类型不改变哈希身份。
- **与后端**：`.obc` 无格式变化（bases 已在 ClassSpec 中）；Rust spike
  不涉及静态类。
- **与接口/属性**：本切片不引入语法，避免与继承语义耦合。

## 跨语言对比

| 语言 | 跨模块类型写法 | 类继承 | 覆盖/`super` |
|------|----------------|--------|--------------|
| Python | `module.Class` | 多继承 | `super().m()`，无关键字 |
| Go | `pkg.Type`（qualified identifier） | 无类继承（组合/嵌入） | — |
| Swift | `Module.Type` | 单类继承 + 多协议 | `override`，`super` |
| Kotlin | `a.b.C` / import | 单类继承 + 多接口 | `override`/`super`，类默认 final |
| Scala | `pkg.C` / import | 单类 + 多 trait | `override`/`super` |
| Rust | `use path::Type` | 无类继承（trait） | — |
| **Oort** | **实体导入：`from` 类带入值+类型；enum 类型用 `m.Type`** | **单类继承（本切片）** | **`super`，不加 override 关键字** |

依据：

- Python 模块是命名空间对象，类通过 `module.ClassName` 访问：
  <https://docs.python.org/3/tutorial/modules.html>。
- Go 的 `package.Type` 是 qualified identifier，不走普通字段选择：
  <https://go.dev/ref/spec#Qualified_identifiers>。
- Swift 类单继承、协议多遵从，`Module.Type` 可用：
  <https://docs.swift.org/swift-book/documentation/the-swift-programming-language/inheritance/>。
- Kotlin 单类继承、`open`/`override`/`super` 与基类初始化顺序：
  <https://kotlinlang.org/docs/inheritance.html>。
- Scala case class/普通类的覆盖与 `super` 语义见 Scala Tour。
- Rust 的 `use` 按实体导入，可同时引入类型/值命名空间；TypeScript 普通 import
  也带入类型，`import type` 是显式优化：
  <https://www.typescriptlang.org/docs/handbook/release-notes/typescript-3-8.html>。

## 替代方案

1. **所有类型都必须模块限定（旧稿 `m.Type`）**：运行时最简单，但本地类可当
   类型、导入类只能当值，造成最大不对称；拒绝。
2. **`from` 隐式导入 enum 类型名并在运行时擦除**：需要运行时区分类型/值或
   “类型占位”，是隐藏规则；拒绝。
3. **所有类型导入都必须写 `import type`**：显式，但类同时作值和类型时要写
   两条导入；TypeScript 先例，留作后续可选语法，不作默认。
4. **完全限定路径类型 `"./shapes".Shape`**：无模块别名，但语法丑陋且与
   表达式冲突。
5. **先做多继承**：运行时支持，但静态槽布局、构造顺序、确定赋值与接口
   混用复杂；先单继承。
6. **要求 `override`/`open` 关键字**：意图更显式，但引入新关键字并改变现有
   类声明；Oort 当前无访问修饰，先保持简单。
7. **接口用基类模拟**：无法表达“只有方法、无槽”的契约；另提案。

## 向后兼容

- 现有单类定义语义不变；`class C < A` 从“显式拒绝”变为支持。
- 多基类仍拒绝（新诊断：仅支持一个基类）。
- 新语法 `m.Type` 只出现在类型位置；值位置的 `m.X` 行为不变。
- 函数类型参数改为逆变：在无子类型的现有代码中行为不变；含类子类型的新代码
  才可观察。
- `.obc` 格式不变；HIR/VM 已有 bases/super。

## 实现计划

1. **A 跨模块类型（已实现，2026-11-22）**：`CoreModuleInfo`/`ModuleType` 增加
   类型导出；模块结束快照；`from` 导入类时同时建立 `imported_types` 类型别名；
   `resolve_annotation(Name)` 查类型别名，`Attribute` 查模块类型导出；
   `_resolve_container_type` 支持 `m.Tree[...]`；`from` 导入 enum 类型名给
   专用诊断；值上下文仍走值导出；诊断与测试。实现说明见
   [design 14 §10](../design/14-core-typechecking.md)。
2. **B 单继承（已实现，2026-11-22）**：`ClassType.bases`、MRO 查找、
   子类型/`join_types`；`visit_class_def` 单基类、槽禁止遮蔽、覆盖检查；
   `super` 类型与调用；确定赋值纳入继承槽与 `super.__init__`；函数参数逆变
   修正。实现说明见 [design 14 §11](../design/14-core-typechecking.md)。
3. **C 后端验证**：eval/vm 差分（继承槽初始化、super init/method、覆盖、
   跨模块基类）；`.obc` round-trip 不变。
4. **D 文档/测试**：spec 05/07/11/06、design 04/14、implementation 09、
   OP 0005/roadmap/README/CHANGELOG、examples。

## 未解决问题

- 是否引入 `from "m" import type E`（显式 type-only 导入）；本切片先用
  `m.E`，未来可加。
- 类型再导出：`from "./a" import Shared` 后，模块 `m` 是否能把 `Shared` 作为
  类型再导出？本切片暂不做。
- ~~方法覆盖是否要求返回类型精确相同还是允许协变~~（已决：参数精确、返回协变）。
- ~~`super.__init__` 视为初始化基类槽的确定赋值规则是否足够~~（已实现：基类
  `__init__` 自身已通过全路径检查）。
- 接口的语法（`interface` 关键字 vs 基类列表 vs `implements`）与运行期表示。
- 属性访问器的语法（Kotlin 风格 `get()`/`set()` vs 独立 `def name`）。
