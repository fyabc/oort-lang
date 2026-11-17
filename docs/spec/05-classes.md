# 类

## 定义与实例化

```oort
class Point {
    def __init__(x, y) {
        this.x = x
        this.y = y
    }

    def norm2: this.x * this.x + this.y * this.y
}

val p = Point(3, 4)
print(p.norm2())     # 25
```

- 类使用函数调用语法实例化，没有 `new`。
- `__init__` 在实例创建后调用；其中不允许 `return` 值。
- 实例字段通过 `this.field = value` 创建；类体顶层的 `var`/`val` 目前不会成为字段，
  计划在 `oort-object` 中改为显式拒绝（[OP 0007](../proposals/0007-oort-object-object-model.md)）。

## 继承

```oort
class A { def f: 1 }
class B < A { def f: super.f() + 1 }
class C < A, B { }
```

- 语法为 `class Name < Base1, Base2`。
- 无基类时默认继承 `Object`。
- 支持多重继承；方法解析顺序使用 C3 线性化。不一致的继承关系报错。
- 子类继承基类的方法与 `__init__`。

## `this` 与 `super`

- `this` 在方法中绑定到接收者实例；在类方法中绑定到类对象。
- `this` 只在方法内可用，在普通函数或顶层使用会报错。
- `super` 在方法中可用，从**定义当前方法的类**之后继续查找成员：

```oort
class A { def f: 0 }
class B < A { def f: super.f() + 1 }
class C < B { def f: super.f() + 10 }
print(C().f())   # 11
```

- `super(args)` 等价于调用父类的初始化器（语法保留）。
- 访问 `super.method` 得到绑定到当前接收者的父类方法。

## 运算符方法

```oort
class Vec {
    def __init__(x) { this.x = x }
    def operator "+"(other) { Vec(this.x + other.x) }
}
```

- `def operator "<sym>"` 定义运算符方法，`this` 绑定到左操作数（一元运算时为唯一操作数）。
- 一元方法 0 个参数，二元方法 1 个参数；同一符号可同时定义两种形式。
- 方法沿线性的类 MRO 查找，因此子类可继承或覆盖基类的运算符。
- 完整调度规则见 [表达式：运算符重载](02-expressions.md#运算符重载)。

## 类方法

```oort
class Factory {
    def class.make: this()
}
```

- `def class.name` 定义类方法，`this` 为类对象。
- 类方法存放在元类上；定义类方法会隐式创建 `类名#Meta` 元类。
- 也可以通过实例调用类方法，但 `this` 仍是类对象。

## 元类

```oort
class M < Type {}
class A :: M {}
```

- `class C :: M` 指定元类。
- 类–实例关系的根是 `Type`，并且 `Type.type is Type`。
- 子类的元类必须是所有基类元类的（非严格）子类，否则报元类冲突。
- 每个类只有一个元类。

## 属性查找

实例属性查找顺序：

1. 实例字段；
2. 类的 MRO 中的类属性；函数绑定为方法；
3. 元类 MRO 中的类方法。

类对象属性查找顺序：

1. 类自身 MRO 中的类属性（方法返回未绑定函数）；
2. 元类 MRO 中的类方法（绑定到类对象）。

## 当前限制

- 槽变量属于 `oort-core` 静态对象模型，尚未实现；`oort-object` 的类体
  `var`/`val` 计划按 [OP 0007](../proposals/0007-oort-object-object-model.md)
  显式拒绝，实例字段通过 `this.x = ...` 创建。
- 扩展方法（类外定义）未接入。
- 属性钩子（`__getattr__` 等）、下标/属性重载、Trait/接口未实现。
- 类属性的修改（`C.x = ...`）规则尚未定义。
