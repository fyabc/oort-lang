# `oort-core` 薄探针

本页描述 `#lang oort-core` 当前**已实现**的最小静态子集。它不是完整的
`oort-core` v1；泛型、ADT/`match`、静态对象模型与跨方言 FFI 尚未实现。
设计取舍见 [OP 0017](../proposals/0017-oort-core-thin-probe.md)。

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
| `Bool` | 参数、变量、返回值、条件、逻辑运算 |
| `Unit` | **仅函数返回类型**；声明的内部类型，不是变量类型 |

- `Int` 与 `Bool` 严格区分，没有隐式转换或 truthiness。
- 静态 `Unit` 在运行时对应 `null`；`print` 返回 Unit。
- 内部还有函数类型、`Unknown`（错误恢复）与 `Never`（所有路径 `return`），
  但它们没有用户可写的标注语法。

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

- 只有顶层 `def`；不允许嵌套函数、lambda、方法、扩展或运算符定义。
- 每个参数与返回类型都必须标注；参数只支持普通位置参数。
- 返回值遵循 Oort 的运行语义：函数体最后一个表达式的值，或显式 `return`。
- 非 Unit 函数必须所有路径返回值，或函数体最后一个表达式的类型可赋给返回类型。
- 裸 `return` 只允许用于 `-> Unit` 函数。
- 顶层函数与变量按源码顺序可见；允许自递归，不支持前向引用或互递归。

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
| `1`、`true` | `Int`、`Bool` |
| `x` | 查词法作用域；未知名报错 |
| `+x`、`-x` | `Int -> Int` |
| `not x` | `Bool -> Bool` |
| `a + b`、`-`、`*`、`//`、`%` | `Int, Int -> Int` |
| `a < b`、`<=`、`>`、`>=` | `Int, Int -> Bool` |
| `a == b`、`!=` | 两个 Int 或两个 Bool -> Bool |
| `a and b`、`a or b` | `Bool, Bool -> Bool` |
| `f(...)` | 仅位置实参；精确元数；实参类型匹配 |
| `if c { ... } else { ... }` | 条件 Bool；两分支类型一致 |
| `{ ... }` | 块的值是最后一条语句的值；空块为 Unit |
| `print(...)` | 任意个 Int/Bool/Unit 实参 -> Unit；可被用户定义遮蔽 |

`if` 没有 `else` 时类型为 Unit。`Never`（例如 `return`）可与任一分支类型合并。

## 显式拒绝

以下写法通过词法/语法分析，但在 `oort-core` 中报错：

| 类别 | 示例 | 诊断 |
|------|------|------|
| 类/方法/扩展 | `class A {}`、`def C.f` | `Classes are not supported...` / `Extension methods...` |
| lambda/嵌套函数 | `do: 1`、函数体里的 `def` | `Lambdas...` / `Nested function definitions...` |
| 循环 | `while`、`for`、`break`、`continue` | `Loops are not supported...` |
| 集合/字符串/浮点/null | `[1]`、`"x"`、`1.5`、`null` | `Lists...`、`String...`、`Float...`、`null...` |
| 属性/下标 | `a.b`、`a[0]` | `Attribute access...` / `Subscripts...` |
| 多目标/增强赋值 | `val a, b = ...`、`x += 1` | 对应诊断 |
| 默认值/关键字/变长 | `def f(x: Int = 1)`、`f(x = 1)`、`*args` | 对应诊断 |
| `/`、`**` | `1 / 2`、`2 ** -1` | 会产生 Float，显式拒绝 |
| 位运算/`in`/`is` | `1 & 2`、`x in xs` | 运算符不支持 |
| 跨方言 import | core 导入 object 模块 | `Cannot import a 'oort-object' module...` |
| native import | `import "math"` | `Native modules are not supported...` |

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

- `-t eval`（默认）：检查后交给现有树遍历解释器执行。
- `-t astm`：检查并打印 AST 元数据，包含 `type='Int'` 等推断结果。
- `-t ast`：只打印 AST，**跳过**语义分析与类型检查。

## 尚未实现

Float/String/集合/null、`/`、循环、类与槽、ADT/`match`、泛型、函数值、
跨方言 FFI、REPL 方言切换、静态对象模型、确定赋值、穷尽性检查、
HIR/字节码后端。
