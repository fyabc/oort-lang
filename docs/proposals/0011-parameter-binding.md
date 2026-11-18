# OP 0011: 参数绑定（默认值、关键字实参与变长参数）

- **状态**：Implemented
- **作者**：Oort 设计讨论
- **相关**：[OP 0009](0009-expression-and-surface-cleanup.md)、
  [OP 0010](0010-token-responsibilities-and-anonymous-parameters.md)、
  [规范：函数](../spec/04-functions.md)、[规范：一致性矩阵](../spec/06-conformance.md)

## 摘要

定义 Oort 的完整参数绑定规则：位置参数、默认值、关键字实参、
位置限定 / 关键字限定参数、`*args`、`**kwargs` 与尾随块参数 `&block`。
目标是让所有用户可调用对象（`def`、lambda、方法、类构造、
`super.__init__`）共用一套确定性的绑定算法，并把所有歧义变成显式错误。

> 实现（2026-11-19）：`runtime/signature.py` 的 `Signature` 与
> `build_call_env` 已接入 `OortFunction` / `OortMethod` / `OortType`；
> `Pass1Analyzer` 已开放默认值、关键字实参和全部参数种类，并增加
> 参数顺序、默认值前向引用与调用实参布局校验。

## 现状

语法和 AST 已经预留了完整形状，但语义层基本拒绝：

- `grammars/Oort.g4` 的 `parameter` 已支持：
  - `name` / `name: Type`
  - `name = default` / `name: Type = default`
  - `*args`、`**kwargs`、`&block`
  - `/`（位置限定）与 `*`（关键字限定）标记
- `ast/nodes/declarations.py` 已有 `ParameterKind`：
  `DEFAULT`、`POS_ONLY`、`KW_ONLY`、`VAR_POS`、`VAR_KW`、`BLOCK`。
- `grammars/Oort.g4` 的 `argument` 已支持 `identifier = expression`；
  `ast/nodes/argument.py` 已有 `ArgumentKind.KEYWORD` / `BLOCK`。
- `ASTBuilder.parseParameterList` 已校验标记顺序、`**kwargs` 与块参数的位置；
  `Pass1Analyzer` 目前仍拒绝默认值、除 `DEFAULT`/`POS_ONLY` 外的参数种类
  和关键字实参。
- 解释器目前只做**位置参数精确匹配**：
  `visit_call` 检查 `len(args) == arity`，
  `OortFunction` / `OortMethod` 按 `zip(params, args)` 绑定。
- 尾随 lambda `f(...) do ...` 目前被当作最后一个位置实参；
  现有 `decorate(arg, f)` 示例依赖这一行为。

本提案实现这些预留语义，并移除对应的拒绝诊断。

## 语法回顾

```oort
def f(a, b = 1, /, c = 2, *args, d, e = 3, **kwargs, &block) {
    ...
}
```

调用：

```oort
f(1)
f(1, 2, c = 3, d = 4)
f(1, 2, 3, 4, 5, d = 6, extra = 7) do { ... }
```

- 参数列表必须带括号（OP 0009）。
- 命名实参使用 `=`（OP 0010），与默认值在语法上相同但上下文不同：
  参数列表内是默认值，调用实参列表内是命名实参。
- 解析阶段只负责形状；参数种类和绑定规则由本提案定义。

## 设计决策

| 编号 | 决策 | 选择 | 理由 |
|---|---|---|---|
| D1 | 默认值求值时机 | **每次调用时求值** | 避免可变默认值共享；支持 `b = a` 引用前面的参数 |
| D2 | `*args` 的容器 | **Tuple** | 不可变、与 Python 直觉一致；`len`/`for`/解包都已支持 |
| D3 | `**kwargs` 的容器 | **Dict（String 键）** | 与现有 Dict 和字符串键一致 |
| D4 | `&block` 缺省值 | **缺省绑定 `null`** | 尾随块是可选 DSL 糖；需要必选时由用户检查 |
| D5 | `&block` 的传入方式 | **尾随块 + `block = ...` 均可**（调研后修订） | Ruby/Kotlin/Swift 都允许显式/命名传递；尾随块只是语法糖 |
| D6 | 位置限定参数被按名传入 | **有 `**kwargs` 时捕获，否则报错**（调研后修订） | 与 PEP 570 一致；位置限定的名字可留给 `**kwargs` |
| D7 | 默认值可见范围 | **闭包 + 已绑定的更早参数**；不含 `this`、不含更晚参数 | 左到右求值，避免前向引用和实例相关默认值 |
| D8 | 原生内建函数 | **只接受位置参数** | 内建签名没有参数名；保持简单 |
| D9 | 运算符方法 | **只接受固定位置操作数**，不允许默认值/变长参数 | 运算符调用没有关键字语法 |
| D10 | 匿名 lambda | **只接受位置参数**，不支持关键字 | `$0` 没有可匹配的名字 |
| D11 | 参数顺序 | **Python 风格**：无默认值的位置参数不能跟在有默认值的位置参数之后 | 避免调用歧义 |
| D12 | 尾随块且无 `&block` | **仍作为最后一个位置实参** | 保持 `decorate(arg, f)` 与现有示例兼容 |
| D13 | 实参求值顺序 | **源代码顺序，先全部求值，再绑定** | 副作用可预测；每个实参只求值一次 |
| D14 | 默认值求值顺序 | **参数声明顺序，只求值缺失的参数** | 默认值可以引用已绑定的更早参数 |

## 跨语言调研（2026-11-19）

### 默认值求值时机与可见性

| 语言 | 求值时机 | 默认值可引用 |
|---|---|---|
| Python | **定义时一次** | 不可引用其他参数 / `self`；使用定义处作用域 |
| JavaScript | **每次调用**、左到右 | 更早参数；更晚参数处于 TDZ，访问报错；普通方法可访问 `this` |
| Kotlin | **每次调用** | 更早参数；更晚参数自 1.9 起禁止前向引用；成员函数可访问 `this`，构造器不可 |
| Scala | **每次调用**（`$default$N`） | 只能引用**更早参数列表**；同一参数列表内不能引用更早参数 |
| Ruby | **每次调用**、左到右 | 更早参数；更晚参数未定义/报错；方法默认值可访问 `self` |
| Swift | **每次调用**，且在所有显式实参之后 | 隔离求值：不能引用其他参数或 `self` |
| C++ | **每次调用**（省略时） | 函数参数不能出现在默认实参中 |
| C# | **编译期常量** | 不能引用参数 / `this` |

结论：

- **D1（调用时求值）** 是现代语言的主流（JS/Kotlin/Scala/Ruby/Swift/C++），
  只有 Python/C# 选择定义期/编译期；Oort 维持调用时求值。
- **D7（更早参数可见、更晚参数不可见）** 与 JS/Kotlin/Ruby 一致；
  Swift/C++/C# 更严格，Scala 只在跨参数列表时允许。
- `this`/`self` 在 JS/Kotlin（成员函数）/Ruby 中可见；Swift/Python/C# 不可见。
  Oort 选择**不暴露 `this`**：默认值在实例初始化之前求值，避免依赖未初始化字段
  和虚方法调用；这是有意保守的取舍。
- Kotlin/Scala/Swift 的默认值求值顺序都在显式实参之后；Oort 的
  “先求值所有实参，再按参数顺序求默认值”与 Swift 更接近。

### 块参数与尾随闭包

| 语言 | 块/尾随闭包 | 可选性 |
|---|---|---|
| Ruby | `&block` 可接字面块，也可显式 `&blk` 传递 | 缺省为 `nil`，可用 `block_given?` 检查 |
| Kotlin | 尾随 lambda 是“最后一个函数参数”的调用语法糖；也可命名/位置传递 | 靠参数默认值（如 `block: () -> Unit = {}`）或可空类型 |
| Swift | 尾随闭包是最后一个闭包参数的语法糖；也可带标签显式传递 | 靠可选类型或默认值 |
| Python | 无专门块参数 | 位置限定参数可与 `**kwargs` 共存 |

结论：

- **D4（缺省 `null`）** 与 Ruby 的 `&block` 最接近；Kotlin/Swift 需要显式
  默认值或可空类型，Oort 用 `null` 作为语言级缺省。
- **D5（是否允许 `block = ...`）** 调研后修订：Ruby/Kotlin/Swift 都允许
  显式/命名传递，尾随块只是糖；Oort 没有理由只允许尾随形式。
- **D6（位置限定 + `**kwargs`）** 调研后修订：PEP 570 明确把位置限定的名字
  留给 `**kwargs`，用于 API 演进；Oort 跟随 Python，有 `**kwargs` 时捕获，
  否则报错。

## 参数分类与合法顺序

一个签名按以下顺序分组：

1. **位置限定参数**（`/` 之前）——只能按位置传入。
2. **位置或关键字参数**——两种方式都可以。
3. **`*args` 或裸 `*` 标记**——开始关键字限定区。
4. **关键字限定参数**——只能按名传入；可以有默认值。
5. **`**kwargs`**——收集所有未匹配的关键字。
6. **`&block`**——必须是最后一个参数。

定义期校验：

- `/` 至多一次，且前面至少有一个位置参数；`/` 之后不能再出现位置限定参数。
- `*` / `*args` 至多一次；裸 `*` 后必须至少有一个关键字限定参数。
- `**kwargs` 至多一次，位于所有普通参数之后，只能被 `&block` 跟随。
- `&block` 至多一次，必须是最后一个参数。
- 参数名不能重复；`$0` 等匿名名字不能显式声明（OP 0010）。
- **位置参数区**中，只要出现了一个带默认值的参数，后续位置参数都必须有默认值；
  关键字限定参数不受此限制（允许 `*, a = 1, b`）。
- `*args` / `**kwargs` / `&block` 不能有默认值。
- 默认值表达式不能引用声明在它之后的参数；可以引用更早的参数与闭包变量。
- 运算符方法只能使用普通位置参数，不能有默认值、变长参数或块参数。

## 默认值

- **每次调用时求值**，不是定义时求值。
- 只对未提供的参数求值；按参数声明顺序，从左到右。
- 求值环境是函数的闭包，加上**已经绑定好的更早参数**；
  不包含调用者的局部变量，不包含 `this`，不包含更晚的参数。
- 默认值可以引用更早的参数（包括通过默认值得到的参数）：
  ```oort
  def f(a, b = a + 1): b
  f(3)        # 4
  f(3, 10)    # 10
  ```
- 默认值每次调用重新求值，因此 `def f(xs = []) { ... }` 不会在调用之间共享列表。
- `oort-object` 不检查默认值的类型；`oort-core` 在类型检查阶段再检查。

## 关键字实参

```oort
f(1, c = 3, d = 4)
```

规则：

- 所有实参表达式先按源代码顺序求值一次，再进入绑定阶段。
- 位置实参按位置绑定到位置参数；超出的位置实参进入 `*args`，否则报错。
- 关键字实参按名字绑定到位置或关键字参数 / 关键字限定参数。
- 位置实参不能出现在关键字实参之后（`f(a = 1, 2)` 报错）。
- 同名关键字不能重复；普通位置或关键字参数 / 关键字限定参数不能同时由位置和
  关键字提供。位置限定参数的名字可以被 `**kwargs` 单独捕获，即使它的位置槽
  已经被填充（与 Python 一致）。
- 未知关键字进入 `**kwargs`，否则报错。
- 位置限定参数不是普通关键字目标；有 `**kwargs` 时该关键字进入 `**kwargs`，
  否则报错（D6，与 Python PEP 570 一致）。
- `*args` / `**kwargs` 的参数名不是关键字目标，同名关键字会作为未知关键字处理
  （有 `**kwargs` 时收集）；`&block` 的名字可以按名传入（D5）。
- 关键字实参只对用户函数、lambda、方法、类构造和 `super.__init__` 生效；
  原生内建函数只接受位置参数。

## `*args` / `**kwargs` / `&block`

- `*args` 绑定为 **Tuple**，即使没有额外位置实参也是空 Tuple `()`。
- `**kwargs` 绑定为 **Dict**，键为 String，值为实参值；没有额外关键字时为空 Dict `{:}`。
- `&block`：
  - 可以由尾随块传入，也可以按名传入（`f(block = do: ...)`）；
  - 两者同时出现时是 `multiple values` 错误；
  - 都没有时绑定 `null`；
  - 如果函数没有 `&block`，尾随块仍然作为最后一个位置实参参与绑定，
    以保持 `decorate(arg, f)` 的行为。
- 尾随块在实参列表中位于最后；一个调用最多一个尾随块。

## 绑定算法

```
bind(signature, evaluated_args):
    provided = {}        # 参数名 -> 值
    extra_pos = []
    extra_kw = {}
    block = None
    seen_keyword = False
    pos_params = positional_only + positional_or_keyword
    pos_index = 0

    for arg in evaluated_args:
        if arg.kind == BLOCK:
            if block is not None: error("duplicate trailing block")
            block = arg.value
            continue

        if arg.keyword is None:
            if seen_keyword: error("positional argument after keyword argument")
            if pos_index < len(pos_params):
                provided[pos_params[pos_index].name] = arg.value
                pos_index += 1
            elif signature.var_pos:
                extra_pos.append(arg.value)
            else:
                error("too many positional arguments")
        else:
            seen_keyword = True
            if arg.keyword in extra_kw:
                error("duplicate keyword argument")
            if arg.keyword in signature.positional_only_names():
                # Positional-only names are not part of the named API; they may
                # be captured by `**kwargs` even if the positional slot is filled.
                if signature.var_keyword:
                    extra_kw[arg.keyword] = arg.value
                else:
                    error("positional-only argument passed by keyword")
                continue
            param = signature.keyword_target(arg.keyword)
            if param is None:
                if signature.var_keyword:
                    extra_kw[arg.keyword] = arg.value
                else:
                    error("unexpected keyword argument")
            else:
                if arg.keyword in provided:
                    error("multiple values for argument")
                provided[param.name] = arg.value

    env = Environment(outer=signature.closure)
    for param in signature.ordered_params:
        if param.kind in (POS_ONLY, POS_OR_KW, KW_ONLY):
            if param.name in provided:
                value = provided[param.name]
            elif param.default_value is not None:
                value = eval_default(param.default_value, env)
            else:
                error("missing required argument")
        elif param.kind == VAR_POS:
            value = Tuple(extra_pos)
        elif param.kind == VAR_KW:
            value = Dict(extra_kw)
        elif param.kind == BLOCK:
            if param.name in provided:
                if block is not None:
                    error("multiple values for block parameter")
                value = provided[param.name]
            else:
                value = block or null
        env.define(param.name, value)

    return env
```

要点：

- `provided` 只保存已提供的命名参数；默认值按声明顺序填充。
- 默认值环境 `env` 逐步增长，因此默认值看不到更晚的参数。
- `this` 在默认值求值之后才绑定；方法默认值不能依赖实例。
- 类构造 `C(...)` 使用 `__init__` 的签名；没有 `__init__` 时只接受零个实参。
- 绑定失败统一抛 `OortTypeError`，位置取调用表达式或具体实参的位置。

## 错误模型

| 情况 | 诊断 |
|---|---|
| 位置实参过多 | `f() takes N positional arguments but M were given` |
| 缺少必选参数 | `f() missing required argument: 'x'`（多个时列出名字） |
| 未知关键字 | `f() got an unexpected keyword argument 'z'` |
| 同一参数被位置和关键字提供 | `f() got multiple values for argument 'x'` |
| 重复关键字 | `f() got multiple values for argument 'x'` |
| 位置实参在关键字之后 | `positional argument follows keyword argument` |
| 位置限定参数按名传入，且无 `**kwargs` | `f() argument 'x' is positional-only` |
| 尾随块与 `block = ...` 同时提供 | `f() got multiple values for argument 'block'` |
| 原生函数收到关键字 | `built-in function 'print' does not accept keyword arguments` |
| 默认值引用更晚的参数 | 定义期错误：`default value of 'b' references later parameter 'c'` |
| 参数顺序非法 | 定义期错误，指出违反的规则 |
| 运算符方法带默认值/变长参数/块 | 定义期错误 |

## 与现有特性的交互

- **匿名参数**（OP 0010）：`do: $0` 等仍然只接受位置实参；
  匿名 lambda 没有名字可供关键字匹配。
- **运算符方法**：调用来自中缀/前缀表达式，只使用固定位置操作数；
  正则签名校验会拒绝默认值/变长参数/块参数。
- **类构造**：`C(...)` 绑定到 `__init__` 的签名；`super.__init__(...)`
  使用同一条绑定路径。
- **原生内建**：保持 `OortNativeFunction`/`OortNativeMethod` 的位置调用；
  `visit_call` 在进入原生函数前拒绝关键字实参。
- **尾随 lambda**：无 `&block` 时保持现有位置参数行为；
  有 `&block` 时从位置参数中取出并绑定到块参数。
- **方言**：语法共享；`oort-object` 只做动态绑定与运行期错误；
  `oort-core` 在绑定前做静态类型检查（默认值和实参类型）。

## 示例

```oort
def connect(host, port = 80, /, timeout = 30, *headers, retries, backoff = 2, **options, &block) {
    print(host, port, timeout, headers, retries, backoff, options)
    if block != null: block()
}

connect("example.com")
connect("example.com", 443)
connect("example.com", timeout = 10, retries = 3)
connect("example.com", 443, 5, "x", "y", retries = 1, color = "red") do {
    print("connected")
}
connect("example.com", retries = 1, block = do { print("connected") })
```

## 替代方案

1. **定义时求值默认值（Python 风格）**：会共享可变默认值，且无法支持
   `b = a` 引用前面的参数；放弃。
2. **`*args` 使用 List**：可变容器容易泄漏状态；Tuple 更安全。
3. **位置限定参数按名传入时一律报错**：更显式，但会阻止位置限定参数
   为 `**kwargs` 保留同名键；调研后选择与 Python PEP 570 对齐。
4. **`&block` 只接受尾随块**：更简单，但 Ruby/Kotlin/Swift 都允许显式/命名
   传递；调研后选择允许 `block = ...`，尾随块作为语法糖。
5. **按关键字重载函数**：引入重载分辨率会与动态绑定、默认值和方言隔离冲突；
   本提案只做绑定，不做重载。

## 实现计划

1. 新增 `Signature`（参数分组、合法顺序、关键字目标、默认值列表），
   在 `FunctionDef` 上惰性缓存。
2. 扩展 `parseParameterList` / `Pass1Analyzer` 的定义期校验：
   参数顺序、默认值后置、默认值前向引用、运算符方法限制。
3. 解释器 `visit_call` 求值后构建 `EvaluatedArgument` 列表，交给 `Signature.bind`；
   移除精确 arity 预检查，保留原生函数的位置调用。
4. `OortFunction` / `OortMethod` / `OortType` 统一使用绑定结果建调用环境；
   `this` 在默认值求值后绑定。
5. 原生函数：关键字实参显式拒绝；尾随块仍作为位置值传递。
6. 更新 `docs/spec/04-functions.md`、`06-conformance.md`、实现笔记、
   CHANGELOG 与示例；新增参数绑定测试与示例程序。

## 测试计划

- `def f(a, b = 2)`：省略/提供/关键字/默认值引用前面参数。
- `def f(a, b = a + 1)`：默认值引用；默认值每次调用重新求值。
- `def f(a, /, b = 1, *, c, d = 2)`：位置限定、关键字限定。
- `def f(*args, **kwargs)`：空/非空 Tuple 与 Dict；未知关键字收集。
- `def f(a, &block)`：有/无尾随块；无 `&block` 时尾随块作为位置参数。
- 错误：过多/缺失/未知/重复/位置后关键字/位置限定按名/原生关键字。
- 类构造与 `super.__init__` 的关键字和默认值。
- 匿名 lambda 只接受位置实参。
- 运算符方法拒绝默认值/变长参数/块参数。
- 定义期错误：默认值前向引用、非法参数顺序、裸 `*` 后无关键字参数。

## 未解决问题

- 默认值是否应允许引用 `*args` / `**kwargs`？本稿允许更早的变长参数，
  但不允许更晚参数与 `this`。
- `oort-core` 是否应要求默认值在编译期可求值（常量）？当前设计为调用时求值。
- 是否需要 `*` / `**` 实参展开（`f(*xs)` / `f(**d)`）？本稿不包含。
- 是否需要参数自省（`signature`、`args`、`kwargs`）？暂不提供。

## 调研来源

- Python：默认参数在定义时求值 —
  <https://docs.python.org/3/tutorial/controlflow.html#default-argument-values>；
  位置限定参数与 `**kwargs` — <https://peps.python.org/pep-0570/>
- JavaScript：默认参数求值顺序、TDZ、`this` —
  <https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Functions/Default_parameters>
- Kotlin：函数/默认参数/尾随 lambda —
  <https://kotlinlang.org/docs/functions.html>；默认参数前向引用限制 —
  <https://kotlinlang.org/docs/compatibility-guide-18.html>；成员函数默认值可访问
  `this`、构造器不可 —
  <https://skie.touchlab.co/features/default-arguments>、
  <https://stackoverflow.com/questions/46575059/calling-a-classs-method-as-default-arg-in-constructor>
- Scala：命名与默认参数（每次调用求值、跨参数列表可见）—
  <https://docs.scala-lang.org/sips/named-and-default-arguments.html>
- Ruby：默认参数左到右求值 —
  <https://bugs.ruby-lang.org/issues/8905>；调用参数文档 —
  <https://github.com/ruby/ruby/blob/master/doc/syntax/calling_methods.rdoc>；
  `&block` 缺省为 nil —
  <https://stackoverflow.com/questions/54975857/does-block-given-render-block-parameter-optional>
- Swift：默认参数隔离求值、不能引用其他参数/`self` —
  <https://forums.swift.org/t/allow-default-argument-expressions-to-reference-earlier-parameters/54602>、
  <https://stackoverflow.com/questions/75756986/how-to-have-a-default-function-parameter-referring-to-another-function-parameter>；
  尾随闭包匹配 —
  <https://github.com/swiftlang/swift/blob/main/userdocs/diagnostics/trailing-closure-matching.md>
- C++：默认实参每次调用求值、函数参数不能出现在默认实参 —
  <https://en.cppreference.com/w/cpp/language/default_arguments>
- C#：可选参数必须是编译期常量 —
  <https://learn.microsoft.com/en-us/dotnet/csharp/programming-guide/classes-and-structs/named-and-optional-arguments>
