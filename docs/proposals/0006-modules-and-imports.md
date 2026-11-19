# OP 0006: 模块与导入系统

- **状态**：Implemented（2026-11-19）
- **作者**：Oort 设计讨论
- **相关**：[OP 0001](0001-feature-layers-and-dialects.md)、[设计笔记 06](../design/06-language-syntax-design.md)、[规范 07](../spec/07-modules.md)

## 摘要

为 Oort 定义模块系统：模块身份、导入语法、查找路径、初始化顺序、循环依赖与可见性。
目标是用 AST 级模块替代 C++ 的 `#include` 文本包含。

## 动机

- 当前 `import` 语法可解析，但语义分析会报“未实现”。
- 头文件模型带来宏泄漏、ODR、重复解析、编译时间等问题；Oort 从一开始就应避免。
- DSL/方言（[OP 0001](0001-feature-layers-and-dialects.md)）需要模块级边界。

## 设计

### 1. 模块身份

- 一个 `.ort` 文件是一个模块。
- 模块名由文件路径 + 包根决定，而不是由内容声明决定；避免 C++ 头文件 guard 式重复。
- 每个模块编译一次并缓存；导入得到同一个模块对象。
- 实现用 `Path.resolve()` 作为缓存键：同一文件经不同相对写法或符号链接到达时
  只初始化一次。

### 2. 语法

```oort
import "math"                    # 导入模块，绑定到 math
import "math" as m               # 起别名
from "math" import sqrt, pow as power
```

现有文法已支持上述形式。补充约定：

- `import` 仅允许在模块顶层；函数/块/类体内的 import 报清晰诊断。
- 默认绑定名取路径最后一段并去掉 `.ort`；非法标识符要求 `as`。
- 所有顶层名字公开；导入进模块的名字会随模块命名空间再导出。

### 3. 查找路径

- 相对路径（以 `./`、`../` 开头）相对于当前模块目录；字符串输入与 REPL
  以当前工作目录为基准。
- 裸模块名相对于项目根/标准库路径；本版项目根是入口文件所在目录。
- 通过编译器选项 `-I/--module-path DIR`（可重复）增加搜索路径。
- 省略扩展名时补 `.ort`；其他扩展名、目录模块与 OS 绝对路径在首版显式拒绝。

### 4. 初始化语义

- 默认**急切**：导入即执行模块顶层语句，且在实际使用前完成。
- 顶层 `import` 提升到模块正文之前执行，按源码顺序完成依赖初始化
  （与 ES 模块、Go 的依赖初始化一致）。
- 模块顶层只允许定义与初始化；复杂副作用建议放到显式 `init()`。
- 重复导入只执行一次。

### 5. 循环依赖

- 长期允许模块图存在环，但初始化顺序需拓扑；环中模块看到未初始化绑定时报错。
- **本版禁止循环导入**，诊断包含环链（如
  `Circular import detected: main.ort -> a.ort -> main.ort.`）；含入口文件的环
  同样会报告。

### 6. 可见性

- 默认公开所有顶层名字（玩具语言阶段）；后续增加 `private`/`pub` 或下划线约定。
- 模块对象是命名空间的只读视图；内建名字不属于模块属性。
- 模块的方言（`#lang`）随模块记录，跨方言调用必须经过 FFI 边界。

### 7. 与类型系统的交互

- 静态模块导入时，类型信息立即可用（不依赖运行期）；
- 模块接口可单独检查，避免全程序重编译。
- 本版只保存 AST 与模块环境；接口签名缓存留给 `oort-core` 与类型检查器。

## 跨语言调研（2026-11-19）

在确定“顶层-only、提升执行、规范路径缓存、首版禁环”之前，对照了主流语言的
模块模型：

| 语言 | 导入位置 | 解析/标识 | 执行与缓存 | 循环 | 可见性 |
|---|---|---|---|---|---|
| Python | `import` 是语句，可出现在函数/块内 | `sys.path`（脚本目录、`PYTHONPATH`、site-packages）；包用 `__init__.py` | 首次导入执行，`sys.modules` 缓存；执行前先放入缓存 | 允许，B 可能看到只初始化一半的 A | 全部公开，下划线为约定 |
| Go | `import` 声明只能在文件顶层 | import path 由模块根解析；绑定名来自被导入包的 `package` 子句 | 依赖先初始化，包只初始化一次 | 直接/间接导入自身非法 | 首字母大写才导出 |
| ES 模块 / Node | 静态 `import` 只在模块顶层，且被提升 | 相对 URL 相对导入者；裸名走 node_modules；扩展名/index 探测 | 图求值一次；Node 以 realpath 缓存 | 允许；未初始化绑定触发 TDZ | 显式 `export` |
| Java | import 只在编译单元顶层 | 包名；类路径 | 按需加载，类初始化惰性 | 普通类可循环；命名模块 `requires` 环非法 | `public` / 包私有 |
| Kotlin | import 是文件级指令，位于声明之前 | 包名 | JVM 类加载 | 允许 | 默认 `public` |
| Swift | import 只能在模块作用域/文件顶层 | 模块名 | 模块编译期链接 | 模块依赖环通常不可构建 | 默认 `internal`，需 `public` |
| Rust | `mod` 构成模块树，`use` 可在块内 | `foo.rs` / `foo/mod.rs`，crate 名 | 无运行期模块初始化 | crate 依赖环不可构建 | `pub` |
| Dart | import 指令在库文件顶部 | URI：相对、`package:`、`dart:` | 库只加载一次 | 允许 | 库内公开 |

来源：

- Python import 系统与 `sys.modules` 预插入：
  <https://docs.python.org/3/reference/import.html>；教程“只执行一次”：
  <https://docs.python.org/3/tutorial/modules.html>；`-I` 实际是 isolated mode：
  <https://docs.python.org/3/using/cmdline.html#cmdoption-I>
- Go spec（“It is illegal for a package to import itself, directly or indirectly”）：
  <https://go.dev/ref/spec#Import_declarations>、<https://go.dev/ref/spec#Package_initialization>
- ES 模块图、提升、求值一次、循环 TDZ：
  <https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Modules/Module_graph>
- Node 解析/缓存/`index.js`/realpath：<https://nodejs.org/api/modules.html>
- Java JLS 第 7 章（import 仅编译单元顶层；命名模块环非法）：
  <https://docs.oracle.com/javase/specs/jls/se21/html/jls-7.html>
- Kotlin packages/imports：<https://kotlinlang.org/docs/packages.html>
- Rust modules：<https://doc.rust-lang.org/reference/items/modules.html>
- Swift access control（默认 internal）：
  <https://github.com/swiftlang/swift/blob/main/docs/AccessControl.md>
- Dart libraries：<https://dart.dev/language/libraries>
- `-I` 作为搜索路径的编译器传统：
  <https://gcc.gnu.org/onlinedocs/gcc/Directory-Options.html>（Python 的 `-I`
  含义不同，因此 Oort 以 `--module-path` 为正式名称）

结论：Oort 采用 Go/ES 式静态模块语义（顶层声明、依赖先初始化、禁止环），
而不是 Python 的“语句位置执行、允许半初始化环”。这为后续模块接口检查与
渐进类型迁移保留确定性。Kotlin/Python 的“默认公开”对应当前玩具阶段的
全公开可见性；显式导出留待后续提案。

## 正交性检查

- 与宏：宏的可见性需与模块绑定，不能像 C 宏一样跨模块泄漏。
- 与方言：模块是方言边界。
- 与缓存/字节码：模块是编译单元与缓存键。

## 替代方案

1. **C++ 式文本包含**：放弃，问题太多。
2. **隐式自动导入标准库**：方便但不利于可读性；可作为预导入列表（prelude）。
3. **仅支持 `from ... import`**：表达力不足。
4. **允许宿主语言模块直接 `import`**：放弃。类型映射、内存/错误模型与平台相关
   二进制分发都需要独立的 FFI 设计（OP 0001、设计笔记 07）；`import` 只解析
   `.ort` 模块。

## 实现记录（2026-11-19）

- `runtime/modules.py`：路径解析、规范路径缓存、`LOADING/LOADED/FAILED`
  状态与环链诊断；加载器通过回调注入编译/执行/环境/模块工厂，不依赖 driver。
- `runtime/environment.py`：模块根环境与 `module_root` 指针；共享 builtins
  环境；顶层重定义规则改为显式 `allow_redefine`。
- `runtime/interpreter.py`：每模块独立顶层环境；全局名按
  `self.env.module_root` 解析，跨模块函数/方法仍使用定义模块的全局。
- `runtime/objects.py`：`OortModule` 原生值；`Module` 类型注册。
- `semantics/pass1.py`：顶层 import 放行，嵌套 import 拒绝。
- `driver/compiler.py`：非退出式 `compile_unit`、`-I` 搜索路径、加载器接线；
  `diagnostics/error_handler.py` 改为按 `(error, input_info)` 配对并按
  `(filename, line, column)` 排序。
- 测试：`test_module_resolution.py`、`test_modules.py`、`test_imports.py`、
  `test_error_handler.py`，以及 CLI/REPL/示例集成测试；示例
  `examples/04_modules/`。
- 规范：[`docs/spec/07-modules.md`](../spec/07-modules.md)。

## 未解决问题

- 模块名与包名的映射规则：本版用入口目录 + `-I` + 路径派生名；包清单
  （`oort.toml` 等）未定义。
- 模块级可变全局状态：允许，初始化顺序由提升后的导入顺序保证；是否需要
  `init()` 约定待后续。
- 编译缓存与源码位置信息的持久化格式：本版仅进程内 AST/模块缓存。
- 目录包、`import lazy`、显式导出与宿主模块/FFI：均推迟到独立提案。
