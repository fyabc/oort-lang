# OP 0013: 迭代器协议

- **状态**：Implemented（2026-11-20）
- **作者**：Oort 设计讨论
- **相关**：[设计笔记 06 §4](../design/06-language-syntax-design.md)、
  [规范：迭代器](../spec/09-iterators.md)、[OP 0012](0012-standard-library.md)

## 摘要

让用户对象可以用于 `for ... in`：可迭代值实现无显式参数的 `__iter__()`，
返回一个零参数可调用迭代器；每次调用迭代器返回 `(value, valid)` 二元 Tuple。
`valid` 是严格 `Bool`：`true` 表示 value 是有效元素（可以是 `null`），
`false` 表示结束。

解释器只通过协议分派，不再按内置容器类型特判；内置容器通过原生 `__iter__`
实现同一协议。

## 动机

- issue #8 要求用户对象可用于 `for`，并明确要求“解释器分派不特判内置容器”。
- 规范 03 已声称支持迭代协议，但实现只有内置容器快照，用户实例报
  “not iterable”。
- 设计笔记 §4 已选定 `(value, valid)` 而非 `StopIteration`：Oort 没有
  `throw`/`try`，用户无法用异常表达结束；异常控制也破坏类型签名与性能。

## 跨语言调研

| 语言 | 协议 | 终止信号 | 评价 |
|---|---|---|---|
| Python | `__iter__` + `__next__` | `StopIteration` 异常 | 成熟，但正常流程依赖异常；PEP 479 修补误抛问题 |
| JavaScript | `[Symbol.iterator]()` + `next()` | `{value, done}` | 每步分配结果对象 |
| Kotlin | `Iterator.hasNext()/next()` | `hasNext == false` | 两次调用，状态显式 |
| Rust | `Iterator::next()` | `Option<T>` | 类型最清晰，需要 ADT/泛型 |
| Swift | `IteratorProtocol.next()` | `nil` | 可选值终止 |
| Lua | generic for 的迭代函数 | 首个值为 `nil` | 闭包状态、无异常；但无法用 nil 元素 |
| Go 1.23 | `iter.Seq` / `yield func(T) bool` | `yield` 返回 false | 推送式、零结果分配 |
| Ruby | `each` + block | block 结束 | 推送式，不适合拉取式助手 |

来源：

- Python <https://docs.python.org/3/reference/datamodel.html>
- JavaScript <https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Iteration_protocols>
- Kotlin <https://kotlinlang.org/api/core/kotlin-stdlib/kotlin.collections/-iterator/>
- Rust <https://doc.rust-lang.org/std/iter/trait.Iterator.html>
- Swift <https://developer.apple.com/documentation/swift/iteratorprotocol>
- Lua <https://www.lua.org/manual/5.4/manual.html#3.3.5>
- Go <https://pkg.go.dev/iter>
- Ruby <https://docs.ruby-lang.org/en/master/Enumerator.html>

## 决策

### D1：拉取式闭包 `(value, valid)`

- `__iter__` 返回一个可调用对象；调用一次拉取一个元素。
- 返回 `(value, valid)`：`valid` 为 `true` 时 value 有效；为 `false` 时结束。
- 结束是数据，不是异常；没有 `StopIteration`。
- 设计笔记旧称 `has_next`，但其示例与调研伪代码实际是 `valid`；本提案统一
  使用 **`valid` / `has_value`**，避免“最后一个元素被丢弃”或“空迭代无法表达”
  的歧义。用户已确认。

### D2：严格 Bool

`valid` 必须是 `OortBool`，不接受 `1`/`0`/`null` 的 truthiness。Oort 已严格
区分 `Bool` 与 `Int`；协议也保持这个边界。`value` 可以是 `null`，由独立
flag 与结束区分。

### D3：内置容器实现同一协议

- `List`、`Tuple`、`String`（字符）、`Dict`（键）、`Set` 的类型字段新增原生
  `__iter__`，返回原生 `OortIterator`。
- 解释器只调用 `__iter__`，没有 `isinstance(OortList/String/...)` 特判。
- 原生 iterator 的 `next_value()` 是解释器快路径，避免每步分配
  `(value, valid)` Tuple；这是对 iterator 实现的优化，不是对容器特判。
- 内置容器在 `__iter__` 时快照；迭代期间修改容器不影响当前循环（保持既有
  语义，也避免 Python dict 结构修改错误）。
- 用户迭代器状态由用户闭包控制；`__iter__` 每次调用应返回新迭代器。

### D4：流式 `for`

- `for` 打开一次迭代器，逐元素拉取；不先物化整个列表。
- 支持无限迭代器（配合 `break`）、正确的副作用时机、`break`/`continue`、
  `break expr`、多目标解包和逐迭代闭包绑定。
- 没有 iterator close：`break`/错误直接放弃迭代器；资源型迭代器需要未来的
  `close` 扩展。

### D5：不支持的扩展

- `yield`/生成器仍被拒绝；未来可以编译成同一闭包协议。
- `range` 与集合助手保持急切；助手接受有限用户迭代器，但会 drain 成 List。
- `in`/`len` 不扩展到用户迭代器。
- 静态 `Iterable<T>` / `Iterator<T>` / `Option<T>` 视图留给 `oort-core`
  与 OP 0005；动态 v1 只保证运行时 Tuple 协议。
- `OortType`（类对象）与 `OortModule` 不是可迭代实例；它们即使有同名成员也
  报 “not iterable”。

## 协议与错误

```oort
class Countdown {
    def __init__(n) { this.n = n }
    def __iter__() {
        var current = this.n
        do {
            if current > 0 {
                val value = current
                current = current - 1
                (value, true)
            } else {
                (null, false)
            }
        }
    }
}
for value in Countdown(3) { print(value) }
```

错误：

| 情况 | 诊断 |
|---|---|
| 没有 `__iter__` | `Type 'X' is not iterable` |
| 类对象/模块 | `Class 'C' is not iterable` / `Module 'm' is not iterable` |
| `__iter__` 非可调用 | `Type 'X' has a non-callable '__iter__'` |
| `__iter__` 返回非可调用 | `__iter__() must return a callable iterator` |
| 步进不是 Tuple | `Iterator must return a Tuple` |
| Tuple 不是 2 元素 | `Iterator must return a 2-element Tuple (value, valid)` |
| valid 不是 Bool | `Iterator 'valid' flag must be a Bool` |
| 迭代器内部错误 | 原样传播，不当作耗尽 |

`__iter__` 带形参、`iterator()` 带实参等绑定错误按普通调用错误报告。

## 与现有特性的交互

- 集合助手（OP 0012）通过 `iter_values` 自动接受有限用户迭代器；仍然返回
  List，无限迭代器会阻塞。
- `for` 的循环变量仍是每轮新的不可变绑定；解包与 `break`/`continue` 不变。
- 模块中的类定义照常工作；类方法闭包指向定义模块的全局环境。
- 每个解释器有独立的 `Iterator` 类型；不注册模块级单例。
- 树遍历器每步对用户迭代器分配一个 OortTuple；文档不声称零分配。原生迭代器
  快路径避免内置容器每步分配。

## 实现记录（2026-11-20）

- `runtime/functions.py`：`OortIterator`（原生可调用迭代器，`next_value` 快
  路径、`take_remaining` 助手 drain、手动调用返回 `(value, valid)`）。
- `runtime/type_system.py`：每运行时注册 `Iterator` 类型。
- `runtime/builtins.py`：内置容器的 `__iter__` 字段与 `Iterator` 类型对象。
- `runtime/interpreter.py`：`open_iterator`、`iterator_next`、流式
  `visit_for_expr`；删除容器 `isinstance` 特判和 `host_value` 迭代回退。
- 测试：`tests/unit/runtime/test_iterators.py`、标准库/示例/基准更新。
- 规范：[`docs/spec/09-iterators.md`](../spec/09-iterators.md)。
