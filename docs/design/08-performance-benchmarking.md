# 性能基准测试方法论

> 整理自项目早期的设计讨论（原始记录未纳入仓库）。

---

## 1. 测试层级

七层测试框架，从微基准到真实工作负载：

| 层级 | 名称 | 测试内容 | 示例 |
|------|------|---------|------|
| L1 | 指令级 | 单条指令执行速度 | LOAD_CONST, ADD |
| L2 | 操作级 | 基本操作序列 | 函数调用开销、属性查找 |
| L3 | 结构级 | 控制流结构 | 循环、递归、闭包 |
| L4 | 数据结构 | 容器操作 | 列表追加、字典查找 |
| L5 | 算法级 | 经典算法 | Fibonacci、排序、矩阵乘法 |
| L6 | 程序级 | 小型完整程序 | 解释器、编译器片段 |
| L7 | 工作负载 | 真实应用 | Richards、DeltaBlue |

## 2. 跨语言基准

推荐用于跨语言对比的标准测试：

| 基准 | 来源 | 测试重点 |
|------|------|---------|
| Richards | Google | 面向对象调度 |
| DeltaBlue | 约束求解器 | 方法调度 + 内联缓存 |
| spectral-norm | Shootout | 数值计算 |
| binary-trees | Shootout | 内存分配 + GC |
| fannkuch | Shootout | 数组操作 |
| n-body | Shootout | 浮点运算 |

## 3. 统计方法

### 3.1 运行要求

- **最少 30 次运行**（中心极限定理）
- 报告中位数（而非平均值，减少离群值影响）
- 几何平均用于跨基准汇总

### 3.2 环境控制

- 预热运行（前 5 次不计入）
- 关闭 CPU 频率调节
- 固定 CPU 核心
- 关闭无关进程

## 4. 当前基准测试

`benchmarks/` 使用 pytest-benchmark 覆盖微基准、宏基准、启动与内存：

| 文件 | 覆盖 |
|------|------|
| `test_micro.py` | 算术、局部变量、函数调用、属性、下标、字典 |
| `test_macro.py` | 递归、循环、方法分派 |
| `test_startup.py` | 编译器/运行时构造、空程序 |
| `test_memory.py` | Runtime 与程序的峰值内存上限 |
| `test_ast_interpreter.py` | 历史 Fibonacci 基线 |

微/宏基准由 `bench_utils.compile_program` 先完成解析、语义分析和解释器
构造，基准函数只测 `interpreter.run(ast)`；编译开销由启动/空程序基准单独
度量，避免把解析时间混入每次操作。

回归跟踪由 `.github/workflows/benchmark.yml` 在 `main` 上写入历史，并在
较基线回退 150% 时告警。运行方式、基线与 profiling 工具
（py-spy / Scalene / Memray）见
[`benchmarks/README.md`](https://github.com/fyabc/oort-lang.py/blob/main/benchmarks/README.md)。

### 扩展计划

- [x] 添加闭包创建/调用基准
- [x] 添加类实例化基准
- [x] 添加属性查找基准
- [x] 添加控制流基准 (循环、分支)
- [ ] 添加跨语言对比基准 (与 Python/Lua/Ruby)
- [ ] 增加 CI 中的机器可读阈值（当前为历史告警）

## 5. 实现语言选择

| 语言 | 适合度 | 说明 |
|------|--------|------|
| **Rust** | ⭐⭐⭐⭐⭐ | 首选，内存安全 + 性能 |
| C | ⭐⭐⭐⭐ | 传统选择，手动内存管理 |
| C++ | ⭐⭐⭐ | 强大但复杂 |
| Zig | ⭐⭐⭐⭐ | 新兴选择，简洁高效 |
