# 迭代器协议

> 本页描述 `oort-object` v1 的迭代协议，对应
> [OP 0013](../proposals/0013-iterator-protocol.md)。

## 协议

一个值要可用于 `for ... in`，必须实现无显式参数的 `__iter__()`：

1. `__iter__()` 返回一个**零参数可调用迭代器**；
2. 每次调用迭代器返回一个二元 Tuple `(value, valid)`；
3. `valid` 必须是 **Bool**：`true` 表示 value 是有效元素（可以是 `null`），
   `false` 表示结束，value 被忽略；
4. 结束是普通返回值，不是异常；
5. `__iter__()` 每次调用应返回新的迭代器，使嵌套/重复循环互不干扰。

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

for value in Countdown(3) { print(value) }   # 3 2 1
```

设计笔记早期写作 `(value, has_next)`，但该名字与本协议不符；flag 的语义是
**valid / has_value**。使用 `valid=false` 结束，不能把最后一个元素丢弃。

## `for` 的语义

- 循环开始时调用一次 `__iter__()`，之后逐元素拉取；**流式**执行，不先物化。
- `valid=false` 时结束；`valid=true` 的 `null` 会执行循环体。
- 每次迭代创建新的变量绑定，闭包捕获当次值。
- 支持多目标解包；元素必须是长度匹配的 Tuple/List。
- `break` / `continue` / `break expr` 与普通循环一致。
- 无限迭代器可以配合 `break`。
- 没有 iterator close：`break` 或错误直接放弃迭代器。

## 内置容器

以下类型实现同一协议，`__iter__()` 返回原生快照迭代器：

| 值 | 迭代元素 |
|---|---|
| List | 元素 |
| Tuple | 元素 |
| Set | 元素（顺序未定义） |
| Dict | 键（顺序未定义；实现当前通常保持插入顺序） |
| String | 字符 |

- 迭代器在创建时快照；循环期间修改容器不影响当前循环。
- 内置迭代器的类型为 `Iterator`；手动调用 `it()` 返回 `(value, valid)`。

```oort
val it = [1, 2].__iter__()
print(it())      # (1, true)
print(it())      # (2, true)
print(it())      # (null, false)
print(it())      # (null, false)
```

## 手动迭代

- 可迭代值可以直接调用 `.__iter__()` 得到迭代器。
- 迭代器自身也有 `__iter__()`，返回自身（一次性迭代器）。
- 迭代器可以传给 `for`；耗尽后继续 `for` 不会产生元素。
- 没有内置 `iter`/`next` 函数；直接调用 `.__iter__()` 和迭代器。

## 集合助手

`map` / `filter` / `zip` / `enumerate` / `sorted` 接受有限用户迭代器，但仍会
**急切 drain** 成 List。无限迭代器传给这些助手会一直运行；只有 `for` 是流式。

## 错误

| 情况 | 诊断 |
|---|---|
| 缺少 `__iter__` | `Type 'X' is not iterable` |
| 类对象/模块 | `Class 'C' is not iterable` / `Module 'm' is not iterable` |
| `__iter__` 非可调用 | `Type 'X' has a non-callable '__iter__'` |
| `__iter__` 返回非可调用 | `__iter__() must return a callable iterator` |
| 步进结果不是 Tuple | `Iterator must return a Tuple` |
| Tuple 长度不为 2 | `Iterator must return a 2-element Tuple (value, valid)` |
| valid 不是 Bool | `Iterator 'valid' flag must be a Bool` |
| 迭代器内部错误 | 原样传播，不当作耗尽 |

`__iter__` 或迭代器的参数绑定错误按普通调用错误报告。

## 非目标

- `yield` 生成器；未来可编译到同一闭包协议。
- 惰性 `range` / 惰性集合助手。
- `in` / `len` 对用户迭代器的扩展。
- iterator `close()` / 资源清理。
- 静态的 `Iterable<T>` / `Iterator<T>` / `Option<T>` 类型视图（`oort-core`）。
- `__next__` / `StopIteration` 风格协议。
