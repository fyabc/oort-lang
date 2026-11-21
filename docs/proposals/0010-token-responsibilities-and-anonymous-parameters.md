# OP 0010: Token 职责与匿名 lambda 参数

- **状态**：Implemented
- **作者**：Oort 设计讨论
- **相关**：[OP 0002](0002-dsl-support.md)、[OP 0005](0005-type-system.md)、
  [OP 0009](0009-expression-and-surface-cleanup.md)、
  [规范：函数](../spec/04-functions.md)

## 摘要

明确 `:`、`=`、`->`、`=>` 四个 token 的职责，避免未来方言、命名实参、按名参数
与模式匹配各自临时解释这些符号。同时实现小型 lambda 的极简写法：
`do: $0 * 2`、`do: $0 + $1`。

## Token 职责

| Token | 一句话直觉 | 当前用途 | 预留用途 | 不用于 |
|---|---|---|---|---|
| `:` | **是什么 / 头部: 内容** | 类型标注 `x: Int`、上界 `T: Bound`、字典键值、切片、`if/def/class` 体 | 记录字段 | 赋值、默认值、返回类型 |
| `=` | **把名字绑到值** | 声明、赋值、默认参数、命名实参 | 槽初始化、解构默认值 | 函数体 |
| `->` | **类型层面的返回** | 返回类型 `-> T` | 函数类型 `(A, B) -> C`、方法签名、FFI | 表达式体、match 分支、命名参数 |
| `=>` | **延迟 / 映射** | 当前未使用 | 按名参数 `x: => T`、match 分支 `pat => expr`、宏规则 `pat => expansion` | 普通函数体、赋值、默认值 |

`::` 仍只用于元类与切片步长，不参与这四个 token 的职责划分。

### 为什么不是 `=` 函数体

`=` 同时承担声明、赋值、默认参数和命名实参。用 `=` 表示函数体会重新制造
“`def f x = 1` 是默认值还是函数体”的歧义；因此函数/lambda 的表达式体继续用
`:`，与 `if cond: expr` 的“头部: 内容”保持一致。

### 命名实参

命名实参继续使用 `=`：

```oort
f(x = 1, y = 2)
```

这与 Python/Kotlin/Scala 的直觉一致，也让 `=` 保持“把名字绑到值”的单一含义。
Swift 风格 `f(x: 1)` 是备选，但会与类型标注的视觉习惯冲突。

### `=>` 的预留

- 声明按名参数：`def unless(cond: => Bool, body: => Unit)`；
- 模式匹配：`match x { Some(v) => v, None => 0 }`；
- 宏规则：`pattern => expansion`。

调用处的按名参数不需要额外的 `=>`：实参仍是普通表达式，由被调方的
`=>` 参数决定是否包装成 thunk。

> 2026-11-21：`=>` 已作为独立 `FATARROW` token 用于 `oort-core` 的
> `match` 分支；按名参数与宏规则仍未实现。

## 匿名参数

### 语法

```oort
val double = do: $0 * 2
val add = do: $0 + $1
val inc = do { $0 + 1 }
apply(do: $0 * 2)
```

- `$0`、`$1`……是匿名参数，从 0 开始编号。
- 参数个数由最大下标推断：`do: $1` 接受两个参数，`$0` 也会被绑定（即使未使用）。
- 匿名参数只允许出现在**没有显式参数列表**的 lambda 中：
  - `do: ...`、`do { ... }` 允许；
  - `do(): ...` 是显式空参数列表，不允许匿名参数；
  - `do(x): ...` 不允许与匿名参数混用。
- 匿名参数只在最近的 lambda 内可见；嵌套 lambda 的 `$n` 绑定各自作用域。
- 匿名参数不能声明类型或默认值；需要这些时写 `do(x: Int): ...`。
- `$n` 不能作为普通变量、参数、函数名或类名声明。
- `def`/方法中不能使用匿名参数；它们只属于小型 lambda。

### 错误诊断

| 写法 | 诊断 |
|---|---|
| `def f { $0 }` | Anonymous parameters are only allowed in lambdas. |
| `do(x): $0` | Anonymous parameters cannot be combined with an explicit parameter list. |
| `do(): $0` | 同上（显式空参数列表） |
| `$0` | Anonymous parameters are only allowed inside a lambda. |
| `var $0 = 1` / `def f($0): $0` | Anonymous parameter names cannot be declared explicitly. |

### 实现

- `ASTBuilder` 在构建 lambda 时扫描 body 中的 `$n`，跳过嵌套函数/类，
  计算 `anonymous_count = max(index) + 1`。
- `FunctionDef` 记录 `anonymous_count` 与 `has_explicit_param_list`；
  `param_count` 用于 arity。
- `Pass1Analyzer` 在函数作用域中合成 `$0..$n` 绑定，并拒绝显式声明 `$n`。
- `OortFunction` / `OortMethod` 调用时把实参绑定到 `$i`。

不修改 ANTLR 文法：`AnonymousParameter` token 已经存在。

## 未来兼容

- 字符串插值若使用 `"$name"` / `"${expr}"`，与 `$0`/`$1` 的数字形式可以共存；
  具体插值语法见 OP 0002 后续实现。
- `oort-core` 可静态检查匿名参数的 arity；动态方言已在运行时检查。
- 如果未来需要 `=>` 函数体，必须先重新审视“按名参数/match/宏规则”的分配；
  当前不采用。

## 测试

- `tests/unit/runtime/test_anonymous_params.py`：一元/二元/块体/尾随 lambda、
  下标推断、嵌套作用域、arity 错误与全部拒绝诊断。

## 未解决问题

- 是否允许 `$0` 出现在 lambda 的返回类型或默认值中？（当前拒绝）
- 是否允许用户显式声明 `$0` 作为普通名字？（当前拒绝）
- 匿名参数与未来字符串插值的 `$` 语法如何在同一词法空间内展示给用户？
