# 语言语法设计笔记

> 整理自项目早期的设计讨论（原始记录未纳入仓库）。

---

## 1. 形参语法设计

### 1.1 参数类型

受 Python 和 Ruby 启发，支持五种参数类型：

```oort
def f(
    pos_only: Int,        /              # 位置限定
    normal: String,                       # 普通参数
    *args: Int,                           # 可变位置参数
    kw_only: Float,                       # 关键字限定
    **kwargs: Any,                        # 可变关键字参数
    &block: Block,                        # 尾随块参数 (Ruby)
) { ... }
```

### 1.2 参数绑定顺序

五阶段参数绑定：

1. **块提取**：提取 `&block` 参数
2. **位置填充**：按顺序填充位置参数
3. **关键字匹配**：按名称匹配关键字参数
4. **默认值应用**：填充未提供的默认值
5. **类型检查**：验证类型约束

### 1.3 严格排序规则

```
pos_only / normal * kw_only **kwargs &block
```

各类型参数之间有严格的顺序要求。

## 2. 运算符重载

### 2.1 设计选择

采用 **Rust 风格 trait** 模型：

| 运算符类别 | 实现方式 | 理由 |
|-----------|---------|------|
| 对称运算 (`+`, `==`) | 自由函数 | 左右操作数地位对等 |
| 不对称/可变运算 (`+=`) | 成员函数 | 明确修改左操作数 |

### 2.2 Trait 定义

```oort
# 加法 trait
trait Add[Rhs = Self] {
    type Output
    def operator "+"(lhs: Self, rhs: Rhs) -> Output
}

# 复合赋值 trait
trait AddAssign[Rhs = Self] {
    def operator "+="(lhs: Self, rhs: Rhs)
}
```

### 2.3 引用处理

为完整支持，需要实现四种组合：
- `(value, value)` — 两个值
- `(value, &ref)` — 值 + 引用
- `(&ref, value)` — 引用 + 值
- `(&ref, &ref)` — 两个引用

### 2.4 当前实现状态

语法层面已支持（`operator "+"` 在 `funcName` 规则中），但运行时仍使用 Python 的 `operator` 模块直接计算，未走 `__op_*` 方法调度。

## 3. 导入系统

### 3.1 语法

```oort
import "module"
from "module" import name1, name2
import lazy "module"   # 显式懒加载
```

### 3.2 执行时机

**默认急切加载**：

| 阶段 | 时机 | 说明 |
|------|------|------|
| 链接/解析 | 急切 | 读取类型签名 |
| 初始化 | 默认急切 | 执行模块顶层代码 |
| 懒加载 | 可选 | `import lazy` 显式声明 |

### 3.3 类型信息可用性

**类型签名必须立即可用**，即使对于懒加载的模块。这确保类型检查的可靠性。

### 3.4 静态模块限制

- **禁止循环依赖**（必须是 DAG）
- 模块边界处建立类型包装器

## 4. 迭代器协议

### 4.1 设计选择

**`(value, has_next)` 双返回协议**，而非 Python 的 `StopIteration` 异常。

理由：
- 避免异常驱动的控制流（性能差、语义不清）
- 类型系统更友好（返回 `Tuple[T, Bool]`）
- 与 `Option<T>` 类型自然配合

### 4.2 协议定义

```oort
# 迭代器：返回 (value, has_next) 的闭包
def __iter__(self) -> () -> (T, Bool) {
    var index = 0
    return do () {
        if index < self.length:
            var val = self[index]
            index += 1
            return (val, true)
        else:
            return (null, false)
    }
}
```

### 4.3 `yield` 编译

`yield` 关键字编译为闭包状态机：

```oort
def fibonacci() {
    var a = 0, b = 1
    while true {
        yield a
        var temp = a + b
        a = b
        b = temp
    }
}
```

### 4.4 类型层级

```
Iterable<T>     — 可迭代（有 __iter__ 方法）
Iterator<T>     — 迭代器（__iter__ 的返回值）
Option<T>       — 可选值（value 或 none）
```

### 4.5 静态优化

对于已知类型，可绕过迭代器协议直接使用索引访问：

```
for i in [1, 2, 3] { ... }
# 优化为：
for i = 0; i < 3; i++ { ... }
```

### 4.6 渐进类型边界

在动态↔静态迭代器边界处需要 blame tracking，确保类型安全。

## 5. 参考

- Python 参数传递：PEP 570 (Positional-Only Parameters)
- Rust `std::ops` — 运算符 trait 设计
- Go `range-over-func` (1.23+) — 迭代器设计
- Lua 迭代器 — 闭包迭代器模型
