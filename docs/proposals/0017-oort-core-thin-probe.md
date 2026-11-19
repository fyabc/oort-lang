# OP 0017: `oort-core` 薄探针

- **状态**：Implemented
- **日期**：2026-11-20
- **相关**：[OP 0001](0001-feature-layers-and-dialects.md)、[OP 0005](0005-type-system.md)、[规范 11](../spec/11-core-probe.md)

## 摘要

在完整 `oort-core` v1 之前，先用一个**薄探针**验证方言路由与语义隔离：

- `#lang oort-core`；
- 最小静态子集：`Int`、`Bool`、`Unit`、函数；
- 独立类型检查器，复用 AST、诊断、模块加载、CLI 与测试框架；
- 同一份源码在 `oort-object` 下动态运行、在 `oort-core` 下静态检查。

探针不是 OP 0005 的完整实现：泛型、ADT/`match`、静态对象模型、跨方言 FFI
都留给后续。

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
5. **整数除法**只用 `//`：`/` 在 Oort 中返回 Float，`**` 在负指数时也可能
   返回 Float，探针都显式拒绝。

来源：

- <https://docs.racket-lang.org/guide/more-hash-lang.html>
- <https://dl.acm.org/doi/fullHtml/10.1145/3579833>
- <https://www.typescriptlang.org/tsconfig/allowJs.html>
- <https://dl.acm.org/doi/10.1145/3450952>
- <https://github.com/Compile-N-Run/Compile-N-Run/blob/main/docs/language/kotlin/2-kotlin-functions/5-kotlin-unit-return-type.mdx>
- <https://users.rust-lang.org/t/why-calling-macro-println-returns-no-value/28469/6>

## 接受的子集

### 类型

- `Int`、`Bool`；
- `Unit`：仅允许作为函数返回类型；
- 内部 `FunctionType`、`Unknown`（错误恢复）、`Never`（所有路径 `return`）。

### 声明与语句

- 顶层与函数内 `val`/`var`，单目标；标注或从初始化器局部推断。
- 赋值只允许 `=` 到 `var`；`val`、参数、函数不可变。
- 顶层 `def`：参数与返回必须标注；允许自递归；按源码顺序可见。
- 函数体、块、`if`/`else`、表达式语句、`return`。
- `if` 条件必须是 Bool；无 `else` 时类型为 Unit；分支类型需一致
  （`Never` 可与任一类型合并）。
- 非 Unit 函数必须所有路径返回值，或函数体最后一个表达式的类型可赋给返回类型。

### 表达式

- Int/Bool 字面量、名字、块、`if`/`else`、调用（仅位置实参、精确元数）。
- 一元 `+`、`-`、`not`。
- 二元 `+ - * // %`、`< <= > >=`、`== !=`、`and`、`or`。
- `print`：未被用户遮蔽时，接受任意个 Int/Bool/Unit 参数，返回 Unit。

### 显式拒绝

类、方法、扩展、`this`/`super`、lambda、嵌套/泛型/运算符定义、循环、
`break`/`continue`、`yield`/`await`、宏、编译器属性、Float/String/Null/
集合字面量、属性/下标、多目标声明、增强赋值、`/`、`**`、位运算、`in`、
`is`、默认值、关键字实参、变长参数、`&block`、import。

拒绝时使用带位置的 `UnsupportedSyntax` 或 `TypeCheckError`，不静默降级。

## 方言隔离

- 每个模块独立解析 `#lang`。
- `oort-core` 暂不支持 import；出现 import 直接报错。
- `ModuleLoader` 在编译后比较目标模块与导入方方言；不同则拒绝并提示需要
  显式 FFI 边界。因此 object↔core 双向导入都被拒绝。
- REPL 固定为 `oort-object`；输入 `#lang` 指令时报错，不静默按 object 执行。
- `-t ast` 跳过语义分析；`-t astm` 与 `eval` 运行检查器。

## 实现

- `parser/dialect.py`：`DialectFeatures.type_checking`，`OORT_CORE.implemented=True`。
- `semantics/analyzer.py`：`create_semantic_analyzer()` 按方言返回
  `Pass1Analyzer` 或 `CoreAnalyzer`（Pass1 + `CoreTypeChecker`）。
- `semantics/core/{types,checker}.py`：独立类型模型与检查器；只依赖
  `ast`/`diagnostics`/`parser`/`source`。
- `runtime/modules.py`：`CompiledModule` 携带方言名；导入时做方言比较。
- `diagnostics/type_errors.py`：`TypeCheckError`。
- 推断类型写入 `node.metadata["type"]`，供 `-t astm` 展示。

## 未决/后续

- 双向检查的 expected-type 传播、函数返回类型推断。
- Float/String/集合/null、`/`。
- 循环、类/槽、ADT/`match`、泛型/HKT。
- 函数值与高阶函数、函数类型标注。
- 模块接口、跨模块类型检查、跨方言 FFI trampoline/blame。
- REPL 方言切换与持久方言状态。
- 静态对象模型、确定赋值、穷尽性检查。
- HIR 与字节码后端。
