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

- `PrimitiveType("Int"|"Bool"|"Unit")`；
- `FunctionType(params, ret)`；
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
- 函数：顶层、标注必填、位置参数、精确元数、所有路径返回。
- 条件：条件必须 Bool；无 `else` 为 Unit；分支类型用 `join_types` 合并。
- 运算：Int 算术/比较、Bool 逻辑、同类型相等；`/` 与 `**` 显式拒绝。
- `print`：特殊内建，返回 Unit；用户绑定优先。

## 模块边界

`runtime/modules.py` 的 `CompiledModule` 携带编译期解析出的方言名。
`ModuleLoader` 在编译目标模块后、执行前比较导入方与目标方言：

- 相同：正常执行；
- 不同：抛 `OortImportError`，提示需要显式 FFI 边界。

`oort-core` 自身在检查器中拒绝所有 import，因此 core 模块目前是入口模块。

## 诊断

- 类型错误：`diagnostics/type_errors.py` 的 `TypeCheckError(OortSyntaxError)`。
- 未实现构造：`UnsupportedSyntax`。
- 所有诊断都带 `SourcePosition`，由 `CompilerErrorHandler` 统一排序/上报。

## 测试

- `tests/unit/frontend/test_core_types.py`：类型模型。
- `tests/unit/frontend/test_core_checker.py`：正向/拒绝/错误恢复矩阵。
- `tests/unit/frontend/test_analyzer_dispatch.py`：分析器选择。
- `tests/unit/runtime/test_core_execution.py`：检查后执行与 Unit/null 映射。
- `tests/unit/runtime/test_modules.py`：跨方言导入拒绝。
- `tests/integration/test_cli.py`、`test_repl.py`、`test_examples.py`：
  端到端、REPL 限制与示例。
