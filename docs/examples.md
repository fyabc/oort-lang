# 示例

示例源码位于仓库的 [`examples/`](https://github.com/fyabc/oort-lang.py/tree/main/examples)
目录；每个文件都可以直接用 `oort <file>.ort` 运行。

## 基础

| 示例 | 内容 |
|---|---|
| [Hello, world](https://github.com/fyabc/oort-lang.py/blob/main/examples/00_basic/00_00_hello_world.ort) | 最小程序与 `print` |
| [控制流](https://github.com/fyabc/oort-lang.py/blob/main/examples/00_basic/00_01_control_flow.ort) | `if` / `while` / `for` |
| [方言指令](https://github.com/fyabc/oort-lang.py/blob/main/examples/00_basic/00_02_lang_directive.ort) | `#lang oort-object` |

## 函数与参数

| 示例 | 内容 |
|---|---|
| [斐波那契](https://github.com/fyabc/oort-lang.py/blob/main/examples/01_functions/01_00_fibonacci.ort) | 递归与计时 |
| [尾随块调用](https://github.com/fyabc/oort-lang.py/blob/main/examples/01_functions/01_01_call_with_block.ort) | `&block` 与 lambda |
| [闭包](https://github.com/fyabc/oort-lang.py/blob/main/examples/01_functions/01_02_closure.ort) | 捕获变量绑定 |
| [参数绑定](https://github.com/fyabc/oort-lang.py/blob/main/examples/01_functions/01_03_parameters.ort) | 默认值、关键字、变长与块参数 |

## 容器与迭代

| 示例 | 内容 |
|---|---|
| [容器字面量](https://github.com/fyabc/oort-lang.py/blob/main/examples/02_collections/02_00_literals.ort) | List / Tuple / Dict / Set、切片 |
| [for 循环](https://github.com/fyabc/oort-lang.py/blob/main/examples/02_collections/02_01_for_loop.ort) | 解包与字典遍历 |
| [用户迭代器](https://github.com/fyabc/oort-lang.py/blob/main/examples/06_iterators/06_00_user_iterators.ort) | `__iter__` 与 `(value, valid)` |

## 类与扩展

| 示例 | 内容 |
|---|---|
| [继承](https://github.com/fyabc/oort-lang.py/blob/main/examples/03_oop/03_00_inheritance.ort) | 继承、`super`、元类 |
| [对象模型](https://github.com/fyabc/oort-lang.py/blob/main/examples/03_oop/03_01_object_model.ort) | 字段袋、方法遮蔽与相等 |
| [扩展方法](https://github.com/fyabc/oort-lang.py/blob/main/examples/03_oop/03_02_extensions.ort) | `def C.f`、扩展运算符、词法作用域 |

## 模块与标准库

| 示例 | 内容 |
|---|---|
| [模块导入](https://github.com/fyabc/oort-lang.py/blob/main/examples/04_modules/04_00_imports.ort) | `import` / `from`、模块属性 |
| [集合助手](https://github.com/fyabc/oort-lang.py/blob/main/examples/05_stdlib/05_00_collections.ort) | `map` / `filter` / `sorted` / `zip` |
| [math 与 string](https://github.com/fyabc/oort-lang.py/blob/main/examples/05_stdlib/05_01_math_string.ort) | 原生标准库模块 |

## `oort-core` 薄探针

| 示例 | 内容 |
|---|---|
| [基础子集](https://github.com/fyabc/oort-lang.py/blob/main/examples/08_core/08_00_core_basics.ort) | `#lang oort-core`、Int/Bool、`var`/`val`、`if`、`print` |
| [静态函数](https://github.com/fyabc/oort-lang.py/blob/main/examples/08_core/08_01_core_functions.ort) | 标注必填、自递归、`-> Unit` 过程 |
| [模块导入](https://github.com/fyabc/oort-lang.py/blob/main/examples/08_core/08_02_core_modules.ort) | core→core `import` / `from`、导出类型 |

```bash
oort examples/08_core/08_01_core_functions.ort
```

## Showcase

| 示例 | 内容 |
|---|---|
| [JSON 解析/格式化 CLI](https://github.com/fyabc/oort-lang.py/blob/main/examples/07_showcase/07_00_json.ort) | `io` / `os`、递归下降解析、`\uXXXX`、pretty-print、错误退出码 |

```bash
oort examples/07_showcase/07_00_json.ort examples/07_showcase/sample.json
```

## 运行

```bash
git clone https://github.com/fyabc/oort-lang.py.git
cd oort-lang.py
uv sync
uv run oort examples/03_oop/03_02_extensions.ort
```
