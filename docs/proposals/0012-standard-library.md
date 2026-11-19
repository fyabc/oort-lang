# OP 0012: 最小标准库与宿主边界

- **状态**：Implemented（2026-11-20）
- **作者**：Oort 设计讨论
- **相关**：[OP 0006](0006-modules-and-imports.md)、[OP 0011](0011-parameter-binding.md)、
  [规范：标准库](../spec/08-stdlib.md)、[设计：宿主边界](../design/12-host-boundary.md)

## 摘要

为 `oort-object` v1 定义最小标准库：

- 全局集合助手 `map`、`filter`、`zip`、`enumerate`、`sorted`；
- 原生模块 `math` 与 `string`。

同时把运行时的 Python 宿主耦合（`py_value` 与隐式解包）收敛为显式的
`HostBridge` / 原生调用模式，为未来 Rust 宿主留下可替换边界。

## 动机

- issue #7 要求集合助手与 `math`/`string` 模块，并补测试、示例和一致性矩阵。
- 当前原生函数把参数递归解包为 Python 值，且拿不到解释器；高阶函数
  `map`/`filter`/`sorted` 无法调用 Oort lambda 或用户 `<` 运算符。
- `OortObject.py_value` 把“Oort 值”和“Python 宿主表示”混在语言核心中，未来
  Rust 宿主无法复用；需要明确 host bridge。

## 跨语言调研

| 语言 | 集合操作位置 | 求值 | 排序 | 数学/字符串 |
|---|---|---|---|---|
| Python | 内建 | `map/filter/zip/enumerate` 惰性；`sorted` 急切 | 稳定；`key`/`reverse` 关键字 | `math`、`string` 模块 |
| JavaScript | `Array.prototype.*` | 急切新数组 | `sort` 原地，ES2019 起稳定 | 全局 `Math`；`String` 方法 |
| Kotlin | 集合扩展函数/Sequence | 集合操作急切；Sequence 惰性 | 稳定 | `kotlin.math`、`kotlin.text` |
| Rust | Iterator 适配器 | 惰性，需消费者 | `slice::sort` 稳定 | `std`/原生库 |
| Go | 无内建 map/filter；`slices`/`sort` | 显式循环 | `sort`/`SliceStable` | `math`、`strings` 包 |
| Ruby | `Enumerable` | 急切数组；`.lazy` 可选 | 非保证稳定 | `Math` 模块；`String` 方法 |

来源：

- Python <https://docs.python.org/3/library/functions.html>
- JavaScript <https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/map>、
  <https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/sort>
- Kotlin <https://kotlinlang.org/docs/collections-overview.html>
- Rust <https://doc.rust-lang.org/std/iter/trait.Iterator.html>、
  <https://doc.rust-lang.org/std/primitive.slice.html#method.sort>
- Go <https://pkg.go.dev/math>、<https://pkg.go.dev/strings>、<https://pkg.go.dev/sort>
- Ruby <https://docs.ruby-lang.org/en/master/Enumerable.html>

## 决策

### D1 集合助手是全局内建

与现有 `len`/`range` 一致，也符合仓库已有示例 `map(xs) do(x): ...`。
不引入 `std` 模块或隐式 prelude。

### D2 急切返回 List

当前没有迭代器协议（#8），`range` 也已物化为 List。`map`/`filter`/`zip`/
`enumerate` 返回 List；`sorted` 返回新 List。惰性版本留待 #8 之后重新评估。

### D3 集合优先、回调最后

Oort 的尾随块是最后一个位置实参，因此：

```oort
map(iterable, callback)
filter(iterable, predicate)
sorted(iterable, key = null, reverse = false)
```

与 Python 的 `map(callback, iterable)` 不同；`map` 只支持单个可迭代对象，
多序列组合用 `zip`。

### D4 `sorted` 稳定且使用 Oort `<`

- 稳定排序；相等元素保持原顺序；
- `key` 每个元素调用一次；`reverse` 按 truthiness；
- 比较只调用 Oort `<`，尊重用户 `def operator "<"`；不使用整容器的宿主比较；
- 用户类缺少 `<` 或混合不可比较类型时报 `OortTypeError`。

### D5 `math` / `string` 是封闭的原生模块

- 由 `ModuleLoader` 的**内部可信注册表**提供，按解释器惰性构建；
- 裸名 `import "math"` / `"string"` 优先于文件；`./math` 仍加载本地文件；
- 不是用户可用的宿主模块/FFI；用户不能通过 `import` 加载 Python/C 模块；
- 未来 Rust 宿主提供同名原生模块；语言可见 API 由规范固定。

### D6 宿主边界

- `OortObject.py_value` 改为 `host_value`；函数/用户对象/模块的 host 投影仍是
  自身，不再暴露 Python callable；
- `HostBridge` 提供 `to_host`/`from_host`；`Runtime.host` 持有 PythonHost；
- 原生调用模式：
  - `HOST`：宿主值进出（运算符、`math`、`string`）；
  - `VALUE`：Oort 值进（`print`、`type`、`super`、`str`、`repr`、`len`）；
  - `CONTEXT`：`NativeContext` + Oort 值进（集合助手）。
- `NativeContext` 提供 `call`、`truthy`、`iterate`、`binary`；解释器提供对应
  的 `call_value`、`is_truthy`、`iter_values`、`apply_operator`。
- 嵌套容器投影是深拷贝，使用 memo 保持别名与 List/Dict 自引用；经由 Tuple 的
  循环显式报错。集合助手不投影，直接操作 Oort 值。
- `len` 使用 VALUE 模式，避免为了长度深拷贝容器。

## API

### 集合助手

| 函数 | 规则 |
|------|------|
| `map(iterable, callback)` | 每个元素调用一次；返回新 List |
| `filter(iterable, predicate)` | `null` 谓词按 truthiness；返回新 List |
| `zip(*iterables)` | 最短截断；无参数返回空 List |
| `enumerate(iterable, start = 0)` | `start` 为 Int；返回 `(Int, value)` 元组 List |
| `sorted(iterable, key = null, reverse = false)` | 稳定；新 List；Oort `<` |

参数均为位置参数（OP 0011 D8）；输入支持 List/Tuple/Set/Dict（键）/String
（字符）；用户迭代器留待 #8。

### `math`

常量 `pi`、`e`、`tau`；函数 `sqrt`、`pow`、`fabs`、`floor`、`ceil`、`trunc`、
`exp`、`log`、`log10`、`sin`、`cos`、`tan`、`atan2`。Bool 不是数字；定义域
错误为运行时错误。

### `string`

`split`、`join(parts, sep = "")`、`upper`、`lower`、`strip`、`lstrip`、
`rstrip`、`startswith`、`endswith`、`find`、`replace`。参数为 String；
`join` 接受字符串 List/Tuple；Unicode 由宿主处理。

## 错误模型

- 参数/类型/不可迭代/不可调用/不可比较 → `OortTypeError`（调用点）；
- 数学定义域错误 → `OortRuntimeError`（调用点）；
- `from "math" import nope` → `OortImportError`；
- 原生模块只读，`math.x = ...` 被拒绝。

## 性能

- 原生模式分派是常数级开销；深拷贝只发生在 HOST 投影。
- 集合助手 CONTEXT 不投影；`len` VALUE 不投影；原生模块工厂惰性构建，
  不增加启动时间。
- 新增 `benchmarks/test_stdlib.py` 覆盖 map/filter/sorted/zip/enumerate、
  `string.join`、列表相等（深投影）与嵌套 `len`；作为重构后的新基准基线，
  由 `gh-pages` 历史持续跟踪。

## 替代方案

1. **把五个助手放进 `std` 模块**：命名空间更干净，但已有文档使用裸 `map`，
   且与 `len`/`range` 的内建风格不一致。
2. **惰性迭代器**：与 Python/Rust 一致，但依赖尚未实现的 #8，会把两个 issue
   绑定。
3. **把 `math`/`string` 写成 `.ort`**：dogfood 更好，但数学函数仍需隐藏宿主
   原语，且引入包数据、方言与启动编译问题。
4. **保留隐式 `py_value` 解包**：改动小，但高阶原生函数与 Rust 宿主都受限。

## 未解决问题

- 惰性版本与迭代器协议（#8）。
- 集合助手的方法式/管道式 API（#9 扩展方法、`|>`）。
- 更多 `math`/`string` API（`min`/`max`/`sum`、格式化、字符码）。
- 用户宿主模块与 FFI（独立提案）。
- 原生函数的关键字参数支持（OP 0011 D8 当前拒绝）。
