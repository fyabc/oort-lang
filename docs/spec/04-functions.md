# 函数

## 定义

```oort
def add(a, b) { a + b }
def add(a, b): a + b
def inc x: x + 1                 # 单个形参可省略括号
def greeting: print("Hello")     # 无形参
def add(a: Int, b: Int) -> Int { a + b }
```

- `def` 后面的名字可以是普通标识符。
- 形参列表为空或只有一个形参时可省略括号。
- 函数体可以是块 `{ ... }` 或 `: expression`。
- 返回值是函数体最后一条语句的值；`return` 可提前返回。
- `-> Type` 与形参类型标注会被解析，但当前不参与检查。

当前支持的形参种类：普通位置参数，以及 `/` 之前的位置限定参数。
默认值、`*args`、`**kwargs`、仅关键字参数、尾随块参数在语义分析阶段会被拒绝。

## 匿名函数

```oort
val add = do (a, b) { a + b }
val inc = do x: x + 1
val hello = do: print("Hello")
```

`do` 引导的匿名函数与 `def` 共享参数与函数体规则。
`$0`、`$1` 等匿名形参尚未实现。

## 调用与尾随闭包

```oort
add(1, 2)
repeat do { print("hi") }        # 唯一实参是 lambda：省略括号
map(xs) do x: x * 2              # lambda 是最后一个实参：放在括号后
```

尾随 lambda 在语法上等价于追加一个位置实参。

## 参数绑定

- 实参按位置绑定，数量必须精确匹配。
- 不支持关键字实参与默认值（显式报错）。
- 参数本身是新的绑定，函数内可重新赋值。

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
def fib n {
    if n <= 1: return n
    fib(n - 1) + fib(n - 2)
}
```

## 方法与类方法

- 在类体顶层定义的 `def` 自动成为实例方法（`this` 绑定到实例）。
- `def class.f` 定义类方法（`this` 绑定到类对象），详见 [类](05-classes.md)。
- 扩展方法（在类外 `def C.f`）与运算符函数（`def operator "+"`）语法可解析，
  但尚未接入语义，会被拒绝或按普通函数处理。
