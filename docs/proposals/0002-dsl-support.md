# OP 0002: 嵌入式 DSL 支持

- **状态**：Proposed
- **作者**：Oort 设计讨论
- **相关**：[OP 0001](0001-feature-layers-and-dialects.md)、[实现笔记 02](../implementation/02-parser.md)

## 摘要

在现有 “ANTLR + Pratt” 前端之上，补充让 Oort 能承载高表达力嵌入式 DSL 的机制：
带接收者的 lambda、DSL 作用域隔离、运算符声明、中缀函数、按名参数、
自定义字符串插值器与结果构建器。

## 动机

目前的语法对 DSL 已相当友好：

- `flattenExprList` + Pratt 使运算符优先级可动态注册；
- `do` 引导闭包，消除了 Ruby `do ... end` 与 `{}` 的绑定歧义；
- `{: :}` / `{. .}` 把数据字面量与代码块分开；
- `def operator "+"` 用字符串命名运算符，无歧义；
- `$0` 简写参数让短 lambda 更紧凑。

但缺少真正决定 DSL 体验的语义层机制：**接收者绑定**与**作用域隔离**。

## 设计

### 1. 带接收者的 lambda（最高优先级）

目标写法：

```oort
html do {
    head do { title("Page") }
}
```

而不是必须显式传 builder：

```oort
html do(h) {
    h.head do(hd) { hd.title("Page") }
}
```

两种路径：

- 类型级（Kotlin 风格）：`Builder.() -> Unit`，调用处自动注入 `this`；
- 调用处显式：`html do(builder: HtmlBuilder) { ... }`。

先实现显式版本，再做类型推导版本。

### 2. DSL 作用域隔离（`@DslMarker`）

嵌套 builder 中，内层不应看到外层同组 builder 的成员：

```oort
html do {
    body do {
        head do { ... }   # 错误：head 属于 html，不属于 body
    }
}
```

没有隔离时，作用域链会静默找到外层 `head`，产生难以调试的结构错误（Groovy/Gradle 的经典坑）。

实现：属性 `@[DslMarker("html")]` 标记 builder 类；同一 marker 的隐式接收者在内层不可见，
并给出“`head` 不能在 `body` 块内使用”的精准诊断。

### 3. 运算符声明

运行时重载调度已实现（2026-11-18）：类体中的

```oort
class Vec {
    def operator "+"(other) { ... }
    def operator "-"() { ... }
}
```

会登记到类型的方法表，内建类型使用同一套调度；`!=` / `!in` 默认由
`==` / `in` 取反。仍未实现的是**按作用域声明优先级**：

```oort
operator "<+>" : 120, left
```

- 数字优先级映射到 Pratt binding power；
- 声明需在模块作用域可见（或作为方言配置的一部分）；
- 当前用户运算符使用默认优先级（中缀 500、左结合），无法改变解析结果。

### 4. 中缀函数

`a to b`、`route "/users" to UsersController`：

- 函数显式标记 `infix` 才参与解析（Scala 3 的教训：隐式中缀易误解析）；
- Pratt 中把 `IDENTIFIER` 作为左结合中缀运算符，默认优先级 500。
- 当前实现已**关闭**隐式中缀（`a b c` 报错），等本节落地后再启用。

### 5. 按名参数（惰性）

```oort
def unless(cond: => Bool, body: => Unit) {
    if not cond { body() }
}
```

让用户能定义看起来像控制结构的 DSL。复用当前未使用的 `=>` 语法。

### 6. 自定义字符串插值器

```oort
sql"SELECT * FROM users WHERE id = $id"
```

任意标识符前缀，脱糖为对字符串上下文的调用；`f`/`r` 变为标准库内建插值器，
而不是词法特例。配合 `comptime` 可实现编译期 SQL 校验（深嵌入）。

### 7. 结果构建器（可选）

Swift `@resultBuilder` 风格：把块内语句序列转换为 builder 调用，
以支持 `if`/`else` 等结构。依赖属性系统与类型系统。

### 8. 免括号命令调用（建议不做）

Ruby/Groovy 的 `get '/users', to: '...'` 解析代价高、歧义多。
已有 `infix` 与尾随闭包，覆盖大部分场景；如果做，仅限语句起始位置并在 DSL 方言中启用。

## 正交性检查

- 与类型系统：接收者类型、按名参数、插值器都需要类型信息才能给出好诊断。
- 与类：DSL builder 就是普通类；不引入新的对象模型。
- 与 Pratt：所有语法扩展都落在运算符表/注册表中，不改 ANTLR 文法结构。

## 替代方案

1. **宏/字符串 DSL**：编译期解析字符串（深嵌入）也重要，但浅嵌入 builder 更易组合，
   两者可以并存。
2. **免括号命令调用**：风险高，暂缓。

## 实现计划（按投入产出比）

1. 属性系统 `@[...]`（当前仅有空语法）
2. 显式接收者 lambda
3. 运算符声明 + 可作用域化的 binding power 表
4. `infix` 修饰符
5. 按名参数
6. 自定义插值器
7. 结果构建器
8. `USER_OP` 空格规则（Swift 风格前缀/中缀判定）——可选

## 未解决问题

- 接收者 lambda 与现有 `this` 的交互（嵌套方法中 `this` 指向哪一层？）。
- 运算符声明的作用域与导入规则。
- 按名参数的求值次数（每次使用重新求值 vs 记忆化）。
