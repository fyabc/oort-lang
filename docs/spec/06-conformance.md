# 实现状态与诊断

Oort 的语法前端接受一个**语言超集**；运行时只实现其中的核心动态子集。
本页是二者之间的一致性矩阵。

实现原则：**未实现的功能必须显式报错**，不能静默产生错误结果。
`Pass1Analyzer` 负责共享的名称/作用域/未实现特性检查；`oort-core` 还由
`CoreTypeChecker` 拒绝静态子集之外的构造。

## 已实现

| 类别 | 特性 |
|------|------|
| 方言 | 首行 `#lang oort-object`（可选，缺省即此方言）与 `#lang oort-core` 薄探针；未知/未实现方言与错位声明显式报错 |
| 字面量 | 整数、浮点、字符串（含 `r`、三引号）、布尔、`null`、List/Tuple/Dict/Set、切片 |
| 表达式 | 全部内建运算符、运算符重载（`def operator "<sym>"`）、位运算高于比较、比较非结合、`Bool` 与 `Int` 严格区分（含嵌套容器）、容器递归值相等、Dict/Set 键相等、List/Tuple 字典序与 Set 子集比较（Dict 无排序）、`and`/`or` 短路、属性、下标、调用、尾随 lambda、块、`if`/`while`/`for` 表达式、行首 `.` 方法链续行 |
| 语句 | `var`/`val`（含多目标解包）、赋值（含 `//=` 等增强赋值、元组交换）、`if`/`elif`/`else`、`while`、`for`、`return`、`break expr`、`continue` |
| 函数 | `def`、`do` lambda、闭包、递归、尾随闭包；所有显式形参列表都使用括号；lambda 支持 `$0`/`$1` 匿名参数；默认值、关键字实参、`/`、`*`、`*args`、`**kwargs`、`&block` |
| 类 | 定义、实例化、`__init__`、方法、类方法、单/多重继承、C3 MRO、元类、`this`/`super`；开放字段袋、方法遮蔽检查、身份键哈希 |
| 扩展 | 类外 `def C.f` 与 `def C.operator "<sym>"`；词法作用域、导入激活、调用点歧义、继承与 `super`（只查类成员） |
| 迭代 | `__iter__` 返回 `(value, valid)` 迭代器；流式 `for`；内置 List/Tuple/Set/Dict/String 的原生 `__iter__`，`Iterator` 类型与手动迭代 |
| 模块 | `.ort` 文件模块；`import "m" [as x]`、`from "m" import a, b as c`；相对/裸名解析、`-I` 搜索路径、规范路径缓存、急切初始化与循环诊断；模块命名空间只读、导入名可再导出；`io` / `math` / `os` / `string` 内置原生模块 |
| 内建 | `print`、`clock`、`type`、`len`、`range`、`str`、`repr`、`int`、`float`、`bool`；集合助手 `map`、`filter`、`zip`、`enumerate`、`sorted` |
| 标准库 | 原生模块 `io`（UTF-8 整文件读写）、`math`（常量/数学函数）、`os`（参数、脚本路径、退出码）与 `string`（切分/连接/大小写/查找/替换/`ord`/`chr`）；裸名优先于同名文件，`./math` 等可加载本地模块 |

## 可解析但被拒绝

以下写法能通过词法/语法分析，但语义分析会显式报错
（`UnsupportedSyntax` 或对应语法诊断）：

| 特性 | 示例 | 诊断信息 |
|------|------|----------|
| 宏系统 | `macro m {}`、`@m(1)` | The macro system is not implemented yet. |
| 生成器 | `yield expr` | Generators (`yield`) are not implemented yet. |
| 异步 | `await expr` | Async/await is not implemented yet. |
| 泛型函数/类 | `def f[T](a)`、`class C[T]` | Generic functions/classes are not implemented yet. |
| 泛型 enum | `enum E[T] { A }` | Generic enums are not supported in oort-core yet. |
| 非 core 的 enum/match | `oort-object` 中的 `enum` / `match` | Enums are only supported in oort-core yet. / match is only supported in oort-core yet. |
| 编译器属性 | `@[]` | Compiler attributes are not implemented yet. |
| 格式化字符串 | `f"..."` | Formatted string literals are not implemented yet. |
| 字典展开 | `{: **d :}` | Dictionary unpacking is not supported yet. |
| 多级接收者 | `def A.B.f ...` | Extension methods must name exactly one receiver type ('def C.f'). |
| 类体内的扩展 | `class C { def C.f ... }` | Cannot define extension method in class scope. |
| 扩展特殊方法 | `def C.__init__ ...` | Extension methods cannot define special method `__init__`. |
| 类方法定义位置 | `def class.f ...`（类外） | Class methods must be defined inside a class. |
| 命名空间类 | `class A.B {}` | Namespaced classes are not implemented yet. |
| 显式 `super` 调用 | `super(1)`、`super(A, this)` | Explicit super(...) calls are not supported |
| 隐式中缀 | `a b c` | Infix call 'b' is not supported yet |
| 裸形参 | `def f x: ...`、`do x: ...` | 语法错误（形参必须加括号） |
| 比较链 | `0 <= i < n` | Comparison operators cannot be chained |

`super.__init__(args)` 与 `super.method` 仍然可用。

## 解析但被忽略（仅 `oort-object`）

- **类型标注**（`val x: Int`、`-> Int`、形参类型）会被解析和保存到 AST，
  但动态解释器不检查、不强制。完整类型系统见
  [proposal 0005](../proposals/0005-type-system.md)。
- 在 `oort-core` 薄探针中，`Int`/`Float`/`Bool`/`String`/`Unit`、单态 enum 与函数类型标注
  会被独立检查器检查；见 [11-core-probe.md](11-core-probe.md)。

## `oort-core` 薄探针

| 类别 | 已实现 |
|------|--------|
| 类型 | `Int`、`Float`、`Bool`、`String`、`Unit`（仅函数返回）、单态 `enum`；内部函数/`Unknown`/`Never` |
| 声明 | 单目标 `val`/`var`，标注或局部推断；`var` 可赋值；模块顶层 `enum` |
| 函数 | 顶层 `def`、标注必填、位置参数、自递归、所有路径返回；函数类型、lambda 与函数值 |
| 表达式 | 字面量、名字、块、`if`/`else`、调用、Int/Float 算术与 `/`、数值/String 比较、Bool 逻辑、`match`、lambda、`print` |
| ADT | 单态 `enum`、构造器、嵌套构造器模式、`_`/绑定、顶层构造器穷尽性 |
| 模块 | core→core `import` / `from`、导出类型与再导出；object↔core 与 native 导入被拒绝 |
| 调试 | `-t ast` 跳过检查；`-t astm` 显示推断类型 |

不在子集中的构造会以带位置的 `UnsupportedSyntax` 或 `TypeCheckError` 拒绝；
完整清单见 [11-core-probe.md](11-core-probe.md)。

## 语法之外的限制

- 用户自定义运算符符号（由 `! % & * + - / < = > ? ^ | ~` 组成）可以定义方法并调度，
  但其**优先级**仍为默认值（中缀 500、左结合）；按作用域声明优先级属于
  [OP 0002](../proposals/0002-dsl-support.md) 的后续工作。
- 类内运算符方法只能在类体内定义；顶层裸 `def operator ...` 与
  `def class.operator` 会被拒绝。扩展运算符使用
  `def C.operator "<sym>"`（[扩展方法](10-extensions.md)）。
- 扩展方法的接收者必须是单个已定义的类标识符；多级接收者、类体内的扩展与
  特殊方法名（`__init__` 等）会被拒绝。
- 下标（`a[b]`）与属性（`a.b`）重载尚未接入运算符调度。
- 类体中的 `var`/`val` 在 `oort-object` 中被显式拒绝；实例字段只能通过
  `this.x = ...` 创建（[OP 0007](../proposals/0007-oort-object-object-model.md)）。
  槽变量属于 `oort-core`。
- 实例字段不能遮蔽实例方法或类方法；写入时报
  `Cannot shadow method 'name' with an instance field`。
- 用户类默认值相等与键哈希使用对象身份；自定义 `==` 只影响值相等，
  不改变 Dict/Set 键身份（[OP 0016](../proposals/0016-equality-protocol.md)）。
- Int 与 Float 值相等但键不同：`1 == 1.0`，`{. 1 .} != {. 1.0 .}`。
- 缺失字段读取抛 `OortAttributeError`；类对象写入可调用成员会被拒绝。
- 匿名参数 `$0` / `$1` 只允许出现在无显式参数列表的 lambda 中；
  `def`、`do()`、`do(x)` 以及显式声明 `$n` 都会报错。
- 模块系统（OP 0006）：
  - `import` 只允许在模块顶层；函数、块、类体中的 import 报
    `Imports are only allowed at module top level.`。
  - 顶层 import 会提升到模块正文之前执行；模块只初始化一次并按规范路径缓存。
  - 首版禁止循环导入；目录包、OS 绝对路径、宿主语言模块与 `import lazy`
    均未实现。详见 [07-modules.md](07-modules.md)。
- 参数绑定（OP 0011）：
  - 默认值每次调用求值，只能引用更早的参数；不能引用 `this` 或更晚参数。
  - `*args` 是 Tuple，`**kwargs` 是 String 键 Dict。
  - 位置限定名的关键字可被 `**kwargs` 捕获；没有 `**kwargs` 时报错。
  - `&block` 可由尾随块或 `block = ...` 提供，缺省为 `null`。
  - 原生内建函数只接受位置实参。

## 已知的实现约定

- 语句之间必须有换行或 `;`；同一行写多条语句时必须用 `;`；
  行首 `.` 续行是这一规则的例外（见词法换行规则）。
- `: expression` 形式的函数/分支体必须与冒号在同一行。
- `for` 的循环变量按迭代独立绑定。
- `print` 使用对象的 `__str__`：字符串不带引号；List/Tuple 使用 `[...]` / `(...)`，
  Dict/Set 使用 `{: ... :}` / `{. ... .}`；`repr` 使用 Oort 字面量形式。

## 测试对应关系

- 单元测试：`tests/unit/frontend/`（词法、解析、AST、语义、诊断、错误配对）、
  `tests/unit/runtime/`（解释器、类、函数、容器、内建、匿名参数、参数绑定、
  模块解析与加载）。
- 集成测试：`tests/integration/`（CLI、REPL、全部示例程序）。
- 每个已实现特性至少有一个测试；拒绝清单由 `test_unsupported.py` 参数化覆盖。
- 模块系统由 `tests/unit/runtime/test_module_resolution.py`、
  `test_modules.py`、`tests/unit/frontend/test_imports.py` 与
  `tests/integration/test_cli.py`、`test_repl.py` 覆盖。
- 标准库由 `tests/unit/runtime/test_collection_builtins.py`、
  `test_math_string_modules.py`、`test_native_modules.py`、
  `test_host_boundary.py` 与 `examples/05_stdlib/` 覆盖。
- 迭代协议由 `tests/unit/runtime/test_iterators.py`、`test_control_flow.py`
  与 `examples/06_iterators/` 覆盖。
- `oort-core` 薄探针由 `tests/unit/frontend/test_core_checker.py`、
  `test_core_types.py`、`test_analyzer_dispatch.py`、
  `tests/unit/runtime/test_core_execution.py`、`test_core_modules.py`、
  `test_core_adt_execution.py`、`test_core_function_values.py` 与
  `examples/08_core/` 覆盖。
