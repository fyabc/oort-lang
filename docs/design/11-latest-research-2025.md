# 2025-2026 年语言设计前沿调研

> 网络调研结果，补充 Oort 设计决策的最新参考。

---

## 1. 渐进类型最新进展

### 学术研究
- **POPL 2025**: "Denotational Semantics of Gradual Typing using Synthetic Guarded Domain Theory" — 为渐进类型提供新的数学基础
- **Programming 2026**: "Efficient Selection of Type Annotations for Performance Improvement" — 用算法确定哪些标注能带来最佳运行时性能
- **ECOOP 2024**: "Learning Gradual Typing Performance" — 机器学习预测最优标注策略

### TypeScript (2025-2026)
- TypeScript 在 2025 年成为 GitHub 上 **#1 语言**（按贡献者数）
- TypeScript 5.9 (2025.8): `import defer` 支持
- **TypeScript 7.0 (预览)**: Go 原生编译器，编译速度 ~10x 提升
- **Differential Subtyping** (MSR): 最小化运行时检查开销，同时保持类型安全性

### Dart 3
- Sound null safety 已是生产级渐进类型 + null safety 的标杆
- 2025-2026 重点转向生态稳定化

### 对 Oort 的启示
- 研究 **Differential Subtyping** 以保持 typed/untyped 边界低成本
- ML 辅助标注选择是趋势方向

## 2. 寄存器式 VM 最新进展

### Luau (Roblox) — 2025 最活跃的寄存器式 VM
- **原生代码生成**扩展到 Android（之前仅 Windows/macOS）
- **Load-Store Propagation**: 原生代码生成复用寄存器值，跳过重载
- **新字节码指令**: `CMP_INT`, `SELECT_IF_TRUTHY`, `GET_CACHED_IMPORT` — 保持基本块线性化，消除分支
- **类型信息驱动运行时优化** — 渐进类型与 VM 的深度集成
- 每个函数 ~200 虚拟寄存器，32-bit 定长指令

### Lua 5.4 (稳定)
- 无新的 VM 架构变更
- 新增分代 GC 和 to-be-closed 变量

### 对 Oort 的启示
- **Luau 2025 是寄存器式 VM 的最前沿参考**
- 关键创新：load-store propagation、linearized basic blocks、type-driven optimization
- `--!native` pragma 模型用于选择性 JIT 编译

## 3. Rust 语言实现工具链 (2025-2026)

### 解析器
| Crate | 说明 |
|-------|------|
| **chumsky** 0.10+ | 零拷贝解析、上下文敏感、Pratt 组合子 |
| **winnow** | 自称最快的 Rust 解析器组合子库 |
| **pest** | PEG 语法文件，类似 ANTLR4 体验 |

### 代码生成 / JIT
| Crate | 说明 |
|-------|------|
| **Cranelift** | 全 Rust 代码生成后端，JIT + AOT。2025 H2 目标成为 rustc 生产级后端 |
| **inkwell** | LLVM 安全包装器 |

### 推荐栈
如果 Oort 迁移到 Rust: **chumsky/winnow** (解析) + **Cranelift** (代码生成)

## 4. 解析器替代方案

| 方案 | 算法 | 适合场景 |
|------|------|---------|
| **ANTLR4** (当前) | LL(*) | 多目标、成熟 |
| **Tree-sitter** | GLR (增量) | IDE/编辑器工具链，**不适合**编译器前端 |
| **Lark** (Python) | Earley / LALR(1) | Python 原生最佳替代，去掉 Java 依赖 |
| **pest** (Rust) | PEG | Rust 实现时的选择 |
| **chumsky** (Rust) | 组合子 | Rust 实现时的选择 |
| 手写递归下降 | 手动 | Rust 本身使用此方案 |

### 对 Oort 的启示
- 如果留在 Python: **Lark** 是最自然的 ANTLR4 替代品
- 如果迁移到 Rust: **chumsky** (组合子) 或 **pest** (PEG 语法)
- Tree-sitter 应仅用于编辑器工具链

## 5. 值表示最新研究

### 经典方案 (未变)
| 引擎 | 技术 |
|------|------|
| V8 | Tagged Pointer + 指针压缩 |
| SpiderMonkey | NaN Boxing |
| JavaScriptCore | NaN Boxing |
| LuaJIT | NaN Tagging |

### 新研究
- **Float Self-Tagging** (arXiv 2024 / ACM 2025): 在 IEEE 754 数值中嵌入类型元数据，避免堆分配。跨 4 种硬件架构验证。
- **ExBoxing** (Kannan Vijayan, 2025): 桥接 Tag Boxing 和 NaN Boxing，用 double 旋转高指数位作为低位标签。~4 bits 标签容量。
- **Extended NaN Boxing in Kotori** (2026): 扩展标准 NaN boxing 以支持更多类型标签。

### 对比
| 因素 | NaN Boxing | Tagged Pointer | Float Self-Tagging |
|------|------------|----------------|-------------------|
| Double | 原生 | 需堆装箱 | 大部分原生 |
| 整数性能 | 好 | 极佳 (Smi) | 好 |
| 实现复杂度 | 高 | 中 | 高 (新颖) |

### 对 Oort 的启示
- NaN Boxing 在浮点密集场景更实用
- Tagged Pointer 在整数密集场景更快
- Float Self-Tagging 是值得跟踪的新方向
