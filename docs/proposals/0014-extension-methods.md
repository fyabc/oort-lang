# OP 0014: 扩展方法与扩展运算符

- **状态**：Implemented（2026-11-20）
- **作者**：Oort 设计讨论
- **相关**：[设计笔记 04 §7](../design/04-class-object-model.md#7-扩展方法)、
  [规范：扩展方法](../spec/10-extensions.md)、
  [OP 0009](0009-expression-and-surface-cleanup.md)、
  [OP 0013](0013-iterator-protocol.md)

## 摘要

允许在类外为目标类型定义方法：

```oort
def Int.double: this * 2
def List.total {
    var sum = 0
    for x in this { sum = sum + x }
    sum
}
print(3.double(), [1, 2, 3].total())
```

扩展是**词法作用域**的：定义在哪个作用域，就在哪个作用域及其内部可见；
`import` / `from` 激活被导入模块**顶层定义**的扩展。成员、实例字段与类内
运算符永远优先。扩展还可以定义运算符：

```oort
def String.operator "**"(times) { ... }
print("ab" ** 2)   # abab
```

## 动机

- issue #9 要求补上“类名解析与方法注册”：文法早已接受 `def C.f`，但 Pass1
  统一拒绝，运行时也没有扩展表。
- 动态对象模型不允许重新打开类；扩展方法是给其他模块的类或内置类型增加
  行为、实现链式 API 的正规途径。
- 设计笔记 04 §7 已规划“外部调度表 + 词法作用域 + 动态 MRO 分发”，但伪代码
  是 MRO-first，与 Kotlin/C#/Dart/Rust 的实际优先级不同，需要一并修正。
- 扩展运算符是同一机制的延伸：给不能修改的类型补上缺失的运算符
  （Kotlin 的 `operator fun` 扩展、Swift extension 中的运算符声明）。

## 跨语言调研

| 语言 | 成员 vs 扩展 | 作用域/导入 | 扩展之间 | `super` |
|---|---|---|---|---|
| Kotlin | 成员 > 扩展 | 顶层扩展需 import；局部扩展优先于顶层/导入扩展 | 同组内选最具体接收者；歧义报错 | 扩展中不允许 `super` |
| C# | 实例成员 > 扩展 | namespace/using；内层 namespace 优先 | 最具体接收者；无唯一最佳报错 | 扩展是静态方法，无 `super` |
| Dart | 成员优先 | 扩展随 library import 可见；`show`/`hide`/前缀解决冲突 | 未命名扩展仅声明库内可见 | 不适用 |
| Rust | 固有方法 > trait 方法 | trait 必须在作用域内 | 多个候选歧义，UFCS 消歧 | 不适用 |
| Ruby Refinements | 扩展可压过成员 | 严格词法，`using` 后生效 | 按激活逆序，后激活者优先 | `super` 调原类方法 |
| Swift | 扩展不能覆盖成员 | 模块级；扩展成员静态分派 | 最具体重载 | 扩展中禁止 `super` |
| Scala 3 | 扩展按接收者类型解析 | 作用域/导入可见 | 多候选歧义 | 不适用 |

来源：

- Kotlin <https://kotlinlang.org/docs/extensions.html>、
  <https://github.com/JetBrains/kotlin/blob/07b0eeccc45ad94e9e0bcb7edd8e94fb65df6b60/spec-docs/NameResolution.adoc>
- C# <https://learn.microsoft.com/en-us/dotnet/csharp/programming-guide/classes-and-structs/extension-methods>、
  <https://learn.microsoft.com/lt-lt/dotnet/csharp/language-reference/language-specification/expressions>
- Dart <https://dart.dev/language/extension-methods>
- Rust <https://doc.rust-lang.org/stable/reference/expressions/method-call-expr.html>
- Ruby refinements <https://git.ruby-lang.org/ruby.git/plain/doc/syntax/refinements.rdoc>
- Swift <https://docs.swift.org/swift-book/documentation/the-swift-programming-language/extensions/>
- Scala 3 <https://docs.scala-lang.org/scala3/reference/contextual/extension-methods.html>

结论：主流语言一致采用“成员优先 + 词法可见 + 多候选时报歧义”；Ruby 的
“扩展压过成员”是少数派。局部扩展优先于导入扩展也是 Kotlin/C# 的共同行为。

## 决策

### D1：成员、字段与类内运算符优先

`x.f` 先走普通属性查找（实例字段 → 类 MRO → 元类 MRO）；只有查找失败才查扩展。
运算符先查类/原生运算符表，miss 后才查扩展运算符。扩展不能覆盖成员，也不能
覆盖内置运算符（`Int +`、`Object ==` 等）。

### D2：作用域分层优先，层内按 MRO 具体度

查找从使用点所在环境开始，逐层向外：

1. 当前环境的**本地**扩展表（绝对优先）；
2. 当前环境导入的模块扩展，合并为一个候选池，按接收者 MRO 距离选最具体；
3. 外层环境重复 1–2；
4. 找不到 → `OortAttributeError`。

同一接收者类型、同一名字的多于一个导入候选且 MRO 距离相同 → 使用点报
`Ambiguous extension method ...`。不同 ancestor/descendant 的候选不算歧义，
最具体者胜。同一模块以多个别名导入只算一个候选。

本地扩展即使匹配较不具体的类型，也压过导入的较具体扩展——这与 Kotlin 的
“局部声明优先”一致，并由测试固定。

### D3：词法作用域，导入直接激活

- 扩展可在任意非类作用域定义：模块顶层、函数体、块。类体内仍拒绝。
- 扩展表属于 `Environment`；块/调用帧退出后不可见。闭包捕获定义环境，
  因此逃逸的闭包仍能看到定义时的扩展。
- 导入（`import` 与 `from ... import`）激活被导入模块**本地定义**的扩展
  （方法与运算符两张表）。
- 导入不传递：A 导入 B、B 导入 C，A 不会自动看到 C 的扩展。
- 扩展不是名字：不参与 `from "m" import f` 绑定，也不作为模块属性暴露。
- 歧义在使用点检测；未使用的歧义导入不影响程序。

### D4：动态类型分发，定义时解析接收者

- 查找按接收者的**运行时类型** MRO 进行；扩展定义在 `Base` 上时自动适用于
  `Child` 实例。
- `def C.f` 的 `C` 在**定义执行时**按普通词法名字解析，必须已绑定为类型：
  `val T = C; def T.f` 注册到 `C`。目标类尚未定义时执行报
  `OortNameError`；绑定到非类型报 `OortTypeError`。
- 接收者按类型对象身份注册；类被重新定义后旧扩展不再命中新类型。
- 同一作用域重复定义同一 `(类型, 名字)` 报错；模块顶层/REPL 与普通名字一致，
  允许覆盖（便于交互式重定义）。

### D5：`this`、`super` 与继承

- 命中扩展后以 `OortMethod(this=receiver, defining_type=命中类型)` 绑定，
  参数绑定、默认值、关键字实参、尾随块全部复用现有机制。
- `super` 在扩展中允许：`defining_type` 是实际命中的 MRO 类型，`super.f()`
  从该类型之后查**类成员**，绝不回退到扩展。
- Kotlin/Swift 禁止扩展中的 `super`；Oort 有意偏离，因为现有
  `OortMethod.defining_type` 机制已能安全表达，且便于包装被扩展类型的原有行为。
- 扩展可以递归调用自身：`this.f()`（裸 `f` 不是名字）。

### D6：扩展运算符

- 语法：`def C.operator "<sym>"(operand)` / `def C.operator "<sym>"()`。
- Pass1 复用类内运算符的全部校验（符号、元数、禁止默认/变长/关键字/块参数），
  只放宽“必须在类内”。
- 注册到 `Environment.extension_operators[(type, symbol, arity)]`；查找规则与
  扩展方法相同。
- 分派复用 `_find_operator`：`in` 查右操作数、`!=` 回退 `==`、增强赋值、
  一元/二元运算符全部自动获得扩展兜底。
- 类内运算符（含继承与原生运算符）永远优先，扩展只填补缺失的运算符。

### D7：语法

- 扩展方法沿用 `def C.f`，与类方法 `def class.f` 区分；`C` 必须是一个
  标识符（多级接收者 `def A.B.f` 拒绝）。
- 扩展运算符：`def C.operator "+"(other)`。
- 扩展定义不产生普通名字：定义后裸 `f` 不存在。
- `def C.f` 的目标类必须在定义执行前可见（导入会被 hoist，因此写在
  `import` 之前的扩展定义也能看到导入的类）。

### D8：拒绝清单

- 多级接收者：`def A.B.f`。
- 类体内的扩展：`class C { def C.f ... }`。
- 特殊方法：`__init__`、`__iter__`、`__str__`、`__repr__`、`__op_*__` 等
  所有 `__x__` 名字。
- `def class.operator ...`（类运算符方法本身仍未实现）。
- 扩展的接收者不是类型、未定义、或扩展名被当作普通函数使用。

## 替代方案

- **Ruby Refinements 式“扩展压过成员”**：会破坏现有类的不变量，不采纳。
- **MRO-first 查找（设计 04 旧伪代码）**：内层较不具体的扩展会输给外层较具体
  的扩展，与“词法作用域”直觉冲突；改为作用域分层优先。
- **静态解析（Kotlin/C#）**：Oort 是树遍历动态方言，没有静态类型；使用运行时
  类型分发。
- **把扩展存进类**：等价于 monkey patching，无法按作用域隔离；不采纳。
- **先禁止扩展运算符**：文法与作用域机制已具备，只差一张表和一次 miss 兜底；
  允许它可使语言更完整。已确认纳入。

## 测试与实现

- 运行时测试：`tests/unit/runtime/test_extensions.py`（注册、成员优先、继承、
  作用域、闭包、`super`、运算符、导入激活/歧义/非传递、错误诊断、隔离）。
- 前端测试：`tests/unit/frontend/test_ast.py` 的 `is_extension` /
  `extension_receiver` / `is_class_method` 属性；`test_unsupported.py`
  删除旧的统一拒绝用例。
- 示例：`examples/03_oop/03_02_extensions.ort`。
- 基准：`benchmarks/test_extensions.py`（成员调用 vs 扩展调用 vs 扩展运算符）。
- 实现细节见 [实现笔记 07](../implementation/07-extensions.md)。
