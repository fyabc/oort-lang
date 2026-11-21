# `oort-core` 类型检查器

本笔记记录薄探针的实现结构。规范见 [spec 11](../spec/11-core-probe.md)，
设计取舍见 [OP 0017](../proposals/0017-oort-core-thin-probe.md)。

## 流水线

```text
source
  -> Compiler._resolve_dialect()        # 首行 #lang
  -> lex/parse + ASTBuilder             # 共享骨架
  -> Compiler.make_semantic_analyzer()  # 按 dialect.features.type_checking 选择
       oort-object -> Pass1Analyzer
       oort-core   -> CoreAnalyzer(Pass1 + CoreTypeChecker)
  -> semantic_analyze()                 # 诊断统一上报
  -> ModuleLoader.execute_entry()       # 复用树遍历解释器
```

`Compiler._run_input`、`compile_unit_details` 与 `ReplSession._submit` 都走
`make_semantic_analyzer`，不再各自构造 `Pass1Analyzer`。

## 分析器

`semantics/analyzer.py`：

- `SemanticAnalyzer` 协议只有 `parse(ast)`。
- `CoreAnalyzer` 先运行 `Pass1Analyzer`；如果 Pass1 增加了错误，就跳过类型检查，
  避免名称解析失败后的级联诊断。
- Pass1 没有错误时运行 `CoreTypeChecker`。

## 静态类型

`semantics/core/types.py` 定义独立于运行时的类型：

- `PrimitiveType("Int"|"Float"|"Bool"|"String"|"Unit")`；
- `ListType`/`SetType`/`DictType`/`TupleType`：结构相等的集合类型；
- `FunctionType(params, ret)`、`ModuleType(name, exports)`；
- `AdtType(origin, name, constructors)`：名义相等只看 `(origin, name)`，
  `constructors` 在声明注册后填充，以支持自递归 payload；
- `ConstructorInfo(name, field_names, payload)`；
- `UnknownType`（错误恢复，兼容一切）；
- `NeverType`（不能正常落到的表达式，例如 `return`）。

`is_assignable(expected, actual)` 与 `join_types(left, right)` 实现探针需要的
最小子类型/分支合并规则。这里不涉及运行时的 `OortType`，也不做 HM。

## 检查器

`semantics/core/checker.py` 的 `CoreTypeChecker`：

- 自带作用域栈 `list[dict[str, NameInfo]]`，不修改 `ScopeLayout`/`Binding`；
- 在 `visit_module` 中按源码顺序检查语句；函数签名在检查函数体前安装，
  因此支持自递归；
- 函数体不额外创建块作用域，与运行时调用环境一致；
- 每个支持的 AST 节点都有显式 visitor；其余节点落到 `visit_children`，
  报 `UnsupportedSyntax` 并返回 `Unknown`，不递归子节点；
- 失败推断返回 `Unknown`；`Unknown` 对任意期望类型静默通过，避免级联；
- 推断类型写入 `node.metadata["type"]`，供 `-t astm` 展示。

关键规则：

- 声明：`val`/`var` 单目标；标注优先，否则局部推断；`Unit` 不能作为变量类型。
- 赋值：只允许 `=` 到 `var`；参数与函数不可变。
- 函数：顶层、标注必填、位置参数、精确元数、所有路径返回；lambda 必须显式
  参数列表与返回类型；函数值可推断、赋值、传参、返回与调用。
- 函数类型：注解中的 `Int -> Bool` / `(Int, Bool) -> Int` / `() -> Unit` 解析为
  `FunctionType`；`is_assignable` 对函数类型逐参数/返回递归比较，`Unknown`
  参与错误恢复。`->` 在 Pratt 表中为右结合（`Int -> Int -> Int` =
  `Int -> (Int -> Int)`）。
- 调用：被调者可以是任意推断为 `FunctionType` 的表达式，因此支持
  `add(1)(2)` 与返回函数的调用；多参数 `def` 仍要求完整元数，不做自动
  部分应用。
- 条件：条件必须 Bool；无 `else` 为 Unit；分支类型用 `join_types` 合并。
- 运算：Int/Float 混合算术（结果类型见规则）、`/` 固定返回 Float、
  数值与 String 比较、数值/Bool/String/同类型集合相等；`**` 因结果类型
  依赖指数而显式拒绝。数值标注不做隐式转换（`val x: Float = 1` 报错）。
- 集合：`List[T]`/`Set[T]`/`Dict[K, V]`/`Tuple[...]` 注解；字面量同质推断
  （Tuple 可异构）；空字面量用期望类型；下标、`len`、集合相等。
- 循环：`while` 条件 Bool；`for` 遍历 List/Set/Dict 键/String/同质 Tuple；
  循环变量单目标且不可变；`break`/`continue` 走 `Never`，`break value` 拒绝。
- `print`：特殊内建，返回 Unit；用户绑定优先；ADT 值可打印，函数值不可打印。
- expected-type 传播：标注、赋值、返回、函数体与调用实参的期望类型会下推到
  `if` 分支、块最后表达式和 `match` arm；不匹配时定位到具体分支/实参。
- 尚未实现函数返回类型推断（签名仍必须显式标注）。

## ADT 与 `match`

- `visit_enum_def`：
  - 仅模块顶层、非泛型、非空；enum 名进入类型命名空间，构造器名进入模块
    值命名空间；先注册 `AdtType` 再解析字段，支持自递归；
  - payload 构造器是 `FunctionType(payload, adt)`，零参构造器是 `AdtType` 值。
- 模式检查（`_check_pattern`）：
  - `_`：覆盖全部；
  - 绑定名：绑定当前期望类型；若命中当前 enum 的零参构造器，则同时限定该
    variant 并绑定该名字；
  - 构造器模式：必须属于当前 enum，元数匹配，子模式按字段类型递归；
  - 同一模式重复绑定由 Pass1/arm 作用域报错。
- 每个 arm 独立作用域；arm 体类型用 `join_types` 合并。
- 穷尽性只做**顶层构造器覆盖**：`_`/绑定覆盖全部；构造器模式的子模式都
  不可反驳时覆盖该构造器；嵌套穷尽性未实现。
- 构造器调用复用 `visit_call`（`FunctionType`），零参构造器复用 `visit_name`。
- `enum ==` 显式拒绝；`print(enum)` 允许。

运行时（`interpreter.py`）：

- `visit_enum_def` 创建 `OortType`，设置 `adt_variants`，定义构造器；
  payload 构造器是 `OortNativeFunction(VALUE)`，零参构造器预构造 `OortADT`。
- `visit_match_expr` 顺序扫描 arms；`_match_pattern` 返回绑定；命中后建立
  独立 `Environment`，按 Pass1 相同顺序定义绑定并求值 body；无命中抛
  `OortRuntimeError`。
- 裸零参构造器模式同样绑定该名字，保证 Pass1 槽位与运行时环境一致。

## 模块导入

core 检查器通过 `ModuleResolver` 回调取得导入模块的导出类型：

```text
Checker.visit_import -> Compiler._resolve_core_module
  -> resolve_module_path
  -> compile_unit_details(target)   # 递归、缓存、循环检测
  -> CoreModuleInfo(dialect, exports)
```

- `CompiledUnit` 缓存 AST、方言与 `CoreAnalyzer.exports`；
  `ModuleLoader` 后续执行时复用同一份 AST。
- 顶层 import 在 `visit_module` 中先于正文绑定，匹配运行时的 import 提升。
- `ModuleType` 保存模块命名空间导出；`visit_attribute` 只允许在模块上取属性，
  `visit_call` 同时接受 `Name` 与模块属性作为被调者。
- `from` 直接绑定导出名；导入名与模块别名均为不可变绑定。
- 导出包括顶层函数、变量、构造器与再导出的导入名，因此支持 re-export；
  enum 类型名只进类型命名空间，暂不支持跨模块类型注解。
- 编译期检测循环导入；跨方言与 native 导入在检查器中拒绝。

`runtime/modules.py` 的 `CompiledModule` 仍携带方言名，`ModuleLoader` 在执行前
做最终方言比较：core→core 允许，object↔core 抛 `OortImportError`。

## 诊断

- 类型错误：`diagnostics/type_errors.py` 的 `TypeCheckError(OortSyntaxError)`。
- 未实现构造：`UnsupportedSyntax`。
- 所有诊断都带 `SourcePosition`，由 `CompilerErrorHandler` 统一排序/上报。

## 测试

- `tests/unit/frontend/test_core_types.py`：类型模型。
- `tests/unit/frontend/test_core_checker.py`：正向/拒绝/错误恢复矩阵。
- `tests/unit/frontend/test_analyzer_dispatch.py`：分析器选择。
- `tests/unit/runtime/test_core_execution.py`：检查后执行与 Unit/null 映射。
- `tests/unit/runtime/test_core_adt_execution.py`：构造、match、嵌套、递归、
  跨模块构造器与打印。
- `tests/unit/runtime/test_core_function_values.py`：lambda、闭包、高阶函数、
  函数值跨模块与 ADT payload。
- `tests/unit/runtime/test_core_modules.py`：同方言导入、再导出、类型检查、
  缺失导出、跨方言/native 拒绝与循环检测。
- `tests/unit/runtime/test_modules.py`：跨方言导入拒绝。
- `tests/integration/test_cli.py`、`test_repl.py`、`test_examples.py`：
  端到端、REPL 限制与示例。
