# 函数

## 定义

```oort
def add(a, b) { a + b }
def add(a, b): a + b
def inc(x): x + 1
def greeting: print("Hello")     # 无形参
def add(a: Int, b: Int) -> Int { a + b }
```

- `def` 后面的名字可以是普通标识符。
- **所有形参列表都必须带括号**；裸形参写法（`def f x: ...`）已移除，
  以避免 `:` 同时表示“类型标注”和“函数体”的歧义。
- 函数体可以是块 `{ ... }` 或 `: expression`。
- 返回值是函数体最后一条语句的值；`return` 可提前返回。
- `-> Type` 与形参类型标注在 `oort-object` 中只作为文档；在 `oort-core`
  薄探针中会检查（参数与返回必须标注，返回可用 `Unit`）。详见
  [11-core-probe.md](11-core-probe.md)。

支持的形参种类：位置/关键字参数、`/` 位置限定、`*` 关键字限定、`*args`、
`**kwargs` 与 `&block`。默认值和关键字实参见“参数绑定”。

## 匿名函数

```oort
val add = do(a, b) { a + b }
val inc = do(x): x + 1
val hello = do: print("Hello")
```

`do` 引导的匿名函数与 `def` 共享参数与函数体规则。
`do` 后面若带形参，必须使用括号；`do x: x + 1` 会被拒绝。

### 匿名参数

无显式参数列表的 lambda 可以用 `$0`、`$1`……作为匿名参数：

```oort
val double = do: $0 * 2
val add = do: $0 + $1
val inc = do { $0 + 1 }
apply(do: $0 * 2)
```

- 参数个数由最大下标推断；`do: $1` 接受两个参数，`$0` 也会被绑定（即使未使用）。
- 匿名参数只在最近的 lambda 内可见，嵌套 lambda 各自绑定。
- 只能用于 `do:` / `do { ... }`；`do()`、`do(x)` 与 `def` 均不允许匿名参数。
- 匿名参数不能声明类型或默认值；需要时写 `do(x: Int): ...`。
- `$0` 等名字不能作为普通变量、参数、函数名或类名声明。

## 调用与尾随闭包

```oort
add(1, 2)
repeat do { print("hi") }        # 唯一实参是 lambda：省略实参括号
map(xs) do(x): x * 2             # lambda 是最后一个实参：放在括号后
```

尾随 lambda 在语法上等价于追加一个位置实参。

## 参数绑定

```oort
def connect(host, port = 80, /, timeout = 30, *headers, retries, backoff = 2, **options, &block) {
    ...
}
```

- **默认值**在每次调用时求值，只对缺失参数求值；可以引用更早的参数，不能引用
  更晚的参数或 `this`。默认值每次调用重新求值，不共享可变对象。
- **关键字实参**使用 `=`：`f(x = 1)`。位置实参必须在关键字实参之前；
  同一参数不能同时由位置和关键字提供。
- `/` 之前的参数是**位置限定**的，不能按名传入；如果存在 `**kwargs`，
  同名关键字会被 `**kwargs` 捕获（与 Python 一致），否则报错。
- `*args` 收集额外位置实参，绑定为 Tuple；`**kwargs` 收集未知关键字，
  绑定为 String 键的 Dict。
- `*` 之后是**关键字限定**参数，只能按名传入；可以有默认值，也可以必选。
- `&block` 是尾随块参数：可由尾随 lambda 或 `block = ...` 提供，
  两者同时出现时报重复绑定；没有提供时绑定 `null`。
- 函数没有 `&block` 时，尾随 lambda 仍作为最后一个位置实参参与绑定。
- 原生内建函数只接受位置实参。
- 参数本身是新的绑定，函数内可重新赋值；调用实参先按源代码顺序求值一次，
  再进行绑定。

## 闭包

函数对象捕获定义处的作用域，形成闭包：

```oort
def make_counter {
    var i = 0
    do {
        i += 1
        i
    }
}
val c = make_counter()
print(c(), c(), c())    # 1 2 3
```

- 闭包捕获的是**变量绑定**，不是值的拷贝；多个闭包共享同一绑定。
- `for` 循环每次迭代创建新绑定，因此各次迭代的闭包互不影响。
- 全局变量按名字在运行时解析。

## 递归

函数在定义时即被绑定，因此可以递归调用自身：

```oort
def fib(n) {
    if n <= 1: return n
    fib(n - 1) + fib(n - 2)
}
```

## 方法与类方法

- 在类体顶层定义的 `def` 自动成为实例方法（`this` 绑定到实例）。
- `def class.f` 定义类方法（`this` 绑定到类对象），详见 [类](05-classes.md)。
  `def class.f` 只能出现在类体内；在其他位置会被拒绝。
- 扩展方法在类外定义：`def C.f(...) { ... }`，按词法作用域生效，详见
  [扩展方法](10-extensions.md)。
- 运算符方法（`def operator "+"(other)`）是类体中的特殊方法，见
  [表达式：运算符重载](02-expressions.md#运算符重载)；扩展运算符写作
  `def C.operator "+"(other)`，同样见 [扩展方法](10-extensions.md)。
