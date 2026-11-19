# 迭代器实现

对应 [OP 0013](../proposals/0013-iterator-protocol.md) 与
[规范 09](../spec/09-iterators.md)。

## 协议分发

`ASTInterpreter`：

- `open_iterator(value, position)`：
  - 排除 `OortType` / `OortModule`（类对象/模块命名空间不可迭代）；
  - 查找 `value.get("__iter__")`，缺失或非可调用报 `OortTypeError`；
  - 无参数调用，返回可调用迭代器。
- `iterator_next(iterator, position)`：
  - `OortIterator` 快路径直接 `next_value()`；
  - 其他迭代器通过 `call_value` 调用，要求恰好 2 元素 `OortTuple`；
  - 第二个元素必须是 `OortBool`（严格）；返回 `(value, bool)`。
- `iter_values`：打开并 drain；`OortIterator` 用 `take_remaining()`，避免第二次
  复制。集合助手使用。

`visit_for_expr` 在循环外打开一次迭代器，逐元素调用 `iterator_next`，保持：

- 每轮新的 `<for>` 环境与不可变循环变量；
- 解包、`break`/`continue`、`break expr`；
- 流式副作用时机；无限迭代器可配合 `break`。

## 原生迭代器

`runtime/functions.py` 的 `OortIterator`：

- 继承 `OortNativeFunction`（`NativeMode.VALUE`），内部持有 values 快照与 index；
- `next_value()` 返回 `(value|None, bool)`，供解释器快路径；
- `take_remaining()` 供急切助手；
- `_next_tuple()` 使手动调用返回 `(value, valid)` OortTuple；
- 类型 `Iterator` 在 `TypeSystem` 中按运行时注册。

`runtime/builtins.py`：

- List/Tuple/String/Dict（键）/Set 的 `__iter__` 使用 `_iter`，返回
  `OortIterator(list(value))`；
- `Iterator` 类型的 `__iter__` 返回自身；
- 使用 VALUE 模式，避免 HOST 深投影容器。

## 边界

- 没有 `yield` 生成器；用户手写闭包。
- 没有 iterator `close`；`break`/错误放弃迭代器。
- `range` 与集合助手仍急切；助手接受有限用户迭代器。
- 静态 `Iterable<T>`/`Iterator<T>`/`Option<T>` 留给 `oort-core`。
