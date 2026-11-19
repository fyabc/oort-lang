# OP 0015: 最小 I/O、命令行参数与退出码

- **状态**：Proposed（2026-11-20）
- **作者**：Oort 设计讨论
- **相关**：[OP 0012](0012-standard-library.md)、
  [规范：标准库](../spec/08-stdlib.md)
- **动机来源**：需要一个可运行的 JSON 格式化/校验 CLI 示例，当前语言无法读文件、
  读命令行参数或设置退出码。

## 摘要

新增两个最小的原生模块，让 Oort 程序可以当作真实 CLI 使用：

```oort
import "io"
import "os"

if len(os.args) == 0 {
    print("usage: json.ort <file>")
    os.exit(2)
}

val text = io.read_file(os.args[0])
io.write_file("copy.json", text)
```

同时给 `string` 模块补两个 Unicode 辅助函数：

```oort
string.ord("A")    # 65
string.chr(65)     # "A"
```

## 动机

- 现有标准库只有 `math` / `string`；程序只能处理内嵌数据，无法读取用户文件。
- 没有命令行参数，任何“真实示例”都只能写死输入。
- 没有退出码，CLI 无法区分成功/用法错误/数据错误。
- JSON 的 `\uXXXX` 转义需要码点与字符串互转；`ord` / `chr` 是最小且通用的补口。

## 跨语言调研

| 语言 | 参数（含程序名？） | 读文件失败 | 退出 |
|---|---|---|---|
| Python | `sys.argv[0]` 是脚本名 | `open()` 抛 `OSError` | `sys.exit(code)`，默认 0 |
| Node.js | `process.argv[0/1]` 是 node/入口 | `fs.readFileSync` 抛异常 | `process.exit(code)` |
| Go | `os.Args[0]` 是程序名 | `os.ReadFile` 返回 `(bytes, error)` | `os.Exit(code)` |
| Rust | `env::args()` 首项通常是可执行文件 | `fs::read_to_string` 返回 `Result` | `process::exit(code)` |
| Ruby | `ARGV` **不含**程序名 | `File.read` 抛 `Errno` | `exit(code)` |
| Kotlin | `args` **不含**程序名 | `File.readText` 抛异常 | `exitProcess(code)` |
| Lua | `arg[0]` 是脚本名，`arg[1..]` 是参数 | `io.open` 返回 `nil, err` | `os.exit(code)` |

来源：

- Python <https://docs.python.org/3/library/sys.html#sys.argv>、
  <https://docs.python.org/3/library/functions.html#open>
- Node.js <https://nodejs.org/api/process.html#processargv>、
  <https://nodejs.org/api/process.html#processexitcode>
- Go <https://pkg.go.dev/os#Args>、<https://pkg.go.dev/os#ReadFile>、
  <https://pkg.go.dev/os#Exit>
- Rust <https://doc.rust-lang.org/std/env/fn.args.html>、
  <https://doc.rust-lang.org/std/fs/fn.read_to_string.html>
- Ruby <https://docs.ruby-lang.org/en/master/ARGF.html>、
  <https://docs.ruby-lang.org/en/master/Kernel.html#method-i-exit>
- Kotlin <https://kotlinlang.org/docs/command-line-arguments.html>、
  <https://kotlinlang.org/api/core/kotlin-stdlib/kotlin.system/exit-process.html>
- Lua <https://www.lua.org/manual/5.4/manual.html#6.8>

结论：

- “参数是否含程序名”两种传统都有；Ruby/Kotlin 的用户参数风格更适合脚本作者。
- Go/Rust 的错误返回值模型最清晰，但 Oort 还没有 `Result`/`Option` 与用户级
  异常处理；首版只能选择“运行时错误”或 `null + 错误信息`。
- `os.exit(code)` 在几乎所有语言里都存在，语义一致：立即结束进程。

## 决策（建议）

### D1：模块划分

- `io`：`read_file(path)`、`write_file(path, text)`。
- `os`：`args`、`script`、`exit(code)`。
- `string`：`ord(text)`、`chr(code)`。

模块名沿用 Python 的 `io` / `os` 直觉；不引入 `fs`、`process` 等额外名称。

### D2：`os.args` 只含用户参数

`oort app.ort a b` → `os.args == ["a", "b"]`；`os.script == "app.ort"`。
`oort -c "..." a b` → `os.args == ["a", "b"]`，`os.script == null`。
REPL → 两者分别为 `[]` / `null`。

理由：脚本作者最常写 `os.args[0]`；把脚本名放在 `os.script` 里更清晰。与
Ruby `ARGV`、Kotlin `args` 一致；需要原始 argv 的用户可以组合两者。

### D3：文件 API 是最小、UTF-8、整文件

- `io.read_file(path) -> String`：读取整个文件，按 UTF-8 解码。
- `io.write_file(path, text) -> null`：覆盖写入，UTF-8；父目录必须存在。
- 失败（不存在、权限、解码错误）→ 运行时错误（`OortRuntimeError`），带路径。
- 不做流式读写、目录操作、文件句柄或 stdin；后续按需另立提案。

### D4：`os.exit(code)` 立即结束进程

- `code` 为 Int；建议 0–125；0 表示成功。
- 立即退出，不执行任何清理（Oort 没有 `finally`）。
- 在 REPL 中调用会结束 REPL 进程。

### D5：`ord` / `chr` 使用 Unicode 码点

- `string.ord(text)`：`text` 必须恰好一个 Unicode 字符，返回其码点。
- `string.chr(code)`：`code` 必须是合法的 Unicode 标量值（0–0x10FFFF，排除
  surrogate），返回单字符 String。
- 非法输入 → 运行时错误。

### D6：非目标

- 环境变量、工作目录、stdin、网络、文件元数据、二进制读写。
- 用户级异常/`Result`；JSON 解析错误仍由解析器对象显式返回。
- 沙箱或路径限制：与 Python/Node 一样，文件系统访问不受语言层限制；文档明确
  说明运行不受信任脚本的风险。

## 兼容性

纯新增模块与函数；不影响现有程序。`os`/`io` 作为裸模块名会优先于同名本地文件
（与 `math`/`string` 规则一致）；`./os`、`./io` 仍可加载本地模块。

## 测试计划

- `io`：临时目录读写、UTF-8 中文/emoji、覆盖写入、缺失文件/目录的错误诊断。
- `os`：文件与 `-c` 的参数切分、`os.script`、REPL 空参数、`os.exit(0/2)` 的
  子进程退出码。
- `string.ord/chr`：ASCII、中文、emoji/增补平面、非法长度与非法码点。
- JSON CLI 示例：合法/非法 JSON、`\uXXXX`、代理对、格式化输出、错误退出码。

## 未决问题

- 文件读取失败：首版用运行时错误（无用户级捕获）；未来有 `Result` 后是否改为
  显式返回？
- `os.args` 是 List 值还是函数？建议 List 值（`os.args[0]`），与 `ARGV` 一致。
- 是否需要 `io.read_stdin()` / `print_error()`？首版不做。
- 是否把 `ord`/`chr` 放在全局内建而不是 `string` 模块？建议留在模块内，避免
  污染全局命名空间。
