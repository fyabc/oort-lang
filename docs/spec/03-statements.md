# 语句

语句由换行或 `;` 分隔。下列形式均为语句：

```text
variableDecl
assignStmt
ifStmt
forStmt
whileStmt
expression              # 表达式语句
return / break / continue
import ...              # 仅模块顶层，见 07-modules.md
@[ ... ]                # 编译器属性，未实现
```

赋值不是表达式，不能出现在要求值的位置。

## 变量声明

```oort
var x = 1               # 可变
val y = 2               # 只读
var a, b = 1, 2         # 多目标
var p, q = [3, 4]       # 从列表解包
val z: Int = 3          # 类型标注：oort-object 忽略，oort-core 检查
```

- 声明必须初始化。
- 同一作用域内不允许重复声明同名变量（全局作用域除外）。
- 局部变量不能在自己的初始化表达式中被读取。
- 多目标声明要求右侧是长度相同的元组或列表。
- `val` 绑定不可重新赋值，但对象内容（如列表元素）不受限制。
- 类型标注在 `oort-object` 中只作为文档；在 `oort-core` 薄探针中会检查，
  且只支持单目标、`Int`/`Bool` 变量标注（`Unit` 仅用于函数返回）。
  详见 [11-core-probe.md](11-core-probe.md)。

## 赋值

```oort
x = 1
a, b = b, a
obj.field = 3
items[0] = 9
x += 1                  # 增强赋值
```

支持的增强运算符：`+= -= *= /= //= %= **= <<= >>= &= ^= |=`。

- 元组解包要求右侧为长度相同的元组/列表。
- 增强赋值先读取左侧当前值，再计算并写回；不能用于元组目标。
- 属性赋值要求目标对象不是内建原生对象（如 `Int`、`List` 等）。

## 条件

```oort
if cond { ... }
if cond: expression
if cond { ... } else { ... }
if cond: a else b
if cond { ... } elif cond2 { ... } else: expression
```

- 条件不需要括号。
- 分支体可以是 `{ ... }` 或 `: expression`（单表达式，需与冒号同一行）。
- `else` 接受 `{ ... }`、`: expression` 或 `expression`。
- `elif` 可以换行书写。
- 整条 `if` 是表达式，值为被选中分支的值；无匹配且无 `else` 时为 `null`。

## 循环

### while

```oort
while cond {
    ...
}
```

### for

```oort
for i in iterable: print(i)
for i in iterable { ... }
for k, v in pairs { ... }
```

- `for` 支持 List、Tuple、Set、Dict（迭代键）、String（迭代字符）以及实现了
  迭代协议的值：`__iter__()` 返回一个调用后给出 `(value, valid)` 的迭代器。
  详见 [09-iterators.md](09-iterators.md)。
- `for` 流式拉取；`valid=false` 结束，`valid=true` 的 `null` 是合法元素。
- 内置容器在循环开始时快照；用户迭代器的状态由 `__iter__` 决定。
- 每次迭代创建新的变量绑定；闭包捕获的是当次迭代的值。
- 支持解包，要求元素是长度与目标数一致的元组/列表。
- `break` / `continue` 可用于 `for` 与 `while`；在其他位置使用会报错。

## 跳转

```oort
return              # 返回值 null
return expr
break               # 循环表达式返回 null
break expr          # 循环表达式返回 expr
continue
```

- `return` 只能出现在函数/方法中；`__init__` 中禁止返回值。
- `break` / `continue` 只能出现在循环中；函数边界会切断与外层循环的关系：
  循环内定义的函数里写 `break` / `continue` 会报错。
- `break expr` 使 `while` / `for` 表达式返回 `expr`；无 `break` 或裸 `break`
  时循环表达式的值为 `null`。

## 语句列表与块

```oort
{
    stmt
    stmt
}
```

块引入新的词法作用域。类体与函数体也是语句列表，但作用域规则不同，
见 [函数](04-functions.md) 与 [类](05-classes.md)。
