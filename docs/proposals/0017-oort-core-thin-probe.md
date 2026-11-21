# OP 0017: `oort-core` 薄探针

- **状态**：Implemented
- **日期**：2026-11-20
- **相关**：[OP 0001](0001-feature-layers-and-dialects.md)、[OP 0005](0005-type-system.md)、[规范 11](../spec/11-core-probe.md)

## 摘要

在完整 `oort-core` v1 之前，先用一个**薄探针**验证方言路由与语义隔离：

- `#lang oort-core`；
- 最小静态子集：`Int`、`Float`、`Bool`、`String`、`Unit`、集合与循环、静态类/槽、函数、单态 ADT 与 `match`；
- 独立类型检查器，复用 AST、诊断、模块加载、CLI 与测试框架；
- 同一份源码在 `oort-object` 下动态运行、在 `oort-core` 下静态检查。

探针不是 OP 0005 的完整实现：泛型 ADT、`Option[T]`/`Result[T,E]`、
静态对象模型、跨方言 FFI 都留给后续。

## 跨语言调研

| 语言/系统 | 模块级切换 | 边界机制 | 保证/代价 |
|---|---|---|---|
| Racket | `#lang racket` / `typed/racket` | `require/typed` 生成 contract、blame | 运行时健全；contract 与代理有性能成本 |
| TypeScript | `allowJs`、`checkJs`、`// @ts-check` | 基本擦除，无运行时检查 | 静态检查为主；跨边界弱保证 |
| Kotlin | — | `Unit` 单例类型；`println` 返回 `Unit` | 适合建模“有副作用、无值”的表达式 |
| Rust | — | `()` 单元类型；`println!` 返回 `()` | 同上 |
| Python / Rust / Go | — | `//` 向下取整 vs `/` 真除法或截断 | Oort 沿用 Python：`//` 取整、`/` 返回 Float |

结论：

1. **模块级方言**是成熟做法。Oort 的 `#lang` 与 Racket 的模块粒度一致。
2. **边界不能假装**。Racket 用 contract 做健全边界，TypeScript 接受擦除后的
   弱保证；Oort 探针选择第三条路：**显式拒绝跨方言导入**，等 OP 0005 的
   trampoline/blame 落地。
3. **双向检查的局部版本**足够：签名必须标注，局部变量可推断，不做 HM。
   Pierce & Turner 的 local type inference 与 Dunfield & Krishnaswami 的
   bidirectional typing 综述都支持这一取舍。
4. **Unit 建模 `print`**：Kotlin/Rust 的先例表明返回 Unit 比返回 `null` 更清晰。
   Oort 运行时把静态 `Unit` 映射到 `null`。
5. **整数除法**用 `//` 保持 Int；`/` 固定返回 Float，探针直接支持 Float
   后放开。`**` 在负指数时也可能返回 Float，仍显式拒绝。

来源：

- <https://docs.racket-lang.org/guide/more-hash-lang.html>
- <https://dl.acm.org/doi/fullHtml/10.1145/3579833>
- <https://www.typescriptlang.org/tsconfig/allowJs.html>
- <https://dl.acm.org/doi/10.1145/3450952>
- <https://github.com/Compile-N-Run/Compile-N-Run/blob/main/docs/language/kotlin/2-kotlin-functions/5-kotlin-unit-return-type.mdx>
- <https://users.rust-lang.org/t/why-calling-macro-println-returns-no-value/28469/6>

## 接受的子集

### 类型

- `Int`、`Float`、`Bool`、`String`、单态 `enum` 与类类型；
- `List[T]`、`Set[T]`、`Dict[K, V]`、`Tuple[T1, ...]`；可嵌套；
- `Unit`：仅允许作为函数返回类型；
- 数值标注不做隐式转换：`val x: Float = 1` 报错，必须写 `1.0`；
- 类类型：顶层的 `class`；名义相等；
- 函数类型：`Int -> Bool`、`(Int, Bool) -> Int`、`() -> Unit`；
- 内部 `FunctionType`、`ModuleType`、`AdtType`、`ClassType`、`Unknown`（错误恢复）、
  `Never`（所有路径 `return`）。

### 声明与语句

- 顶层与函数内 `val`/`var`，单目标；标注或从初始化器局部推断。
- 赋值只允许 `=` 到 `var`；`val`、参数、函数不可变。
- 顶层 `def`：参数与返回必须标注；允许自递归；按源码顺序可见。
- 显式参数列表的 `do(...)` lambda：参数/返回必须标注；函数值可推断、赋值、
  传参、返回与调用。函数类型箭头右结合；不做自动柯里化，链式调用
  `f(1)(2)` 由手动返回 lambda 支持。
- 顶层 `enum`：单态、非空；构造器与字段；字段类型为 Int/Float/Bool/String/本地 enum。
- 顶层 `class`：固定 `val`/`var` 槽（标注）、方法、`__init__`；无继承/元类/
  类方法/运算符方法。槽初始化器在构造时、`__init__` 前按声明顺序求值。
- 构造器确定赋值：无初始化器的槽必须在 `__init__` 所有落空路径赋值；
  赋值前读取、提前 return、分支遗漏均报错；`val` 只读且最多赋值一次。
- 函数体、块、`if`/`else`、`match`、表达式语句、`return`。
- `while` 条件必须 Bool；`for` 遍历 List/Set/Dict 键/String/同质 Tuple；
  循环变量单目标、不可变；`break`/`continue` 仅循环内，`break value` 拒绝。
- `if` 条件必须是 Bool；无 `else` 时类型为 Unit；分支类型需一致
  （`Never` 可与任一类型合并）。
- 非 Unit 函数必须所有路径返回值，或函数体最后一个表达式的类型可赋给返回类型。

### 表达式

- Int/Float/Bool/String 字面量、名字、块、`if`/`else`、调用（仅位置实参、精确元数）。
- List/Tuple/Dict/Set 字面量：同质 List/Set/Dict 推断，Tuple 可异构；
  空字面量需要期望类型；`xs[i]` 下标、`len(x)`；同类型集合相等。
- `do(x: Int) -> Int { ... }` 函数值；函数值可作为被调者/实参/返回值。
- 一元 `+`、`-`、`not`。
- 二元 `+ - * // %`（Int/Float 混合，任一为 Float 则结果 Float）、
  `/`（固定 Float）、`< <= > >=`（数值或 String）、`== !=`（数值、Bool 或
  String）、`and`、`or`。
- `this`、`obj.slot`、`obj.method`、`this.slot = value`、构造器 `C(...)`；
  类实例不可打印或比较。
- `print`：未被用户遮蔽时，接受任意个 Int/Float/Bool/String/Unit/enum/集合参数，
  返回 Unit；函数值与类实例不可打印。

### ADT 与 `match`

- 单态 `enum Name { Variant(field: Type, ...) Variant }`，仅模块顶层；
  字段类型为 Int/Bool/本地 enum，支持自递归。
- 构造器进入值命名空间；零参构造器是值，有参构造器是可调用值。
- `match` 的 scrutinee 必须是 enum；arm 用 `,` 或换行分隔。
- 模式：`_`、绑定名、构造器模式（可嵌套）；裸零参构造器名同时限定 variant
  并绑定该名字。
- arm 独立作用域、implicit join；顶层构造器穷尽性；嵌套穷尽性暂不做。
- `print` 接受 enum 值；`enum ==` 显式拒绝。

### 显式拒绝

类继承/元类/泛型类/类方法/运算符方法、扩展方法、`super`、匿名/泛型/默认值
lambda、嵌套/泛型/运算符定义、`yield`/`await`、宏、编译器属性、Null、切片、
非模块/非类属性、多目标声明与循环解包、下标赋值、增强赋值、`**`、位运算、`in`、
`is`、默认值、关键字实参、变长参数、`&block`、未声明槽、非法槽赋值；
跨方言与 native 模块导入；泛型 ADT、字面量/元组/守卫/或模式、嵌套穷尽性。

拒绝时使用带位置的 `UnsupportedSyntax` 或 `TypeCheckError`，不静默降级。

## 方言隔离

- 每个模块独立解析 `#lang`。
- core 模块可以导入其他 core 模块：`import "m"` 绑定模块命名空间，
  `from "m" import f` 绑定导出名。模块导出顶层函数、变量、构造器与再导出的
  导入名；导入名不可变，模块命名空间属性不可写。enum 类型名只进入类型
  命名空间，暂不支持跨模块类型注解；函数签名可携带 `AdtType`。
- 静态检查器通过编译器注入的 resolver 递归编译目标模块，取得导出类型，
  并缓存 `CompiledUnit`；编译期循环导入显式报错。
- `ModuleLoader` 在编译后比较目标模块与导入方方言；object↔core 双向导入
  仍被拒绝，跨方言调用等待 OP 0005 的 FFI trampoline/blame。
- native 模块（`math` 等）不能从 core 导入。
- REPL 固定为 `oort-object`；输入 `#lang` 指令时报错，不静默按 object 执行。
- `-t ast` 跳过语义分析；`-t astm` 与 `eval` 运行检查器。

## 实现

- `parser/dialect.py`：`DialectFeatures.type_checking`，`OORT_CORE.implemented=True`。
- `semantics/analyzer.py`：`create_semantic_analyzer()` 按方言返回
  `Pass1Analyzer` 或 `CoreAnalyzer`（Pass1 + `CoreTypeChecker`）。
- `semantics/core/{types,checker}.py`：独立类型模型与检查器；只依赖
  `ast`/`diagnostics`/`parser`/`source`。`ModuleType` 表示模块命名空间，
  `AdtType` 表示名义 ADT，`ClassType` 表示固定槽类；检查器负责构造器、模式、
  顶层穷尽性与类成员。
- `semantics/core/definite_assignment.py`：构造器 (definite, maybe) 确定赋值分析。
- `runtime/type_system.py` + `interpreter.py`：槽定义/初始化、`val` 只读与缺失槽
  运行时兜底。
- `driver/compiler.py`：`CompiledUnit` 缓存 AST、方言与导出类型；
  `_resolve_core_module` 递归编译 core 导入并检测循环。
- `runtime/modules.py`：`CompiledModule` 携带方言名；导入时做方言比较。
- `diagnostics/type_errors.py`：`TypeCheckError`。
- 推断类型写入 `node.metadata["type"]`，供 `-t astm` 展示。

## 未决/后续

- 函数返回类型推断（签名仍必须显式标注）；更强的 expected-type 传播。
- null、类继承/元类、泛型 ADT/HKT、`Option[T]`/`Result[T,E]`。
- 集合切片/原地修改、`in`、排序、惰性视图。
- 字面量/元组/列表/守卫/或模式、嵌套穷尽性、ADT 相等与迭代。
- 跨方言 FFI trampoline/blame；更完整的模块接口版本管理与增量编译。
- REPL 方言切换与持久方言状态。
- 继承/接口、属性访问器与槽的跨方言边界。
- HIR 与字节码后端。
