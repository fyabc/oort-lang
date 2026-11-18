# 树遍历解释器

当前唯一的执行后端是 `src/oort_lang/ast_interpreter/` 中的树遍历解释器，
入口参数 `-t eval`（默认）。

选择树遍历而不是字节码，是为了先稳定**语义**：在语言特性仍然快速变化时，
每加一个语法节点只需实现一个 visitor；而字节码后端会把寄存器分配、闭包
布局、异常表等工程问题提前引入（曾经的寄存器 VM 原型因此被移除，见
[proposal 0004](../proposals/0004-bytecode-vm.md)）。

## 对象表示

所有 Oort 值都是 `OortObject` 的实例，带一个 `type`（类型对象）：

| Oort 类型 | Python 类 | 说明 |
|-----------|-----------|------|
| `Int` / `Float` / `String` / `Bool` / `Null` | `OortInt` 等 | 装箱的标量；实现简单，牺牲性能 |
| `List` / `Tuple` / `Dict` / `Set` / `Slice` | `OortList` 等 | 容器与切片 |
| `Type` | `OortType` | 类型对象本身也是对象；`Type.type is Type` |
| `Function` / `Method` | `OortFunction` / `OortMethod` | 用户函数与绑定方法 |
| `Object` | `OortInstance` | 用户类实例 |
| `SuperProxy` | `OortSuperProxy` | `super` 的中间对象 |

- 标量实现 `__eq__` / `__hash__`，因此可以作为字典键和集合元素；
  `List`/`Dict`/`Set` 不可哈希。
- `Bool` 不是 `Int` 的子类型；`Bool` 只登记 `==` / `!=`，不参与算术、位运算
  或大小比较。容器成员测试也对 `Bool`/`Int` 做严格区分。
- lambda 的匿名参数 `$0` / `$1` 在调用时按位置绑定到 `OortFunction` 的调用
  环境；arity 由 `FunctionDef.param_count` 提供。
- `py_value` 提供与 Python 原生值的转换，供内建函数与运算符使用。
- 运算符通过 `OortType.operators` 表调度，键为 `(符号, 操作数个数)`：
  - 用户类在类体中用 `def operator "<sym>"` 定义，解释器在
    `visit_class_def` 中调用 `set_operator` 登记；
  - 内建类型在 `setup_type_system` 中登记原生运算符方法，
    因此 `1 + 2` 与 `Vec(1) + Vec(2)` 走同一条查找/调用路径；
  - `OortMethod.defining_type` 让运算符方法内部的 `super` 正确定位；
  - `is` / `!is` 直接比较对象身份，`and` / `or` / `not` 不走运算符表；
  - `!=` 与 `!in` 在没有显式方法时分别由 `==` 与 `in` 取反。
  设计背景见 [proposal 0002](../proposals/0002-dsl-support.md)。

## 作用域与闭包

`Environment` 是链式作用域：

- 每个块、函数调用、循环迭代都创建新的 `Environment`；
- 语义分析（`pass1.py`）为每个名字计算 `name_depth` 与 `name_index`，
  运行时直接按深度访问，避免每次线性查找；
- 函数对象保存定义时的 `Environment`，即形成闭包；
- 只在全局作用域允许重定义同名变量，局部重复定义报错；
- `val` 的不可变性在赋值时检查。

`for` 循环**每次迭代创建新的绑定环境**，因此闭包捕获的是当次迭代的值
（对应 JavaScript `let` / C# 5+ `foreach`；Python 的循环变量是共享绑定）：

```oort
var fs = []
for i in [1, 2] {
    fs = fs + [do: i]
}
print(fs[0](), fs[1]())   # 1 2
```

## 控制流

- `if` / `elif` / `else` 都是表达式；`elif` 在 AST 中降级为嵌套 `if`。
- `while`、`for` 支持 `break` / `continue`（通过内部异常实现）。
- `break value` 使循环表达式返回该值；裸 `break` 或正常结束返回 `null`。
- 块的值是最后一条语句的值；函数体返回值同理。

## 参数绑定

`ast_interpreter/signature.py` 的 `Signature` 把 `FunctionDef.params` 分为
位置限定、位置或关键字、`*args`、关键字限定、`**kwargs` 与 `&block` 六组。
`visit_call` 先按源代码顺序求值所有实参（带 `keyword` / `BLOCK` 元数据），
再由 `Signature.bind` 完成绑定：

- 默认值在绑定阶段按声明顺序求值，求值环境包含闭包与更早的参数；
  `this` 在默认值之后才写入方法调用环境。
- `*args` 构造成 Tuple，`**kwargs` 构造成 String 键 Dict。
- 尾随块在函数有 `&block` 时绑定到块参数；没有时保持位置实参行为。
- 绑定错误由 `ArgumentBindingError` 转换为 `OortTypeError`，位置取调用表达式。

原生内建函数仍走位置参数路径；`visit_call` 在进入原生函数前拒绝关键字实参。

## 内建函数与类型

`builtins.py` 注册：

- 类型对象：`Object`、`Type`、`Int`、`Float`、`String`、`Bool`、`Null`、
  `List`、`Tuple`、`Dict`、`Set`、`Function`、`Method`。
- 函数：`print`、`clock`、`type`、`super`、`len`、`range`、`str`、`repr`、
  `int`、`float`、`bool`。

这些内建函数默认接收解包后的 Python 值（`unwrap=True`），返回值再装箱；
`print`、`type`、`super`、`str`、`repr` 需要看到 Oort 对象本身，因此
`unwrap=False`。`str` / `repr` 使用对象自己的 `__str__` / `__repr__`，
容器因此输出 Oort 字面量形式。

## 未实现功能的处理

`ASTVisitor` 为每个节点提供了默认的 `visit_children`。如果解释器漏实现某个
visitor，默认行为会“穿过”节点执行子节点——这正是旧字节码后端静默出错的根源。
因此，当前策略是：

1. 解释器实现所有语法分析阶段接受的**核心**节点；
2. `Pass1Analyzer` 对未实现的特性显式报 `UnsupportedSyntax`；
3. 新增语法节点时，必须同时实现 visitor 或加入拒绝列表。

拒绝清单见 [规范：一致性矩阵](../spec/06-conformance.md)。
