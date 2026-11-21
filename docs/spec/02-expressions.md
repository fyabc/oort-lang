# 表达式

## 原子表达式

```text
字面量
identifier
this
super               # 仅在方法内；super.method 访问父类成员
(a, b)              # 元组字面量
[1, 2, 3]           # 列表
{: ... :} {. ... .}
a.b                 # 属性访问
a[b]                # 下标
a[1:3]、a[::2]      # 切片
f(args)             # 调用
f(args) do ...      # 尾随 lambda
{ statements }      # 块表达式
if ... / while ... / for ...
def ... / class ... / do ...
```

## 运算符

二元运算的求值顺序为从左到右（先求左操作数，再求右操作数）。
`and` / `or` 短路：返回决定结果的操作数本身，而不强制转换为布尔值。

```oort
1 and 2     # 2
0 or 3      # 3
```

真值规则与 Python 相同：`null`、`false`、数值 0、空字符串、空容器为假；
其余为真。

比较与运算通过运算符方法调度（见下节）。内建类型的默认行为：

- 数值之间按数值比较；
- 字符串按字典序比较；
- 列表/元组按字典序比较（先逐元素，再比长度）；
- 集合按子集/超集关系比较；
- 字典没有大小比较；
- `is` / `!is` 比较对象身份，**不可重载**；
- `in` / `!in` 对容器做成员测试（字典测试键，集合测试元素）。

对不支持的类型会抛出运行期错误。

- 比较运算非结合；`a < b < c` 会报语法错误，请用 `and` 连接。
- `Bool` 不是 `Int` 的子类型：`true + true`、`true == 1` 都不成立；
  `Bool` 只支持 `==` / `!=`。
- 容器成员测试与容器相等性使用 Oort 值相等（见下节），对 `Bool` 与 `Int`
  做严格区分：`true in [1]` 与 `[true] == [1]` 都为 `false`。
- 列表/元组比较不走宿主比较：元素相等按值相等判断，元素顺序按 Oort `<`
  递归判断。混用 List 与 Tuple，或元素不可排序（如 `Bool`、Dict）时报
  `OortTypeError`。

### 容器排序

- List/Tuple：字典序；全部元素相等时较短者更小。元素相等使用值相等，
  因此 `1` 与 `1.0` 视为相等，`[1] < [1.0]` 为 `false`。
- Set：按子集/超集关系；`{. 1 .} <= {. true, 1 .}` 为 `true`，
  `{. true .} <= {. 1 .}` 为 `false`（键相等严格区分 Bool/Int）。
- Dict：不支持 `<`/`<=`/`>`/`>=`。
- 用户类通过 `def operator "<"` 等方法参与元素比较。

### 运算符重载

在类中用字符串名定义运算符方法：

```oort
class Vec {
    def __init__(x) { this.x = x }
    def operator "+"(other) { Vec(this.x + other.x) }
    def operator "=="(other) { this.x == other.x }
    def operator "-"() { Vec(0 - this.x) }
}
```

- 方法参数不含 `this`：一元运算符方法 0 个参数，二元运算符方法 1 个参数。
- 同一符号的一元与二元形式可以并存（如上例的 `-`）。
- 二元运算在**左操作数**的类型上查找方法；`in` / `!in` 在**右操作数**
  （容器）上查找。
- `!=` 默认是 `==` 结果取反；`!in` 默认是 `in` 结果取反。显式定义时以显式方法为准。
- `==` 对用户类的默认实现是对象身份比较。
- `and` / `or` 短路，`not` 使用真值规则，`is` / `!is` 使用对象身份，这些不可重载。
- 内建类型同样用这套方法表实现（记录在类型的 `operators` 表中），
  因此 `+` 在 `Int`、`String`、`List` 等类型上的行为与用户类走同一条路径。
- 没有对应方法时抛出 `OortTypeError`；方法内部抛出的 Python 类型错误会转换为
  `OortTypeError`。

类内运算符方法只能在类体内定义；顶层裸 `def operator` 与
`def class.operator` 会被拒绝。

类体中只有 `__init__` 与 `__iter__` 是运行时识别的特殊方法。其他 dunder
名字（`__str__`、`__repr__`、`__op_*__`、`__getitem__` 等）定义在类体中会报
`Special method '<name>' is not supported.`，避免看起来生效、实际从不分派。

扩展运算符可以补上目标类型没有定义的运算符，写作
`def C.operator "+"(other)`。查找顺序是类/继承/原生运算符优先，miss 后才查
当前词法作用域可见的扩展运算符；`in`、`!=`、增强赋值等规则完全相同。
详见 [扩展方法](10-extensions.md)。

## 相等与成员测试

完整设计见 [OP 0016](../proposals/0016-equality-protocol.md)。规则分为两层：

### 值相等 `==`

- List/Tuple：长度相同且逐元素 `==`；Dict：键相等且对应值 `==`；Set：
  按键相等比较元素。
- Bool 与 Int 在所有嵌套层严格区分：`[true] == [1]` 为 `false`。
- Int 与 Float 按数值比较：`1 == 1.0` 与 `[1] == [1.0]` 为 `true`。
- String 按内容；Null 只等于 Null；用户类使用其 `operator "=="`，未定义时
  按身份。
- `!=` 默认取反 `==`；显式 `operator "!="` 优先。
- 身份短路：同一对象直接相等；循环容器使用已比较对象对 memo。

### 成员测试 `in`

- List/Tuple/String：逐元素用值 `==`；`!in` 取反。
- Dict：按键查找；Set：按键相等查找。
- 用户容器可显式定义 `operator "in"` 覆盖。

### 键相等（Dict 键 / Set 元素）

- Null、Bool、Int、Float、String、Tuple（元素可哈希）按类型严格的键相等；
  Type/Function/Module/用户实例按身份。
- **Int 与 Float 是不同的键**：`1 == 1.0`，但 `{1: "x"} != {1.0: "x"}`，
  `1 in {. 1.0 .}` 为 `false`。这是 Ruby `eql?` 式的值/键分层。
- List/Dict/Set 不可哈希，不能作键或集合元素。
- 用户类自定义 `==` 不改变键身份；自定义哈希协议留待后续提案。

## 下标与切片

```oort
[1, 2, 3][1]        # 2
[1, 2, 3][-1]       # 3
"abc"[1]            # "b"
{: "a": 1 :}["a"]   # 1
[0, 1, 2, 3][1:3]   # [2, 3]
[0, 1, 2, 3][::2]   # [0, 2]
"hello"[1:]         # "ello"
```

- 下标表达式可以带多个参数（会组成元组），为未来的多维下标保留。
- 切片对 List/Tuple/String 返回同类型的新对象。
- 越界/类型错误转换为 `OortRuntimeError`。

## 属性访问

- 实例属性先查实例字段，再沿类的 MRO 查类属性；函数会绑定为方法。
- 类对象的属性先查类 MRO（返回未绑定函数），再查元类 MRO（绑定为类方法）。
- 访问不存在的属性抛出 `OortAttributeError`。

## 调用

```oort
f(1, 2)
f(x = 1)                # 关键字实参
f do(x): x + 1          # 唯一实参是 lambda，可省略实参括号
f(1) do(x): x + 1       # lambda 作为最后一个实参
f(do: $0 * 2)           # 匿名参数 lambda
f(block = do { ... })   # 按名传入块参数
```

- 实参先按源代码顺序求值，再按签名绑定；支持位置、关键字、默认值、
  `*args`、`**kwargs` 与 `&block`，详见 [函数：参数绑定](04-functions.md#参数绑定)。
- `C(...)` 创建实例：先创建对象，再调用 `__init__`。

## 块与语句表达式

块 `{ ... }` 的值是最后一条语句的值；空块的值为 `null`。
`if` 返回被选中分支的值（无匹配且无 `else` 时为 `null`）。
`while` / `for` 正常结束时为 `null`；`break expr` 时返回 `expr` 的值。

## 错误

表达式阶段可能产生：

| 异常 | 场景 |
|------|------|
| `OortNameError` | 名字未定义 |
| `OortAttributeError` | 属性不存在 |
| `OortTypeError` | 运算/调用类型不匹配、参数数量不符 |
| `OortRuntimeError` | 下标越界等其他运行期错误 |
