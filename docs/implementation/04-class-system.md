# 类系统实现

Oort 的类系统主要来自 Smalltalk / Python：类也是对象，类由元类实例化，
支持多重继承与 C3 线性化。实现位于 `ast_interpreter/objects.py`。

## 类作用域

- 类体内可以写任意语句，这些语句在类定义执行时立即执行。
- 类作用域顶层定义的函数自动成为实例方法。
- 顶层 `var` / `val` 目前不会成为类成员。按 [OP 0007](../proposals/0007-oort-object-object-model.md)，
  `oort-object` 将显式拒绝类体变量；槽变量属于 `oort-core` 静态对象模型
  （[OP 0005](../proposals/0005-type-system.md)）。
- 类属性沿类的 MRO 查找；实例方法通过 `this` 绑定到实例。
- 通过 `C.f` 访问方法得到未绑定函数；通过 `C().f` 得到绑定方法。

## 继承

```oort
class C < A, B { ... }
```

- 继承顶点为 `Object`；无基类时默认继承 `Object`。
- 多重继承使用 [C3 线性化](https://docs.python.org/3/howto/mro.html) 计算 MRO。
- 子类继承基类的方法与 `__init__`。
- `super` 从**定义当前方法的类**之后继续查找，而不是从接收者的动态类型开始：

```oort
class A { def f: 0 }
class B < A { def f: super.f() + 1 }
class C < B { def f: super.f() + 10 }
print(C().f())   # 11
```

  `OortMethod` 记录 `defining_type`，解释器执行方法时保存当前方法，
  `super` 据此确定查找起点。

## 元类

- 类–实例关系的顶点是 `Type`；`Type.type is Type`。
- 用 `class C :: M` 指定元类。
- 每个类只有一个元类；子类的元类必须是所有父类元类的共同子类，否则报错
  （与 Python 的元类冲突规则一致）。
- 没有类方法的类与父类共享元类。

### 类方法

```oort
class C {
  def class.f: print(this)
}
C.f()      # this 绑定到类对象 C
C().f()    # 也可以从实例调用（不推荐），this 仍为 C
```

- 类方法本质上是元类的方法。
- 类中定义了至少一个类方法时，会隐式创建元类 `类名#Meta`：
  - 名称：`C#Meta`
  - 父类：原有的元类
  - 类方法存放在该元类中。

例如：

```oort
class M < Type {}
class A {}
class B :: M {
  def class.f {}
}
class C < A, B {
  def class.g {}
}
```

- `C` 的 MRO 为 `[C, A, B, Object]`
- `C` 的类型为 `C#Meta`
- `C#Meta` 的 MRO 为 `[C#Meta, B#Meta, M, Type, Object]`

## 运算符方法

- 类体中的 `def operator "<sym>"` 不会进入普通方法表，而是登记到
  `OortType.operators[(符号, 操作数个数)]`。
- 一元方法（0 个参数）与二元方法（1 个参数）使用不同的键，因此 `-x` 与 `x - y`
  可以同时定义。
- 查找沿类的 MRO 进行，找到后绑定为 `OortMethod`（记录 `defining_type`）或
  `OortNativeMethod`，与普通方法调用一致。
- 语义分析阶段校验符号、参数个数与定义位置；内建类型在
  `setup_type_system` 中登记原生运算符实现。
- 详见 [规范：运算符重载](../spec/02-expressions.md#运算符重载)。

## 初始化器

```oort
class Rect {
  def __init__(w, h) {
    this.w = w
    this.h = h
  }
  def area: this.w * this.h
}
Rect(3, 4).area()   # 12
```

- 实例化使用函数调用语法，没有 `new`。
- `__init__` 在实例创建后调用；不允许在其中 `return` 值。
- 子类未定义 `__init__` 时继承父类的初始化器。

## 已知限制

- `oort-object` 的实例字段通过 `this.x = ...` 动态添加；类体变量将按 OP 0007
  被拒绝。槽变量属于 `oort-core` 静态对象模型，尚未实现。
- 扩展方法（在类外 `def C.f`）语法可解析，但尚未接入语义。
- 下标与属性重载尚未接入运算符方法表。
- 属性查找没有 `__getattr__` / `__setattr__` 等钩子。
- 类属性的赋值（`C.x = 1`）与元类方法解析的边界仍需在类型系统阶段明确。
