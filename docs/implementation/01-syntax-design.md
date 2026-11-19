# 语法设计

本文记录 Oort 语法层面的设计取舍。语言参考见 [spec](../spec/index.md)。

## 基本语法

- 变量声明：采用后置类型声明，允许省略类型声明（通过初始值推断），禁止未初始化的变量。
  - `var` 声明可变变量，`val` 声明只读变量，后者优先使用。
  - 支持多目标声明与解包：`var a, b = 1, 2`、`var a, b = [3, 4]`。
- 类型标注在 `oort-object` 中只被解析、不参与检查；`oort-core` 薄探针会检查
  其中的 `Int`/`Bool`/`Unit` 子集。完整类型系统见
  [提案 0005](../proposals/0005-type-system.md)。

```oort
var a = 1
val b: Int = 2
var a, b = 1, 2
```

### 字面量

- 整数：十进制、`0b`、`0o`、`0x`，以及 `0d42` 形式的显式十进制。
- 浮点：`1.5`、`2e3`、`1.5e-2`。
- 字符串：单/双引号、三引号多行、`r` 原始字符串。
  - 格式化字符串（`f"..."`）**尚未实现**，会显式报错——避免用 Python `eval`
    在解析期执行任意代码。
- 布尔：`true`、`false`；空值：`null`。

- 列表：`[1, 2, 3]`（可变 `List[T]`）
- 元组：`(1, "Oort", true)`（不可变 `Tuple[...]`；单元素写作 `(1,)`）
- 字典：`{: "a": 1 :}`；空字典 `{:}`
- 集合：`{. 1, 2 .}`；空集合 `{.}`

用 `{: :}` / `{. .}` 而不是 `{}`，是为了在词法层把**数据字面量**与**代码块**
区分开，避免 Python/JavaScript 中 `{}` 的二义性。

### 注释与换行

- `#` 到行尾为注释。
- 语句以换行或 `;` 分隔，末尾不需要分号。
- 若位于 `()`、`[]`、`{: :}`、`{. .}` 内（且最内层不是 `{}`），换行被忽略，
  长表达式可直接换行；否则可用行尾 `\` 续行。

## 表达式

- 运算符优先级与结合性由 Pratt 解析器统一处理，见
  [spec: 表达式](../spec/02-expressions.md#运算符) 与
  `src/oort_lang/parser/operator_defs.py`。
- 用户自定义运算符在词法/语法层受支持（`USER_OP`），运行时通过
  `def operator "<sym>"` 方法调度；未定义方法的类型会在运行期报错。
  运算符优先级声明仍待实现，设计见
  [proposal 0002](../proposals/0002-dsl-support.md)。
- 函数调用（`f(x)`）、下标（`a[b]`）、属性（`a.b`）的优先级高于所有 Pratt 运算符。
- 赋值是**语句**，不是表达式：
  - 关键字实参沿用 `f(x=1)` 语法；若赋值也是表达式会产生歧义；
  - 赋值作为表达式价值很低，因此排除。

## 函数

```oort
def addInt(a: Int, b: Int) -> Int {
  a + b
}

def subInt(a: Int, b: Int): a - b

def doubleInt(a: Int): a * 2
```

- 所有形参列表都必须使用括号；裸形参形式已移除，避免 `:` 在类型标注与
  函数体之间的歧义。
- 函数体最后一条语句的值即返回值（除非用 `return` 提前返回）。
- 返回类型用 `->`；`oort-object` 中仅作标注，`oort-core` 薄探针中会检查。
- 支持默认值、关键字实参、`/`、`*`、`*args`、`**kwargs` 与 `&block`
  （[OP 0011](../proposals/0011-parameter-binding.md)）。
- 匿名函数用 `do` 引导：

```oort
val add = do(a, b) { a + b }
val inc = do(x): x + 1
```

- 不使用 `{}` 直接引导 lambda：`if` / `class` / `def` 的代码块也会用 `{}`，
  省略 `do` 会造成解析歧义。`do` 与 Ruby 的 `do ... end` 长度相同。
- 尾随闭包：仅当 lambda 是最后一个实参时可省略括号：

```oort
repeat do { print("Hello") }
val doubled = map(ints) do(i): i * 2
```

- `$0`、`$1` 匿名形参只用于无显式参数列表的 lambda：
  `do: $0 * 2`、`do: $0 + $1`（见 [OP 0010](../proposals/0010-token-responsibilities-and-anonymous-parameters.md)）。

## 函数式与对象式的边界

- 函数是一等值，可放入容器、作为参数与返回值。
- 类系统采用 Smalltalk/Python 风格（元类、多重继承、C3 MRO），详见
  [04-class-system.md](04-class-system.md)。
- 目前**没有**结构体、Trait、ADT、模式匹配；这些是
  [proposal 0005](../proposals/0005-type-system.md) 的内容。
- 语言“方言”（oort-core / oort-object / oort-systems）与模块级隔离是
  [proposal 0001](../proposals/0001-feature-layers-and-dialects.md) 的方向，
  当前实现只对应其中的动态/对象方言。

## 命名风格

- 类名：大驼峰；函数、变量、值：蛇形命名，首字母小写（与 Python 一致）。
