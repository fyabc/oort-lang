# 模块与导入

> 本页描述 `oort-object` 当前实现的模块系统，对应
> [OP 0006](../proposals/0006-modules-and-imports.md)。本版只支持由 Oort
> 编写的 `.ort` 模块；宿主语言模块与跨语言 FFI 不在范围内。

## 模块身份

- 一个 `.ort` 文件是一个模块。
- 模块名由文件路径决定，模块内容不需要（也不能）声明模块名。
- 同一个文件在一次运行中只编译、初始化一次；重复导入得到同一个模块对象。
- 缓存键是解析后的规范路径。`./a`、`./sub/../a.ort` 等写法指向同一文件时
  共享缓存。

## 语法

```oort
import "./lib"                  # 绑定到 lib（文件名去掉 .ort）
import "./lib" as l             # 绑定到 l
from "./lib" import a, b as c   # 绑定 a 与 c
```

- `import` 只能出现在**模块顶层**。函数、块、类体中的 `import` 报
  `Imports are only allowed at module top level.`。
- 顶层 `import` 会被提升到模块最前执行：所有导入先按源码顺序完成解析与
  初始化，然后才执行其余顶层语句（与 ES 模块、Go 的依赖初始化顺序一致）。
- `import "<spec>"` 的默认绑定名是路径最后一段去掉 `.ort`。若该名字不是
  合法标识符，必须使用 `as` 给出别名。
- 所有顶层名字默认公开；导入进模块的名字也留在模块命名空间中，因此会
  自动再导出。

## 路径解析

设入口文件所在目录为**项目根**（字符串输入与 REPL 使用当前工作目录）。

| 写法 | 解析方式 |
|------|----------|
| `./x`、`../x` | 相对**当前模块**所在目录 |
| `x`、`lib/x` | 依次在项目根、`--module-path` 目录中查找 |
| `x.ort` | 保留扩展名；省略扩展名时自动补 `.ort` |

规则细节：

- 裸模块名不会在当前导入者目录中隐式查找；需要导入者相对路径时显式写
  `./` 或 `../`。
- 其他扩展名（如 `x.py`）会被拒绝：模块路径只接受 `.ort` 或省略扩展名。
- 目录模块（`pkg/`、`pkg/__init__.ort`）尚未支持，命中目录会报错。
- OS 绝对路径（`C:\...`、`/...`）尚未支持；用 `./`、`../` 或
  `--module-path` 指定位置。
- 找不到模块时，诊断会列出所有尝试过的路径。

CLI 可以用可重复的 `-I/--module-path DIR` 增加搜索目录：

```bash
oort --module-path ./libs main.ort
```

`--module-path` 是正式名称；Oort 的 `-I` 与 Python 的 `-I`（isolated mode）
含义不同。

## 初始化与缓存

- 导入是**急切**的：`import` 解析后立即编译并执行模块顶层语句。
- 每个已加载模块只初始化一次；模块对象是命名空间的只读视图：
  `lib.x` 读取当前值，但 `lib.x = ...` 会被拒绝（native 对象不可写）。
- 内建名字不是模块属性：`lib.print` 不存在。
- 模块级变量可以重新赋值；模块顶层也允许重复 `var` 声明（与入口模块的
  顶层规则一致）。
- 循环导入在首版被禁止：`Circular import detected: main.ort -> a.ort -> main.ort.`。
  含入口文件参与的环同样会报告。

## 方言

- 每个模块独立解析首行 `#lang`。被导入模块可以是显式的
  `#lang oort-object`，也可以省略（缺省即 `oort-object`）。
- 导入未知或未实现的方言（如 `oort-core`）会在该模块的诊断中报错。
- 跨方言调用必须经过未来的显式 FFI 边界；本版不提供该机制。

## 导入错误

| 情况 | 诊断 |
|------|------|
| 模块不存在 | `Cannot find module '...'`，列出搜索路径 |
| 目录模块 | `Directory modules are not supported` |
| 其他扩展名 | `Module path '...' must use the .ort extension or none.` |
| `from` 缺少名字 | `Module '...' does not export '...'` |
| 模块编译失败 | 模块自身诊断 + `Failed to import module '...': compilation failed.` |
| 循环导入 | `Circular import detected: ...` |
| 非顶层 import | `Imports are only allowed at module top level.` |

被导入模块中的语法、语义与运行时错误会带该模块的文件名与行号；运行时错误
不会改写成导入处的错误。

## 非目标（本版）

- 导入 Python/C 等宿主模块；未来通过独立提案的 `foreign` / 宿主边界提供。
- 目录包与包清单（`__init__.ort`、`oort.toml` 等）。
- `import lazy` 惰性导入（设计笔记 06 的后续方向，文法尚未提供）。
- 标准库模块；标准库由 #7 单独引入，加载器只负责提供搜索路径与缓存。
