# 语法宏系统设计

> 整合来源：`chat-编程语言中的语法宏`, `chat-动态语言解释器扩展`

---

## 1. 设计目标

在动态语言中实现强大的编译期元编程能力，同时保持代码可读性和可维护性。

## 2. 宏系统对比

| 语言 | 宏类型 | 特点 | 缺点 |
|------|--------|------|------|
| C | 文本宏 | 简单、强大 | 无卫生性、调试困难 |
| Lisp | 卫生宏 | 安全、强大 | 学习曲线陡 |
| Rust | Token Stream | 卫生、类型安全 | 宏规则复杂 |
| Julia | AST 宏 | 直觉、表达力强 | 宏展开顺序问题 |
| Nim | AST 宏 | 编译期 VM | 生态较小 |

## 3. Oort 宏设计

### 3.1 宏类型选择

**Token Stream 宏** 作为主要方案（Rust 风格 + `!` 标记），结合 AST 宏的 `quote`/`unquote`/`splice`（Julia 启发）。

理由：
- Token Stream 提供最佳平衡：强大且可控
- AST 宏的 quote/unquote 语法更直觉
- 默认卫生性 + 显式逃逸

### 3.2 语法

```oort
# 宏定义
macro my_macro {
    # 宏体：接收 token stream，返回 AST
}

# 宏调用
@my_macro(args)
@my_macro { block_body }
```

### 3.3 AST 宏 API

```oort
# quote/unquote/splice
macro unless {
    quote {
        if not ${condition}:
            ${body}
    }
}
```

### 3.4 卫生性

- **默认卫生**：宏内生成的标识符不会与调用者冲突
- **显式逃逸**：使用 `unhygienic { ... }` 块来有意引入标识符

## 4. 编译期计算 (comptime)

受 Zig 启发的 `comptime` 关键字：

```oort
# 编译期执行
comptime {
    var table = generate_lookup_table()
}

# 编译期函数参数
def process(comptime N: Int) {
    var arr: Array[Int, N]
}
```

## 5. 编译器架构

### 5.1 共享 VM 原则

**"One VM, Two Contexts"**：编译器 VM 共享运行时 VM 的执行引擎。

```
┌─────────────────────────────────────┐
│           Execution Engine           │
├──────────────┬──────────────────────┤
│  运行时 VM    │  编译期 VM           │
│  (普通执行)   │  (comptime + 宏展开) │
└──────────────┴──────────────────────┘
```

### 5.2 宏展开流程

```
源代码 → 解析 → 宏展开 (定点迭代) → 语义分析 → 编译 → 执行
                ↑                              ↑
                └── 编译器 VM 执行宏代码 ──────┘
```

### 5.3 展开策略

- **定点迭代**：重复展开直到 AST 不再变化
- **循环检测**：限制最大展开次数防止无限递归
- **Arena 分配**：编译期使用 arena 内存分配
- **Gas 机制**：限制编译期计算步数

### 5.4 确定性

- 确定性哈希确保可重现编译
- 编译期随机数需 seed 可控

## 6. 解释器内部暴露

将解释器内部结构作为元编程 API 暴露：

- **AST API**：主要的元编程接口
- **Bytecode API**：字节码操作（高级用法）
- **Frame API**：栈帧内省（调试用途）

### 风险

- 版本耦合：内部 API 变更可能破坏用户宏
- 解决方案：稳定的 AST 接口 + 版本协商

## 7. 参考实现

- Rust `proc-macro` crate — Token Stream 模型
- Julia `MacroTools.jl` — AST quote/unquote
- Zig `comptime` — 编译期执行
- Nim `macros` module — AST 操作

## 8. 开放问题

1. 宏展开的错误报告如何映射回源码位置？
2. 如何处理宏的调试（宏展开后的代码可视化）？
3. 编译器插件机制？
4. 与类型检查器的交互（宏生成的代码何时参与类型检查）？
