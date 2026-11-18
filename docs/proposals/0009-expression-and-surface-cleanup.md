# OP 0009: 表达式语义与语法表面积清理

- **状态**：Implemented
- **作者**：Oort 设计讨论
- **相关**：[OP 0002](0002-dsl-support.md)、[OP 0003](0003-grammar-cleanup.md)、
  [OP 0008](0008-lexer-postprocessing-and-repl.md)、[规范：词法](../spec/01-lexical.md)、
  [规范：函数](../spec/04-functions.md)

## 摘要

根据一次完整的代码评审，统一表达式层的优先级与比较语义，并清理一批
“文法接受、语义未定”的表面语法。目标是让容易静默出错或产生歧义的写法
变成显式错误，而不是继续扩大语法超集。

## 决策

### 1. 位运算高于比较；比较非结合

`&` / `^` / `|` 的优先级提高到比较之上（与 Python/Rust 一致）：

```oort
flags & 1 == 0      # (flags & 1) == 0
```

比较运算统一为同一优先级并标记为非结合：

```oort
0 <= i < n          # 语法错误，应写 0 <= i and i < n
```

这样 `flags & 1 == 0` 不再因为 `Bool <: Int` 静默得到错误结果；链式比较
也不会被解析成 `(0 <= i) < n`。

### 2. `Bool` 不再是 `Int` 的子类型

- `true + true`、`true == 1` 不再成立；`Bool` 只支持 `==` / `!=`。
- 容器成员测试对 `Bool` / `Int` 做严格区分（`true in [1]` 为 `false`）。
- 容器成员测试仍使用宿主相等性，不调用用户定义的 `operator "=="`；
  这保留为后续相等性协议的工作。

### 3. 移除标识符的 `!` 后缀

`a!=b`、`x!in xs`、`a!is b` 不再被词法成 `a!` + `=` / `in` / `is`。
Oort 已有 `var`/`val` 表达可变性，`!` 后缀收益不足，直接删除。

### 4. 所有形参列表必须带括号

```oort
def f(x): x + 1
def f(x: Int): x + 1
do(x): x + 1
```

`def f x: Int` / `do x: Int` 现在是语法错误。`:` 在裸形参位置同时可能表示
类型标注与函数体，无法可靠消歧；删除裸形参形式比保留启发式更安全。
如果未来确实需要简洁的裸 lambda，应通过单独提案引入无歧义的形式
（例如 `do x => expr`）。

### 5. 关闭隐式中缀，拒绝半成品

- `a b c` 不再解析为 `a.b(c)`；等 OP 0002 的显式 `infix` 声明落地后再启用。
- 类外 `def C.f`、`class A.B`、显式 `super(...)` 调用统一报
  `UnsupportedSyntax`。父类初始化器使用 `super.__init__(...)`。

### 6. 小步补齐

- `break expr` 使 `while` / `for` 表达式返回 `break` 的值。
- 行首 `.` 续行：
  ```oort
  val name = user
      .profile()
      .name()
  ```
- 增强赋值补齐 `//=`；token `TRUE_DIV` 更名为 `FLOOR_DIV`。
- Dict/Set 的 `str` / `repr` 使用 Oort 字面量定界符
  （`{: ... :}` / `{. ... .}`）。

## 同时修复的实现问题

- `break` / `continue` 不再穿越函数边界（进入函数时清空循环上下文）。
- 参数布局校验的哨兵值从魔法整数改为 `None`，修正首个 `**kw` / `&block`
  参数漏检和标记顺序诊断。
- Pratt 使用整数 binding power，移除 `+0.1` 浮点 epsilon。

## 兼容性

项目处于 `0.x`，上述均为有意的破坏性变更；仓库内的示例、测试与文档已同步。
`super.method`、`super.__init__`、括号形参和显式运算符方法保持可用。

## 测试

- `tests/unit/frontend/test_parser.py`：括号形参、隐式中缀、比较链。
- `tests/unit/frontend/test_parameters.py`：参数布局校验。
- `tests/unit/frontend/test_semantic.py`：循环控制不穿越函数边界。
- `tests/unit/runtime/test_operators.py`：优先级、Bool 严格性、`!` 无空格、
  `//=`、容器成员测试。
- `tests/unit/runtime/test_control_flow.py`：`break value`。
- `tests/unit/runtime/test_classes.py`：行首 `.` 续行与 `super.__init__`。

## 未解决问题

- 比较链的 Python 式语法（`0 <= i < n`）是否作为后续兼容扩展引入？
- 容器成员测试是否改为调用 Oort 的 `==` 协议？
- 容器相等性是否也严格区分 `Bool` / `Int`（当前 List/Tuple/Dict/Set 的 `==`
  仍使用宿主相等性）？
- `Bool` 是否允许大小比较（当前只允许 `==` / `!=`）？
