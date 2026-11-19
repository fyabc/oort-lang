# 标准库

> 本页描述 `oort-object` v1 的最小标准库（[OP 0012](../proposals/0012-standard-library.md)、
> [OP 0015](../proposals/0015-minimal-io-and-process.md)）。
> 集合助手是全局内建；`io`、`math`、`os`、`string` 是封闭的宿主原生模块。
> 所有集合助手都是**急切**的：返回新的 List，不返回惰性迭代器。
> 用户定义的可迭代对象遵循 [09-iterators.md](09-iterators.md)；助手会接受
> 有限用户迭代器并立即 drain 成 List。

## 集合助手

| 函数 | 签名 | 返回值 |
|------|------|--------|
| `map` | `map(iterable, callback)` | 新 List |
| `filter` | `filter(iterable, predicate)` | 新 List |
| `zip` | `zip(*iterables)` | List of Tuple |
| `enumerate` | `enumerate(iterable, start = 0)` | List of `(Int, value)` Tuple |
| `sorted` | `sorted(iterable, key = null, reverse = false)` | 新 List |

### 回调顺序

Oort 采用**集合优先、回调最后**的顺序，以支持尾随 lambda：

```oort
print(map([1, 2, 3]) do(x): x * 2)       # [2, 4, 6]
print(filter([1, 2, 3]) do(x): x > 1)    # [2, 3]
```

这与 Python 的 `map(function, iterable)` 不同；Oort 的尾随块总是最后一个
位置实参。`filter(iterable, null)` 按元素 truthiness 过滤。

### 规则

- `map` / `filter` 对 List、Tuple、Set、Dict（迭代键）、String（迭代字符）
  操作，也接受实现了 `__iter__` 的有限用户对象；助手会立即 drain 成 List。
  无限迭代器会让助手一直运行；只有 `for` 是流式。
- `zip` 在最短输入结束时停止；无参数返回空 List。
- `enumerate` 的 `start` 必须是 Int，可为负数。
- `sorted`：
  - 返回新 List，不修改输入；
  - 稳定排序：比较相等的元素保持原相对顺序；
  - `key` 为 `null` 时比较元素本身，否则对每个元素调用一次 `key`；
  - `reverse` 按 truthiness 解释；
  - 比较只使用 Oort `<` 运算符，因此用户类必须定义 `def operator "<"`；
  - 混合类型或缺少 `<` 时报 `OortTypeError`。
- 所有参数都是位置参数（原生内建不接受关键字，见 OP 0011 D8）。
- `sorted(xs) do(x): key` 是合法的尾随 lambda 写法；`reverse` 需要显式写
  `sorted(xs, key, true)`。注意 `sorted(xs, null) do(x): ...` 会把 lambda 当作
  第三个实参（`reverse`），不会自动识别为 key。

## `math`

```oort
import "math"
print(math.floor(math.sqrt(10)))   # 3
```

| 名称 | 类型/签名 | 说明 |
|------|-----------|------|
| `pi`、`e`、`tau` | Float | 常量 |
| `sqrt(x)` | Float | 平方根 |
| `pow(x, y)` | Float | 幂 |
| `fabs(x)` | Float | 绝对值 |
| `floor(x)`、`ceil(x)`、`trunc(x)` | Int | 取整 |
| `exp(x)`、`log(x[, base])`、`log10(x)` | Float | 指数/对数 |
| `sin(x)`、`cos(x)`、`tan(x)` | Float | 三角函数（弧度） |
| `atan2(y, x)` | Float | 反正切 |

- 参数必须是 Int 或 Float；Bool 不是数字，会被拒绝。
- 定义域错误（如 `sqrt(-1)`）报 `OortRuntimeError`，位置在调用点。

## `string`

```oort
import "string"
print(string.split("a,b,c", ","))       # [a, b, c]
print(string.join(["a", "b"], "-"))    # a-b
```

| 函数 | 说明 |
|------|------|
| `split(text[, sep])` | 返回 List[String]；`sep` 为 `null`/省略时按空白切分 |
| `join(parts[, sep])` | 用 `sep` 连接 List/Tuple 中的字符串；`sep` 默认为空串 |
| `upper(text)`、`lower(text)` | Unicode 大小写转换 |
| `strip(text[, chars])`、`lstrip`、`rstrip` | 去除首尾字符（默认空白） |
| `startswith(text, prefix)`、`endswith(text, suffix)` | 返回 Bool |
| `find(text, needle)` | 返回首个下标，找不到为 -1 |
| `replace(text, old, new)` | 替换全部出现 |
| `ord(text)` | 单字符的 Unicode 码点（Int） |
| `chr(code)` | Unicode 标量值对应的单字符 String |

- 参数必须是 String（`join` 的 parts 必须是字符串 List/Tuple）；类型错误报
  `OortTypeError`，位置在调用点。
- `join` 采用集合优先顺序，与 Go 的 `strings.Join(elems, sep)` 一致。

## `io`

```oort
import "io"
val text = io.read_file("data.json")
io.write_file("copy.json", text)
```

| 函数 | 说明 |
|------|------|
| `read_file(path)` | 读取整个文件并按 UTF-8 解码，返回 String |
| `write_file(path, text)` | 以 UTF-8 覆盖写入；父目录必须存在；返回 `null` |

- 路径按当前工作目录解析；相对路径与脚本所在目录无关。
- 文件不存在、权限不足、解码失败都在调用点报 `OortRuntimeError`。
- 这是整文件、同步 API；没有文件句柄、流式读写或目录操作。

## `os`

```oort
import "os"
print(os.args)          # 用户参数，如 ["input.json"]
print(os.script)        # 脚本路径；-c 与 REPL 为 null
if len(os.args) != 1 {
    os.exit(2)
}
```

| 名称 | 类型/签名 | 说明 |
|------|-----------|------|
| `args` | List[String] | 脚本路径之后的用户参数 |
| `script` | String 或 null | 入口脚本路径；`-c` / REPL 为 `null` |
| `exit(code)` | `(Int) -> never` | 立即以给定状态码结束进程 |

- `oort app.ort a b` → `os.args == ["a", "b"]`，`os.script` 是 `app.ort` 的
  绝对路径。
- `oort -c "..." a b` → `os.args == ["a", "b"]`，`os.script == null`。
- REPL 中 `os.args == []`、`os.script == null`。
- `exit` 接受 0–255；0 表示成功。它立即终止进程，不执行清理。
- 模块是封闭原生的：`./os` / `./io` 可加载本地同名文件。

## 原生标准库模块

- `import "io"`、`import "math"`、`import "os"`、`import "string"`、
  `from "math" import sqrt` 等工作方式与普通模块一致；模块对象只读，重复导入
  返回同一对象。
- 标准库名称是保留的**裸名**：`import "math"` 总是得到原生模块，即使项目里
  有 `math.ort`；要加载本地同名文件请写 `import "./math"`。
- 带扩展名的 `import "math.ort"` 不匹配原生注册表，按普通文件解析。
- 这是运行时内部的封闭注册表（目前为 `io`、`math`、`os`、`string`），不是
  用户可用的宿主模块或 FFI 机制；用户不能通过 `import` 加载 Python/C 模块。

## 错误

- 集合助手的参数错误、不可迭代输入、不可调用回调与不可比较元素都会在调用点
  报 `OortTypeError`（定义域错误为 `OortRuntimeError`）。
- `from "math" import nope` 报 `OortImportError`，列出缺失的名字。
