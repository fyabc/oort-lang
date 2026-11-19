# 扩展方法与扩展运算符

> 本页描述 `oort-object` v1 的扩展机制，对应
> [OP 0014](../proposals/0014-extension-methods.md)。

## 语法

```oort
class Counter {
    def __init__(start) { this.n = start }
}

def Counter.bump {
    this.n = this.n + 1
    this
}

def Int.twice: this * 2
def String.operator "**"(times) { ... }
```

- 扩展方法：`def C.f(...) { ... }` / `def C.f: expr`，`C` 是单个标识符。
- 扩展运算符：`def C.operator "<sym>"(operand)` / `def C.operator "<sym>"()`。
- 扩展可以在模块顶层、函数体或块中定义；**不能**在类体中定义。
- 扩展名不是普通变量：`def C.f` 之后裸 `f` 不存在。
- `C` 在定义语句执行时按普通词法规则解析，必须是已绑定的类：
  `def Missing.f` 报 `OortNameError`，绑定到非类型报 `OortTypeError`。
- 导入会被 hoist，因此源码中写在 `import` 之前的扩展也能使用导入的类。

## 查找优先级

读取 `x.f` 或计算 `x + y` 时：

1. **实例字段**（仅方法调用场景）；
2. **类成员**：类 MRO，其次元类 MRO；
3. **扩展**：从使用点的词法环境向外查找；
4. 仍失败 → `OortAttributeError` / `OortTypeError`。

成员、字段与类内运算符永远优先，扩展不能覆盖它们。内置运算符
（`Int +`、`Object ==` 等）同样视为成员，不能被扩展覆盖；扩展只能填补
原本不支持的运算符。

## 词法作用域

扩展按定义位置生效，与环境链一致：

```oort
def Int.tag: "outer"
def scoped() {
    def Int.tag: "inner"
    1.tag()          # inner
}
print(1.tag())       # outer
print(scoped())      # inner
```

- 内层作用域的同名扩展压过外层，即使外层扩展匹配更具体的类型。
- 块或函数调用结束后，其中定义的扩展不再可见。
- 闭包捕获定义环境，逃逸的闭包仍能看到定义时可见的扩展。
- 类体内的扩展定义被拒绝：`Cannot define extension method in class scope.`

## 导入

`import "m"` 与 `from "m" import x` 都会激活模块 `m` **顶层定义**的扩展
（方法与运算符）。规则：

- 只激活模块本地定义的扩展，不传递它自己导入的扩展。
- 本地定义优先于导入的扩展。
- 同一作用域导入多个模块时：
  - 候选匹配不同具体度（ancestor/descendant）→ 最具体者胜；
  - 同一接收者类型、同一名字、同一具体度有多个候选 → 使用点报
    `Ambiguous extension method ...`；
  - 同一模块以多个别名导入只算一个候选。
- 歧义在使用点检测；未使用的歧义导入不报错。
- 扩展不是模块属性，也不参与 `from "m" import f`；`module.f` 不会暴露扩展。
- 块内定义的扩展不会导出给导入者。

## 继承与多态

- 定义在 `Base` 上的扩展适用于 `Child` 实例。
- 同一作用域内同时存在 `Base` 与 `Child` 的扩展时，`Child` 实例命中
  `Child` 的扩展。
- 成员优先于扩展的规则跨越继承：基类的实例方法仍压过子类型上的扩展。

## `this` 与 `super`

- 扩展方法内 `this` 绑定接收者；参数绑定、默认值、关键字实参与尾随块与
  普通方法一致。
- `super` 在扩展中可用，从**实际命中的类型**之后继续查类成员：
  ```oort
  class Named { def name: "named" }
  class Person < Named {}
  def Person.describe: super.name() + " person"
  ```
- `super.f()` **绝不**查找扩展；找不到时抛 `OortAttributeError`。
- 递归调用使用 `this.f()`；裸 `f` 不是扩展的绑定名。

## 扩展运算符

- 校验与类内运算符相同：符号合法、元数匹配、禁止默认/变长/关键字/块参数。
- 分派规则：
  - 二元运算符查左操作数；`in` / `!in` 查右操作数；
  - `!=` 在缺失时回退到 `==`（扩展同样适用）；
  - 增强赋值复用二元运算符；
  - 类内运算符（含继承与原生实现）优先。
- 扩展运算符的 `this`、`super`、作用域与导入规则与扩展方法相同。

## 诊断

| 情况 | 诊断 |
|---|---|
| `def A.B.f` | `Extension methods must name exactly one receiver type ('def C.f').` |
| `def class.A.f` | `Class method names must use 'def class.name'.` |
| 类体内定义 | `Cannot define extension method in class scope.` |
| 特殊方法名 | `Extension methods cannot define special method '<name>'.` |
| 接收者未定义 | `Extension receiver 'C' is not defined.` |
| 接收者非类型 | `Extension receiver 'C' is not a type.` |
| 同作用域重复定义 | 模块根可覆盖；嵌套作用域报 `... is already defined in this scope.` |
| 导入歧义 | `Ambiguous extension method 'f' for type 'C': candidates from 'a' and 'b'.` |
| 运算符非法 | 复用类内运算符诊断（符号/元数/参数形式） |

## 非目标

- 扩展属性（getter/setter 形式）。
- 特殊方法扩展：`__init__`、`__iter__`、`__str__`、`__repr__`、`__op_*__`
  等所有 dunder 名字仍被拒绝。
- 多级接收者（`def A.B.f`）、命名空间类上的扩展。
- 静态类型解析与编译期歧义检查：本版按运行时类型分发，歧义在使用点报告。
- 类运算符方法（`def class.operator`）与 `class A.B` 仍未实现。
