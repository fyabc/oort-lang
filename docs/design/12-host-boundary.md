# 12 - 运行时宿主边界（Host Boundary）

> **文档状态**：设计决策记录（2026-11-20）
> **相关**：[OP 0012](../proposals/0012-standard-library.md)、
> [规范：标准库](../spec/08-stdlib.md)

---

## 1. 问题

树遍历解释器最初把 Python 宿主的表示直接暴露在 `OortObject.py_value` 上：

- 原生函数默认把参数递归解包为 Python 容器；
- 原生方法总是解包 `this`；
- 原生函数拿不到解释器，因此不能调用 Oort lambda、类构造或用户运算符；
- 函数值会泄漏为底层 Python callable。

这既阻碍标准库实现（`map`/`filter`/`sorted`），也把 Python 类型系统绑进语言
核心。未来 Rust 宿主需要同样的能力，但不可能使用 `py_value`。

## 2. Oort 值优先

- **Oort 值**是语言语义的唯一表示：`OortInt`、`OortList`、`OortInstance` 等。
- 宿主表示只在边界出现：原生函数参数/结果、CLI 顶层结果、未来 FFI。
- `host_value` 是 Python 宿主的投影；它不是语言语义的一部分。
- 函数、用户实例、模块、类型没有宿主等价物，投影保持为 Oort 对象本身。

## 3. HostBridge

```python
class HostBridge(Protocol):
    def to_host(self, value: OortObject) -> object: ...
    def from_host(self, value: object) -> OortObject: ...
```

- Python 实现是 `PythonHost`：`to_host` 读取 `host_value`，`from_host` 调用
  `wrap_value`。`Runtime.host` 持有一个实例。
- Rust 宿主实现自己的等价物：`to_host`/`from_host` 在 Rust 值与 Oort 值之间
  转换；语言核心只依赖协议，不依赖 Python 类型。

### 容器投影规则

- List/Tuple/Dict/Set/Slice 深度递归投影；嵌套容器变成宿主容器。
- 同一次投影使用 memo：共享子容器保持同一宿主对象（别名保留）；
  List/Dict 的自引用可保留为 Python 自引用容器。
- Tuple 无法先建空再填充；经由 Tuple 的循环显式抛出 `TypeError`。
- 用户实例、函数、模块、类型保持 Oort 对象；宿主函数若需要其宿主表示，
  必须显式处理或报类型错误。
- `from_host` 递归包装宿主容器；原生标准库只返回无环扁平结构，宿主回调不应
  返回循环引用。

## 4. 原生调用模式

`OortNativeFunction` / `OortNativeMethod` 的 `mode`：

| 模式 | 参数 | 结果 | 用途 |
|------|------|------|------|
| `HOST` | 经 `HostBridge.to_host` 投影 | 经 `from_host` 包装 | 内建运算符、`math`、`string` |
| `VALUE` | Oort 值原样 | 经 `from_host` 包装 | `print`、`type`、`super`、`str`、`repr`、`len` |
| `CONTEXT` | `NativeContext` + Oort 值 | 经 `from_host` 包装 | `map`、`filter`、`zip`、`enumerate`、`sorted` |

- `HOST` 是宿主相关代码；Rust 宿主需要自己的 `math`/`string` 实现。
- `VALUE`/`CONTEXT` 只操作 Oort 值，是宿主无关的语义，可在不同实现间复用思路。
- `len` 使用 VALUE：直接读取 `OortList.__len__` 等，避免为长度做深拷贝。
- 原生方法 `from_native_func` 复制模式；运算符沿用 HOST。

## 5. NativeContext

```python
class NativeContext:
    interpreter: ASTInterpreter
    position: SourcePosition | None
    def call(func, args) -> OortObject
    def truthy(value) -> bool
    def iterate(value) -> list[OortObject]
    def binary(symbol, lhs, rhs) -> OortObject
```

对应解释器钩子：

- `call_value`：统一调用用户函数/方法/类/原生函数，并保留调用位置的诊断；
- `is_truthy`：语言 truthiness；
- `iter_values`：通过 `__iter__` 协议 drain 可迭代值（内置容器与用户迭代器
  共用；见 [09-iterators](../spec/09-iterators.md)）；
- `apply_operator`：按 Oort 运算符表执行（含用户 `operator "<"`）。

`visit_call` 在原生分支先重新抛出 `OortException`，再包装 Python 的
TypeError/Exception，避免 `NativeContext` 诊断被二次包装。

## 6. Rust 宿主迁移

1. 用 Rust 值类型实现 Oort 标量/容器/实例/函数；不引入 `py_value`。
2. 实现 `HostBridge` 等价物：Rust 值与 Oort 值之间的投影/构造。
3. 实现解释器钩子：调用、truthiness、迭代、运算符分派。
4. 提供 `math`/`string` 的原生模块实现（API 以 [spec 08](../spec/08-stdlib.md)
   为准）；集合助手可在 Rust 中按 CONTEXT 语义重写，或共享 Oort 源码。
5. 原生模块注册表保持封闭：只允许受信任的标准库名称，不提供任意宿主模块
   导入。

## 7. 性能

- 模式分派只增加常数级开销；深投影是 HOST 模式的主要成本。
- 集合助手与 `len` 不投影；`math`/`string` 只投影标量或字符串容器。
- 原生模块惰性构建，不增加启动时间。
- 基准见 `benchmarks/test_stdlib.py`；重构后的结果作为新历史基线。
