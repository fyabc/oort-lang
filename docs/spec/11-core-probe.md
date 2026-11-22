# `oort-core` 薄探针

本页描述 `#lang oort-core` 当前**已实现**的最小静态子集。它不是完整的
`oort-core` v1：已实现 Int/Float/Bool/String、集合与循环、函数、泛型 ADT
（`enum E[T]`，含声明处变型）、内建 `Option`/`Result` 与 `match`、静态类
与固定槽，但跨方言 FFI 尚未实现。
设计取舍见 [OP 0017](../proposals/0017-oort-core-thin-probe.md) 与
[OP 0022](../proposals/0022-generic-adts.md)。

## 启用

```oort
#lang oort-core

def add(a: Int, b: Int) -> Int {
    a + b
}

print(add(1, 2))
```

- 必须显式写 `#lang oort-core`；省略首行仍是 `oort-object`。
- core 模块可以导入其他 core 模块（`import` / `from` 均可）；跨方言与
  native 模块导入会被拒绝。
- REPL 固定使用 `oort-object`；在 REPL 输入 `#lang` 会报错。

## 类型

| 类型 | 位置 |
|------|------|
| `Int` | 参数、变量、返回值、表达式 |
| `Float` | 参数、变量、返回值、表达式 |
| `Bool` | 参数、变量、返回值、条件、逻辑运算 |
| `String` | 参数、变量、返回值、表达式 |
| `Unit` | **仅函数返回类型**；声明的内部类型，不是变量类型 |
| `enum` 类型 | 参数、变量、返回值、字段类型；单态 `Shape` 或泛型 `Option[Int]`，名称在模块内唯一 |
| 内建 ADT | `Option[T]`（`Some`/`None`）与 `Result[T,E]`（`Ok`/`Err`）；每个 core 模块隐式可用 |
| 集合类型 | `List[T]`、`Set[T]`、`Dict[K, V]`、`Tuple[T1, ...]`；参数/变量/返回值/字段 |
| 类类型 | 类名；参数、变量、返回值、槽类型；名义相等 |
| 函数类型 | `Int -> Bool`、`(Int, Bool) -> Int`、`() -> Unit`；参数/变量/返回值/字段 |

- `Int`、`Float`、`Bool`、`String` 严格区分，没有隐式转换或 truthiness：
  `val x: Float = 1` 报 `Expected Float, got Int.`，必须写 `1.0`。
- 数值运算允许 Int/Float 混合；结果是否为 Float 见“表达式”。
- 集合类型参数化且结构相等：`List[Int]` 与 `List[Float]` 不同，
  不做元素类型提升；`Tuple[Int, Bool]` 可异构。
- 空集合字面量必须能从期望类型推断（标注、参数、返回值等）。
- `Unit` 与模块值不能存入集合；`Set` 元素与 `Dict` 键必须是
  `Int`/`Float`/`Bool`/`String`/enum/可哈希 `Tuple`。
- 静态 `Unit` 在运行时对应 `null`；`print` 返回 Unit。
- 内部还有 `Unknown`（错误恢复）与 `Never`（所有路径 `return`）。

## 声明

- `val`/`var` 必须初始化，且只允许单目标：
  `val x = 42`、`var n: Int = 0`。
- 有标注时检查初始化器；无标注时从初始化器局部推断。
- `var` 可重新赋值；`val`、函数参数与函数名不可变。
- 不允许重复声明同名变量（包括模块顶层）。
- `Unit` 不能出现在变量或参数标注中；`val x = print(1)` 也会被拒绝。

## 函数

```oort
def fact(n: Int) -> Int {
    if n <= 1 { 1 } else { n * fact(n - 1) }
}

def show(n: Int) -> Unit {
    print(n)
}
```

- 顶层 `def` 与非匿名的 `do(...)` lambda；不允许嵌套 `def`、方法、扩展或
  运算符定义。
- 每个参数都必须标注；参数只支持普通位置参数。**返回类型可省略**：顶层
  `def` 与 lambda 的返回类型可从函数体推断（各 `return` 类型与尾表达式类型
  合并）；显式标注时仍按标注检查。类方法同样可推断（按调用依赖拓扑序；
  递归环上的方法仍需标注），见 [design 14](../design/14-core-typechecking.md)。
- 返回值遵循 Oort 的运行语义：函数体最后一个表达式的值，或显式 `return`。
- 非 Unit 函数必须所有路径返回值，或函数体最后一个表达式的类型可赋给返回类型。
- 裸 `return` 只允许用于 `-> Unit` 函数（推断出 Unit 的函数同样允许）。
- 顶层函数与变量按源码顺序可见；允许自递归，不支持前向引用或互递归。
  **自递归函数必须显式标注返回类型**（推断无法穿过递归调用确定类型，对齐
  Kotlin/Scala）；缺标注报 `Recursive function 'f' requires a return type
  annotation`。算法见 [design 14](../design/14-core-typechecking.md)。
- 函数值可存入变量/ADT 字段、作为实参、返回和调用；函数类型使用
  `(参数类型, ...) -> 返回类型`，`()` 表示零参。函数值不可打印/比较。
- `->` 在函数类型中右结合：`Int -> Int -> Int` 等同于
  `Int -> (Int -> Int)`；需要函数参数时写 `(Int -> Int) -> Int`。
- 多参数函数**不会自动柯里化**；手动柯里化用返回 lambda：
  `do(a: Int) -> Int -> Int { do(b: Int) -> Int { a + b } }`。
  函数值链式调用 `add(1)(2)` 可用。
- lambda 必须写显式参数列表；**返回类型可省略**（从体推断，或由期望函数类型
  下推，如 `val f: (Int) -> Int = do(x: Int) { x }`）。匿名 `$0` lambda、泛型
  lambda、默认值/变长参数 lambda 第一切片不支持。
- 期望类型会传播到 `if` 分支、块最后表达式、`match` arm 与调用实参：
  标注、赋值、返回和函数体的期望类型会下推，错误定位到具体分支/实参。

## 模块导入

```oort
# lib.ort
#lang oort-core
val base: Int = 10
def add(a: Int, b: Int) -> Int { a + b }

# main.ort
#lang oort-core
from "./lib" import add, base
import "./lib" as l

print(add(base, 2))
print(l.add(1, 2))
```

- 只允许 core→core；目标模块必须是同一方言。
- `import "m"` 绑定模块命名空间；`m.f(...)` 与 `m.x` 可用，但
  `m.x = ...` 不可写。
- `from "m" import f, g as h` 直接绑定导出的名字；导入名不可变。
- 模块导出所有顶层名字（函数、`val`/`var`、再导出的导入名）。
- import 与运行时一致，会被提升到模块正文之前；因此函数体可以引用
  稍后出现的 import。
- 循环导入在编译期报错；缺失导出、跨方言导入与 native 模块导入也会报错。

## 表达式

| 形式 | 规则 |
|------|------|
| `1`、`1.5`、`true`、`"x"` | `Int`、`Float`、`Bool`、`String` |
| `x` | 查词法作用域；未知名报错 |
| `+x`、`-x` | 数值 -> 同类型数值 |
| `not x` | `Bool -> Bool` |
| `a + b`、`-`、`*`、`//`、`%` | 两个数值 -> `Int`，任一为 Float 则 `Float` |
| `a / b` | 两个数值 -> `Float` |
| `a < b`、`<=`、`>`、`>=` | 两个数值或两个 String -> Bool |
| `a == b`、`!=` | 两个数值、两个 Bool、两个 String 或同类型集合 -> Bool；`1 == 1.0` 允许 |
| `[1, 2]`、`(1, true)`、`{: ... :}`、`{. ... .}` | 集合字面量；同质 List/Set/Dict 推断，Tuple 可异构 |
| `xs[i]` | List/Tuple/String 用 Int，Dict 用键类型；Tuple 字面量下标检查越界 |
| `len(x)` | String 或集合 -> Int |
| `this`、`obj.slot`、`obj.method` | 方法内的当前实例、槽读取、方法引用 |
| `this.slot = value` | 槽赋值；`val` 只读，固定布局拒绝未声明槽 |
| `C(...)` | 构造器调用；参数来自 `__init__`，无 `__init__` 时为零参 |
| `for x in xs { ... }`、`while c { ... }` | 循环表达式，结果 Unit；循环变量不可变 |
| `break`、`continue` | 仅循环内；`break value` 显式拒绝 |
| `a and b`、`a or b` | `Bool, Bool -> Bool` |
| `f(...)` | 仅位置实参；精确元数；实参类型匹配；被调者可为函数值 |
| `do(x: Int) -> Int { ... }` | 函数值；参数必须标注，返回可省略（推断/期望下推） |
| `if c { ... } else { ... }` | 条件 Bool；两分支类型一致 |
| `match e { ... }` | `e` 必须是 enum；arm 为 `pattern => expr`；结果类型为各 arm 的合并 |
| `{ ... }` | 块的值是最后一条语句的值；空块为 Unit |
| `print(...)` | 任意个 Int/Float/Bool/String/Unit/enum 实参 -> Unit；可被用户定义遮蔽 |

`if` 没有 `else` 时类型为 Unit。`Never`（例如 `return`）可与任一分支类型合并。

## 集合与循环

```oort
val xs: List[Int] = [3, 1, 2]
val pair: Tuple[Int, Bool] = (7, true)
val scores: Dict[String, Int] = {: "a": 1, "b": 2 :}
val tags: Set[String] = {. "core", "static" .}

var total = 0
for x in xs {
    total = total + x
}
while total > 0 {
    total = total - 1
}
```

- 类型写法：`List[T]`、`Set[T]`、`Dict[K, V]`、`Tuple[T1, ...]`；
  可嵌套（如 `Dict[String, List[Int]]`）。裸 `List`/`Tuple` 等需要参数。
- List/Set/Dict 字面量要求元素（键/值）类型可合并；空字面量需要期望类型，
  例如 `val xs: List[Int] = []`。
- Tuple 字面量可异构，长度即类型的一部分；`()` 推断为 `Tuple[]`。
- 下标：List/String 用 Int；Dict 用键类型；Tuple 用 Int。
  Tuple 的**非字面量**下标要求所有元素同类型；字面量下标检查边界，
  负数按运行时规则从尾部计数。
- `len` 是 core 的特殊内建（与 `print` 一样可被用户绑定遮蔽），
  只接受 String 或集合；集合的 `.length` 属性在 core 中仍被拒绝。
- `for` 遍历 List/Set 元素、Dict 键、String 字符，以及元素同类型的 Tuple；
  循环变量可用 `for x: Int in xs` 显式标注，必须与元素类型兼容。
  多变量解包第一切片不支持。
- `while` 条件必须是 Bool；`break`/`continue` 只能在循环内。
  `break value` 与把循环结果当值使用（循环类型为 Unit）均不支持。
- 集合相等要求同类型（`List[Int]` 对 `List[Int]`）；跨 List/Tuple 或
  元素类型不同显式拒绝。集合大小比较（`<` 等）在 core 中尚未支持。
- core 集合不可原地修改：下标赋值、切片与 `in` 第一切片均未实现。

## 静态类与槽

```oort
class Point {
    val x: Int
    val y: Int
    var label: String = "point"

    def __init__(x: Int, y: Int) {
        this.x = x
        this.y = y
    }

    def sum() -> Int { this.x + this.y }
}
```

- `class` 只能声明在模块顶层；第一切片不支持继承、元类、泛型类、类方法、
  运算符方法与扩展方法，类体只允许槽（`val`/`var`）和方法声明。
- 槽是**固定布局**：每个槽必须在类体中声明且带类型标注；给未声明槽或方法
  赋值会报错，不存在动态字段。
- 槽初始化器可选；有初始化器的槽在**每个实例**构造时、`__init__` 之前按
  声明顺序求值（无继承时就是类体顺序）。初始化器不能引用 `this`。
- `var` 槽可在任意方法中赋值；`val` 槽只能由初始化器赋值，或在 `__init__`
  中赋值一次，且不能在循环中赋值。
- **确定赋值**：没有初始化器的槽必须在 `__init__` 的所有落空路径上赋值；
  在赋值前读取 `this.slot`、提前 `return`、缺少分支赋值都会报错。
  循环体不会让赋值在循环之后“确定”；方法调用内部是否初始化槽不在分析范围内。
- `__init__` 参数必须标注；返回类型可省略（视为 Unit），显式标注时必须是
  Unit。构造函数是类名值 `C(...)`，参数即 `__init__` 参数。
- 方法参数必须标注；**返回可省略**（按方法调用依赖序推断，见
  [design 14](../design/14-core-typechecking.md)）；**递归环上的方法需显式返回
  标注**。`this` 的类型是当前类。方法可读取槽、调用其他方法、返回 `this`，
  方法引用可作为函数值传递。
- 类实例不可打印、不可用 `==` 比较；类类型可用于参数/变量/返回值与槽类型。

## ADT（`enum`）与 `match`

```oort
enum Shape {
    Circle(radius: Int),
    Rect(width: Int, height: Int),
    Empty
}

def area(shape: Shape) -> Int {
    match shape {
        Circle(r) => r * r * 3,
        Rect(w, h) => w * h,
        Empty => 0
    }
}
```

泛型 ADT 用 `[T]` 声明类型参数，用 `Name[...]` 应用：

```oort
enum Maybe[T] {
    Just(value: T),
    Nothing
}

enum MyList[T] {
    Cons(head: T, tail: MyList[T]),
    Nil
}

enum Producer[out T] {
    Get(value: T),
    Empty
}

enum Consumer[in T] {
    Use(f: (T) -> Int)
}

val a: Option[Int] = Some(1)          # Option 是内建 ADT（见下）
val b = Some("text")                  # 推断为 Option[String]
val xs: MyList[Int] = Cons(1, Cons(2, Nil))
val m: Maybe[Int] = Just(2)           # 用户定义的泛型 enum

def unwrap(o: Option[Int]) -> Int {
    match o { Some(v) => v, None => 0 }
}
```

完整模式示例：

```oort
def classify(n: Int) -> String {
    match n {
        0 => "zero",
        1 | 2 | 3 => "small",
        x if x < 0 => "negative",
        _ => "large"
    }
}

def at_origin(p: Tuple[Int, Int]) -> Bool {
    match p {
        (0, 0) => true,
        _ => false
    }
}
```

- `enum` 只能出现在模块顶层；必须至少有一个构造器；字段类型必须标注，
  可为任意已支持的静态类型（标量、集合、函数、此前声明的 enum/类，不能是
  Unit）；支持自递归。enum 类型名
  与构造器按源码顺序可见，不支持前向/互递归枚举。
- 构造器是普通可调用值：`Circle(2)`；零参构造器是值：`Empty`。
- 字段名用于声明/文档；构造与模式都按**位置**绑定，暂不支持命名字段。
- 构造器名进入模块值命名空间，可被 `from`/`import` 导出；enum 类型名只进入
  类型命名空间，暂不支持跨模块类型注解。
- `match` 的 scrutinee 可为 enum、`Bool`、`Int`、`Float`、`String` 或 `Tuple`；
  arm 用 `,` 或换行分隔。
- 模式：`_`、绑定名、构造器（可嵌套）、字面量（Int/Float/String/Bool，数字可带
  `-`）、元组（`()`、`(p1, p2)`；`(p)` 是分组）、或模式 `p1 | p2`。
  - 裸名字若命中当前 enum 的零参构造器：按构造器处理并同时绑定该名字；
    否则按普通绑定处理。
  - 字面量模式必须与期望类型精确一致（`Int` 不匹配 `Float`，反之亦然）。
  - 或模式的每个分支必须绑定相同的名字集合与兼容类型；绑定不可变。
- **守卫**：`pattern if cond => body`；`cond` 必须 Bool，可引用 pattern 绑定，
  按 arm 作用域求值；`1 | 2 if c` 的守卫作用于整个或模式。守卫失败时继续下
  一个 arm（不回溯或模式的其他分支）。
- 每个 arm 独立作用域；重复绑定报错。
- arm 体类型必须可合并；`Never` 可参与合并。
- **嵌套穷尽性**：按 Maranget usefulness 检查。ADT 构造器集合、`Bool`
  （`true`/`false`）与元组（单构造器）是完整签名；Int/Float/String 是无限域，
  必须由 `_`/绑定覆盖；或模式按分支展开；**守卫 arm 不计入覆盖**。缺失时
  报告 witness：`Match is not exhaustive; missing: Some(false).`、
  `... missing: (false, _).`、`... missing: _.`。
- **泛型参数**：`[T]` / `[T, E]`；参数名不得遮蔽内建/已知类型，重复参数报错。
  可选声明处变型 `[out T]`（协变）/ `[in T]`（逆变），缺省不变型；`out` 仍是
  普通标识符（`val out = 1` 合法），非法变型文本报
  `Expected 'in' or 'out' before type parameter ...`。上界 `T: Bound` 与类型参数
  默认值显式拒绝（见 [OP 0022](../proposals/0022-generic-adts.md)）。
- **变型检查**：声明处按使用位置检查。payload 是构造器产出的数据，起始为
  协变位置；函数参数翻转极性；内建集合（`List`/`Set`/`Dict`/`Tuple`，不可变）
  保持协变；嵌套 ADT 按其实参的声明变型复合，不变型实参使出现位置变为不变。
  `out T` 只能出现在协变位置，`in T` 只能逆变；违反时定位到字段：
  `Type parameter 'T' is declared covariant ('out') but appears in a
  contravariant position in constructor 'B'.` 当前没有子类型（无继承/接口/顶
  类型），变型关系尚不可观察，但检查已启用，为后续对象模型预置健全性。
- **类型应用**：`Option[Int]`、`Pair[Int, String]`，可嵌套（`Option[List[Int]]`）；
  实参个数必须匹配；裸 `Option` 报“requires N type argument(s)”；单态 enum
  不接受实参。
- **构造器多态**：`Some` 的类型是 `(T) -> Option[T]`。类型实参由**期望类型**
  （`val x: Option[Int] = Some(1)`）或**实参类型**（`Some(1)` 推断
  `Option[Int]`）确定。求不出的参数是错误：`val x = None`、`val r = Ok(1)`
  （`E` 未知）需要标注；构造器作值仅在有期望函数类型时可用
  （`val f: (Int) -> Option[Int] = Some`）。
- **模式载荷**：match 按 scrutinee 的实参代换构造器载荷类型；
  `Option[Int]` 上的 `Some(v)` 把 `v` 绑定为 `Int`。递归载荷
  （`MyList[T]` 里的 `MyList[T]`）与嵌套构造器模式均支持。
- 空 enum、非顶层 enum、匹配非 enum、enum `==` 均显式拒绝。

### 内建 `Option` / `Result`

每个 `oort-core` 模块隐式拥有：

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

- 无需 import；`Some`/`None`/`Ok`/`Err` 是普通预置构造器，构造、match 与作值
  的规则同其他泛型 enum。
- `Option`/`Result` 类型名与四个构造器是**模块级保留名**；用户重定义类型、
  类、构造器或顶层绑定报 `... is declared in the core prelude.`。内层作用域
  可按普通遮蔽规则局部遮蔽（如函数内 `val Some = 1`）。
- 预置构造器不进入模块导出（`from "m" import Some` 失败）；每个模块各自获得
  预置声明。
- 预置类型使用固定名义 origin，因此模块 A 返回的 `Option[Int]` 与模块 B 的
  `Option[Int]` 是同一类型，可以跨模块传递与匹配。

## 显式拒绝

以下写法通过词法/语法分析，但在 `oort-core` 中报错：

| 类别 | 示例 | 诊断 |
|------|------|------|
| 类继承/元类/泛型类 | `class B < A`、`class C :: M`、`class C[T]` | 对应 "not supported" 诊断 |
| 类方法/运算符方法 | `def class.f`、类体内 `def operator` | `Only plain instance methods...` |
| 类体其他语句 | 类体中的 `print(1)` | `Only slot and method declarations...` |
| 槽未标注/重名 | `val x = 1`、重复成员 | `Slot ... requires a type annotation` / 重复诊断 |
| 未声明槽 | `this.y = 2`（未声明） | `Class 'C' has no slot 'y'.` |
| `val` 只读 | 方法内改 `val`、初始化器已赋值的 `val`、循环中赋值 | 只读槽诊断 |
| 确定赋值 | 分支漏赋值、赋值前读取、提前 return | `Constructor must initialize...` 等 |
| 类实例打印/相等 | `print(C())`、`c == c` | 不可打印 / `Class equality is not supported` |
| 扩展方法 | `def C.f` | `Extension methods...` |
| lambda/嵌套函数 | `do: 1`、函数体里的 `def` | `Lambdas...` / `Nested function definitions...` |
| null | `null` | `null is not supported...` |
| 切片 | `xs[1:2]`、`text[1:]` | `Slices are not supported...` |
| 属性 | `xs.length`、`a.b`（非模块/非类成员） | `Attribute access is only supported on imported modules...` |
| 空字面量 | 无标注的 `[]`、`{: :}`、`{. .}` | `Cannot infer ...; add a type annotation.` |
| 异构容器 | `[1, true]`、`{: 1: true :}` | `... have incompatible types` |
| 非法键类型 | `{. [1] .}`、`{: f: 1 :}` | `Set elements/Dict keys must be ... key types` |
| Tuple 动态异构下标 | `pair[i]`，`pair = (1, "a")` | `... require all elements to have the same type` |
| 集合跨类型相等/排序 | `[1] == (1,)`、`[1] < [2]` | 同类型相等；排序尚未支持 |
| 循环误用 | `for x in 1`、多变量、异构 Tuple、`break value` | 对应诊断 |
| 多目标/增强赋值 | `val a, b = ...`、`x += 1` | 对应诊断 |
| 默认值/关键字/变长 | `def f(x: Int = 1)`、`f(x = 1)`、`*args` | 对应诊断 |
| `**` | `2 ** -1` | 结果类型依赖指数，显式拒绝 |
| 位运算/`in`/`is` | `1 & 2`、`x in xs` | 运算符不支持 |
| 跨方言 import | core 导入 object 模块 | `Cannot import a 'oort-object' module...` |
| native import | `import "math"` | `Native modules are not supported...` |
| 类型参数上界/默认值 | `enum E[T: Int] { A }`、`enum E[T = Int] { A }` | `Type parameter bounds/defaults are not supported...` |
| 变型误用 | `enum E[out T] { A(f: (T) -> Int) }`、`enum E[in T] { A(v: T) }` | `Type parameter 'T' is declared covariant/contravariant ... but appears in a ... position ...` |
| 非法变型文本 | `enum E[foo T] { A }` | `Expected 'in' or 'out' before type parameter 'T', got 'foo'.` |
| 重定义预置 | `enum Option[T]`、`class Result`、`val Some = 1`、`enum Foo { Some(x: Int) }` | `Type/Constructor/Name ... is declared in the core prelude.` |
| 裸泛型类型 | `val x: MyOption = None` | `Type 'MyOption' requires 1 type argument(s); write MyOption[...].` |
| 单态 enum 加实参 | `Shape[Int]` | `Enum 'Shape' does not take type arguments.` |
| 泛型实参数目 | `MyOption[Int, String]` | `Type 'MyOption' expects 1 type argument(s), got 2.` |
| 无法推断类型实参 | `val x = None`、`val r = Ok(1)` | `Cannot infer type argument ...; add a type annotation.` |
| 类型实参冲突 | `Same(1, "s")`（`Same[T]` 的两个字段都是 `T`） | `Type parameter 'T' ... is inferred as both Int and String.` |
| 非顶层 enum | 函数/块内 `enum` | `Enum declarations are only allowed at module top level...` |
| 空 enum | `enum E { }` | `An enum must declare at least one constructor.` |
| match 不支持的类型 | `match [1] { _ => 1 }` | `The scrutinee of match must have an enum, Bool, Int, Float, String or Tuple type...` |
| 字面量类型不符 | `match f { 1 => ... }`（f 为 Float） | `Literal pattern of type Int cannot match Float.` |
| 元组模式误用 | `match 1 { (x, y) => ... }`、元组元数不符 | `Tuple patterns require a tuple type...` / `Tuple pattern has N element(s), expected M.` |
| 或模式绑定不一致 | `A(x) \| B(x, z)`、`A(x) \| B(x: String)` | `All alternatives ... same names` / `Binding 'x' has incompatible types...` |
| 非穷尽 | 缺少构造器 | `Match is not exhaustive; missing: ...` |
| enum 相等 | `A == A` | `Enum equality is not supported...` |
| 其他模式 | 字面量/元组/守卫/或模式 | 第一切片不支持（语法或诊断） |
| 匿名 lambda | `do: $0 + 1` | `Lambdas without an explicit parameter list...` |
| 泛型 lambda | `do[T](x: Int) -> Int ...` | `Generic functions are not implemented yet.` |
| 函数值打印/相等 | `print(f)`、`f == g` | 打印仅接受标量/ADT/集合；相等仅数值/Bool/String/同类型集合 |

类型错误使用 `TypeCheckError`，未实现构造使用 `UnsupportedSyntax`。

## 与 `oort-object` 的隔离

同一份源码在 object 下动态运行、在 core 下静态检查：

```oort
#lang oort-object
var x: Bool = 1   # 标注被忽略，运行时 x 是 Int
print(x)          # 1
```

把首行改为 `#lang oort-core` 后，同一个程序会报
`Expected Bool, got Int.`。core 模块之间可以互相导入；object 与 core
不能互相导入，跨方言调用需要未来的显式 FFI 边界。

## 执行与调试

- `-t vm`（默认）：检查后降低到 HIR/字节码，交寄存器 VM 执行（类型已擦除，见
  [spec 12](12-hir-bytecode-vm.md)）。
- `-t eval`：回退，检查后交树遍历解释器执行。
- `-t astm`：检查并打印 AST 元数据，包含 `type='Int'` 等推断结果。
- `-t ast`：只打印 AST，**跳过**语义分析与类型检查。

## 尚未实现

null、类继承与元类、泛型类/函数/lambda、匿名 $n lambda、跨方言 FFI、
REPL 方言切换、ADT 相等。
