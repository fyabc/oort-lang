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
- `ClassType(origin, name, slots, methods)`：名义相等，槽/方法在注册后填充；
- `SlotInfo(name, slot_type, mutable, has_initializer)`；
- `FunctionType(params, ret)`、`ModuleType(name, exports)`；
- `AdtTemplate(origin, name, params, constructors)`：enum 声明（类型构造器），
  `constructors` 在声明注册后填充，以支持自递归 payload；
- `AdtType(template, args)`：应用后的类型（`Option[Int]`）；名义相等看
  `(template.origin, template.name)`，实参结构比较。单态 enum 是 `args=()`；
- `TypeParameterType(name, variance)`：声明体内的刚性参数，带声明处变型；
- `ForallType(params, body)`：构造器的多态类型方案；
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
- 函数：顶层、参数标注必填、位置参数、精确元数、所有路径返回；**返回类型可
  省略**（顶层 def、lambda 与类方法从体推断，递归函数/方法仍需标注）；
  lambda 必须显式参数列表；函数值可推断、赋值、传参、返回与调用。算法见
  [design 14](../design/14-core-typechecking.md)。
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
- 类：两遍处理——先收集槽/方法签名并注册 `ClassType`，再检查槽初始化器与
  方法体；方法体作用域绑定 `this: ClassType`；槽赋值按 `val`/`var` 检查。
- 构造器确定赋值：`semantics/core/definite_assignment.py` 用 (definite, maybe)
  集合分析 `__init__`，处理分支交集、循环保守、提前 return、赋值前读取与
  `val` 单次赋值；运行时另有槽初始化与缺失槽兜底。
- `print`：特殊内建，返回 Unit；用户绑定优先；ADT 值可打印，函数值不可打印。
- expected-type 传播：标注、赋值、返回、函数体与调用实参的期望类型会下推到
  `if` 分支、块最后表达式和 `match` arm；不匹配时定位到具体分支/实参。
- 函数返回推断：缺标注时以 `Unknown` 占位建签名，`_infer_stack` 压
  `_ReturnInfer` 帧收集 `return` 类型，查体后与尾表达式类型 `join_types` 合并，
  重建 frozen `FunctionType` 并回填 `NameInfo.type`/`metadata`；`visit_call`
  经 `_mark_recursive_call` 检测自递归（需显式标注）。lambda 的期望返回类型经
  `_build_signature` 的 `default_return` 挂钩下推。**类方法**经
  `_infer_and_check_methods`/`_method_dependencies` 按调用依赖拓扑序推断、回填
  `class_type.methods`，递归环上的方法需显式标注。
  算法与跨语言对比见 [design 14](../design/14-core-typechecking.md)。

## ADT 与 `match`

- `visit_enum_def`：
  - 仅模块顶层、非空；enum 名进入类型命名空间，构造器名进入模块值命名空间；
    先注册 `AdtTemplate` 再解析字段，支持自递归；
  - 类型参数 `[T]` / `[out T]` / `[in T]`：`_enum_type_parameters` 校验
    重名/遮蔽并映射 `VarianceKind`；上界与默认值显式拒绝（无
    traits/interfaces）。解析载荷时 `self.type_parameters` 提供刚性参数；
  - `_check_enum_variance` 按 payload 极性检查变型：函数参数翻转、内建集合
    保持、嵌套 ADT 按声明变型复合，不变型实参把极性压成 0；违规定位到字段。
    算法见 [design 14](../design/14-core-typechecking.md) §7；
  - payload 构造器是 `ForallType(params, FunctionType(payload, adt))`
    （单态时直接是 `FunctionType`），零参构造器同理是 AdtType 值。
- 变型文法：`typeParameter` 用 `(in_variance=IN | out_variance=identifier)?`
  两个独立标签（ANTLR 不允许同一标签混用 token/rule）；AST builder 把
  `in`/`out` 映射为 `VarianceKind`，其他文本报语法错误。`out` 仍是普通标识符。
- 类型应用：`_resolve_container_type` 识别已声明 enum 模板，检查实参数目并
  返回 `AdtType(template, args)`；裸泛型名与单态 enum 加实参分别报错。
- 构造器实例化（`_check_expr` / `_check_generic_call` / `_check_generic_value_expected`）：
  check 模式由同模板期望类型绑定参数（`Some([])` 可用）；infer 模式用
  `unify()` 从实参求解，未绑定报硬错误、冲突报双绑定诊断；裸构造器作值要有
  期望函数类型。算法见 [design 14](../design/14-core-typechecking.md) §7。
- 模式检查（`_check_pattern`）：
  - `_`：覆盖全部；
  - 绑定名：绑定当前期望类型；若命中当前 enum 的零参构造器，则同时限定该
    variant 并绑定该名字；
  - 构造器模式：必须属于当前 enum，元数匹配；载荷先用
    `_instantiated_payload` 代入 scrutinee 实参，再递归子模式；
  - 同一模式重复绑定由 Pass1/arm 作用域报错。
- 每个 arm 独立作用域；arm 体类型用 `join_types` 合并。
- 穷尽性只做**顶层构造器覆盖**：`_`/绑定覆盖全部；构造器模式的子模式都
  不可反驳时覆盖该构造器；嵌套穷尽性未实现。
- 零参构造器复用 `visit_name`；泛型构造器在无期望时由 `visit_name` 报
  “无法推断类型实参”。
- `enum ==` 显式拒绝；`print(enum)` 允许。

## 完整模式匹配（OP 0023）

- **前端**：文法 `pattern : patternPrimary (BIT_OR patternPrimary)*`；
  `patternPrimary` 含 `patternLiteral`（`SUB?` 数字/浮点、字符串、`true`/`false`）、
  元组/分组 `LPA patternList? RPA`、构造器与裸名。`matchArm` 为
  `pattern (IF expression)? FATARROW expression`。AST 增加
  `LiteralPattern`/`TuplePattern`/`OrPattern` 与 `MatchArm.guard`。
- **Pass1**：`_pattern_bindings` 收集 pattern 内唯一绑定名（或模式分支去重），
  在 arm 作用域一次 declare/define，再检查 guard 与 body。
- **检查器**：`_check_pattern` 返回 `PatternResult(bindings, alternatives,
  failed)`；`_NormPattern`（wild/ctor/literal）供 `_missing_witness` 使用。
  字面量精确匹配类型；元组按元素递归；或模式校验绑定名/类型一致；守卫按 Bool
  检查。穷尽性用 Maranget usefulness 的 witness 版；守卫 arm 不入矩阵；矩阵含
  全 wild 行即覆盖（递归 ADT 终止条件）。
- **HIR/字节码**：`Pattern` 增加 `value` 与 literal_*/tuple/or kind；
  `MatchArm`/`MatchArmSpec` 增加 `guard_index`；守卫编译为独立函数（参数为
  pattern 绑定）。`.obc` 写 v2（字面量值 + guard 字段），读兼容 v1。
- **运行时**：解释器 `_match_pattern` 与 VM 同步支持 literal/tuple/or；守卫
  失败继续下一个 arm，不回溯或模式分支。

**内建 `Option`/`Result`（`semantics/core/prelude.py`）**：用 AST 节点构造
`Option[out T]` / `Result[out T, out E]`，由 `Compiler._run_input` 与
`compile_unit_details` 在语义分析前注入 core 模块（`-t ast` 不注入）。注入
`EnumDef` 带 `synthetic=True`（AST printer 跳过）与
`declaration_origin="<core-prelude>"`（检查器用它替代模块路径）。预置构造器
以 `NameInfo.from_prelude` 标记：`visit_module` 过滤导出，`declare` 与 enum/class
重复检查报 `... is declared in the core prelude.`。运行时每个模块照常执行注入
的 enum；运行时模块命名空间仍含这些绑定，但静态导出过滤使检查后的代码不可达。

**与内置容器泛型的关系**：`List[T]`/`Set[T]`/`Dict[K, V]`/`Tuple[...]` 是
`ListType` 等硬编码的结构化类型，由 `_resolve_container_type` 按名字白名单
特判；它们**不经过** `AdtTemplate`。运行时的 `List` 等也只是每种容器一个
不带参数的 `OortType`（`runtime/type_system.py`）。泛型 ADT 是另一套模板
机制，两者不共用实现；统一属于后续类型系统重构。

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
  跨模块构造器与打印；泛型 ADT 的 eval/vm 差分与跨模块用例。
- `tests/unit/frontend/test_core_checker.py::TestCoreVariance`：协变/逆变
  正例、函数位置误用、嵌套不变/逆变复合、非法变型文本与 `out` 标识符兼容。
- `tests/unit/frontend/test_core_checker.py::TestCorePrelude` 与
  `tests/unit/runtime/test_core_adt_execution.py`：内建 Option/Result 的
  构造/匹配、跨模块、导出过滤与保留名；`test_cli.py` 验证 astm 隐藏预置。
- `tests/unit/frontend/test_core_checker.py::TestCorePatterns`：字面量/元组/
  或/守卫正例、绑定一致性、嵌套 witness 与字面量类型错误；
  `test_serialize.py` 覆盖含模式与守卫的 `.obc` round-trip。
- `tests/unit/runtime/test_core_function_values.py`：lambda、闭包、高阶函数、
  函数值跨模块与 ADT payload。
- `tests/unit/runtime/test_core_modules.py`：同方言导入、再导出、类型检查、
  缺失导出、跨方言/native 拒绝与循环检测。
- `tests/unit/runtime/test_modules.py`：跨方言导入拒绝。
- `tests/integration/test_cli.py`、`test_repl.py`、`test_examples.py`：
  端到端、REPL 限制与示例。
