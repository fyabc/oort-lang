# 实现笔记

本目录记录 Oort 编译器的实现细节与设计取舍，面向想了解（或复刻）解释器实现的读者。

语言使用者请阅读 [语言规范](../spec/index.md)；语言演进提案见 [proposals](../proposals/README.md)；
更宏观的设计调研见 [design](../design/00-INDEX.md)。

| 文档 | 内容 |
|------|------|
| [00-references.md](00-references.md) | 参考资料与阅读清单 |
| [01-syntax-design.md](01-syntax-design.md) | 语法设计：字面量、声明、函数、闭包 |
| [02-parser.md](02-parser.md) | ANTLR 词法/语法 + Pratt 表达式解析，错误报告 |
| [03-interpreter.md](03-interpreter.md) | 树遍历解释器、对象模型、作用域与内建函数 |
| [04-class-system.md](04-class-system.md) | 类、继承、元类、`this` / `super` |
| [05-stdlib.md](05-stdlib.md) | 宿主边界、集合助手、`math` / `string` 原生模块 |
| [06-iterators.md](06-iterators.md) | `__iter__` 协议、原生迭代器、流式 for |
| [07-extensions.md](07-extensions.md) | 扩展方法/运算符：分类、扩展表、查找、导入、`super` |
| [08-equality.md](08-equality.md) | 值相等、键协议、CONTEXT/VALUE 运算符与循环容器 |

## 当前实现边界

Oort 目前只有一条执行路径：**树遍历解释器**（`oort -t eval`，默认）。

- 语法前端解析的语言超集比运行时支持的更大；运行时未实现的功能会在语义分析阶段
  以 `UnsupportedSyntax` 显式报错，而不是静默产生错误结果（见
  [规范：未实现功能](../spec/06-conformance.md)）。
- 曾经的寄存器字节码原型已移除：它会在未实现的语法节点上静默“穿透”到子节点，
  产生错误结果。重新实现前的设计要求见 [提案 0004](../proposals/0004-bytecode-vm.md)。
