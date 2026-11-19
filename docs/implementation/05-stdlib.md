# 标准库与宿主边界

实现对应 [OP 0012](../proposals/0012-standard-library.md) 与
[规范 08](../spec/08-stdlib.md)。

## 宿主边界

- `src/oort_lang/runtime/host.py`
  - `HostBridge` 协议：`to_host` / `from_host`；
  - `PythonHost`：`host_value` / `wrap_value`；
  - `Runtime.host` 持有当前宿主的桥接对象。
- `src/oort_lang/runtime/native.py`
  - `NativeMode`：`HOST` / `VALUE` / `CONTEXT`；
  - `NativeContext`：`call` / `truthy` / `iterate` / `binary`。
- `OortObject.host_value` 是 Python 宿主投影；容器的投影是带 memo 的深拷贝。
  用户实例、函数、模块与类型保持 Oort 对象。
- `len` 是 VALUE 模式，直接读取容器长度，不做投影。

解释器钩子（`runtime/interpreter.py`）：

- `call_value`：按可调用对象类型分派，保留调用位置诊断；
- `is_truthy`；
- `iter_values`：`for` 与集合助手共用；
- `apply_operator`：通过 `OortType.operators` 执行 `<` 等运算符。

## 集合助手

`runtime/stdlib/collections.py` 注册五个全局内建（CONTEXT 模式）：

- `map(iterable, callback)`
- `filter(iterable, predicate)`（`null` 谓词按 truthiness）
- `zip(*iterables)`（最短截断）
- `enumerate(iterable, start = 0)`
- `sorted(iterable, key = null, reverse = false)`（稳定、Oort `<`）

全部急切返回 List；不调用宿主投影。`sorted` 用 `functools.cmp_to_key` 与
`NativeContext.binary("<", ...)` 比较 key（或元素）。

## 原生模块

`runtime/stdlib/`：

- `math_module.py`：常量与数学函数，HOST 模式，Bool/非数字被拒绝；
- `string_module.py`：字符串函数，HOST 模式，显式类型检查；
- `__init__.py`：`native_module_factories(interpreter)` 返回惰性工厂。

`ModuleLoader` 接收 `native_modules` 映射；`import_module` 在文件解析前检查
精确裸名，缓存模块对象。`Compiler.make_module_loader` 注入工厂，因此 CLI、
`-c`、REPL 与已安装 wheel 都共享同一行为。

## 测试

- `tests/unit/runtime/test_host_boundary.py`：投影、别名、循环、`len`；
- `test_collection_builtins.py`：五个助手的语义与错误；
- `test_math_string_modules.py`：数学/字符串 API 与错误；
- `test_native_modules.py`：导入、from-import、优先级、缓存；
- `examples/05_stdlib/` 与 `benchmarks/test_stdlib.py`。
