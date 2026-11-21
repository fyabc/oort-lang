# 基准结果（当前快照）

> 本文件由 `benchmarks/report.py` 从机器可读结果生成，请勿手改数字。
> 手工维护的只有 `benchmarks/history.json` 的历史里程碑元数据。
> 快照日期：2026-11-21  
> 提交：`9e0ee90`  
> 环境：AMD Ryzen 7 5800H with Radeon Graphics / Windows 11 / Python 3.12.12  
> 版本：Oort 0.4.0

本文件是 Oort **当前结果的唯一人工入口**。运行方式、统计规则与 profiling
见 [README.md](README.md)；跨语言套件的 caveat 见
[reference/README.md](reference/README.md)；长期趋势由 GitHub Actions 的
benchmark 工作流维护。

生成命令：

```bash
uv run --frozen pytest benchmarks/ -q --benchmark-json=benchmark.json
uv run --frozen python benchmarks/reference/run.py --repeat 3 --runtime oort --runtime oort-vm --runtime python --runtime node --runtime 'ruby=<path-to-ruby>' --runtime 'lua=<path-to-lua>' --json > refvm.json
uv run --frozen python benchmarks/report.py --benchmark benchmark.json --reference refvm.json
```

## 1. pytest-benchmark 当前结果

中位数；微/宏基准只测 `interpreter.run(ast)`，启动与编译构造成本单独测量。

### 微基准

| 基准 | 中位数 |
|---|---:|
| arithmetic | 0.046 ms |
| variable lookup | 0.044 ms |
| function call | 0.032 ms |
| attribute | 0.047 ms |
| index | 0.018 ms |
| dict | 0.020 ms |
| closure | 0.049 ms |
| class instantiation | 0.054 ms |

### 宏基准

| 基准 | 中位数 |
|---|---:|
| recursion fib(10) | 54.84 ms |
| recursion fib(20) | 893.3 ms |
| fibonacci (fib 10) | 11.25 ms |
| loop (1000) | 14.36 ms |
| method dispatch (1000) | 32.63 ms |

### 标准库与宿主边界

| 基准 | 中位数 |
|---|---:|
| map | 18.92 ms |
| filter | 27.34 ms |
| sorted | 2.37 ms |
| zip + enumerate | 5.25 ms |
| string join | 16.63 ms |
| host list equality projection | 2.16 ms |
| host `len` without projection | 0.031 ms |

### 迭代器

| 基准 | 中位数 |
|---|---:|
| builtin loop | 13.85 ms |
| user closure | 56.05 ms |
| infinite + break | 37.03 ms |

### 扩展方法/运算符

| 基准 | 中位数 |
|---|---:|
| member call | 54.77 ms |
| method call | 62.04 ms |
| operator call | 66.04 ms |

### 启动与编译

| 基准 | 中位数 |
|---|---:|
| compiler construction | 0.556 ms |
| empty program | 1.37 ms |
| empty program (vm) | 1.53 ms |
| runtime construction | 0.133 ms |
| HIR lowering (empty) | 0.016 ms |
| HIR lowering (fib) | 0.129 ms |
| bytecode compile (empty) | 0.016 ms |
| bytecode compile (fib) | 0.110 ms |

### 内存上限

- `Runtime` 峰值分配 < 32 MiB；
- 典型 1000 次循环程序峰值分配 < 16 MiB。

## 2. VM vs 树遍历解释器

同一 HIR 支持程序、同机、中位数：

| 基准 | 树遍历解释器 | 字节码 VM | 加速 |
|---|---:|---:|---:|
| fib(15) | 91.33 ms | 31.29 ms | **2.92×** |
| loop 10000 | 141.5 ms | 68.92 ms | **2.05×** |
| method dispatch (5000) | 164.8 ms | 114.5 ms | **1.44×** |

完整子集进入 VM 后的当前结论见下方历史表；目标与预算见
`docs/design/08-performance-benchmarking.md`。

## 3. 跨语言参考（仅手动，不进入 CI）

`exec` 为单次 workload 内部计时；`startup` 为空程序进程实际耗时：

| 运行时 | fib(20) | loop 20000 | methods 5000 | 启动 |
|---|---:|---:|---:|---:|
| Oort 树遍历 0.4.0 | 969.0 ms | 315.8 ms | 169.3 ms | 487.1 ms |
| Oort VM 0.4.0 | 324.2 ms | 128.0 ms | 127.7 ms | 525.9 ms |
| Python 3.12.12 | 1.29 ms | 1.33 ms | 0.580 ms | 44.95 ms |
| Node 24.15.0 | 0.067 ms | 0.007 ms | 0.002 ms | 51.57 ms |
| Ruby 4.0.10 | 0.559 ms | 0.323 ms | 0.273 ms | 151.3 ms |
| Lua 5.4.8 | 0.394 ms | 0.075 ms | 0.172 ms | 6.76 ms |

当前 Oort（解释器及 VM）约为 CPython 的 **96–750 倍**耗时。Node 的优化 JIT 可能折叠简单循环/字段更新，其数字只作下限；Ruby/Lua 作语境参考。

详细运行方式与 Node/JIT、Ruby/Lua 的 caveat 见
[reference/README.md](reference/README.md)。

## 4. 历史里程碑

| 日期 | 状态 | fib(15) | loop 10000 | 说明 |
|---|---|---:|---:|---|
| 2026-11-21 | VM 第一切片 | 18.74 ms（5.47×） | 76.23 ms（2.34×） | 仅标量/函数/分支/循环 |
| 2026-11-21 | 完整子集复测 | 37.83 ms（2.72×） | 95.04 ms（1.96×） | 加入集合、类、模块、ADT、参数绑定后 |
| 2026-11-22 | 0.4.0 | 34.65 ms（2.97×） | 94.19 ms（1.99×） | VM 动态子集完整（闭包/元类/super/扩展/协议） |
| 2026-11-22 | 热路径快赢 | 31.90 ms（2.88×） | 69.07 ms（2.21×） | STORE_G 快路径、惰性环境日志、循环不变量提升；loop 稳定过 2×（methods 1.35× 待调用点缓存） |
| 2026-11-22 | 属性路径优化 + 默认切 VM | 31.29 ms（2.92×） | 68.92 ms（2.05×） | get 去冗余 import/Type 检查、for_class 记忆化、动态字段直写、LOAD_K 整数快路径；methods 1.44×；默认后端切 VM（fib/loop 口径） |

第一切片数字保留用于对照，不作为当前性能承诺。每次后端/优化改动后，
应重新生成当前快照并在 `benchmarks/history.json` 追加里程碑。

## 5. 维护规则

1. 在安静机器上运行上面的三条命令，确认 benchmark 结果校验通过；
2. reference 必须跑**完整运行时集**（oort/oort-vm/python/node/ruby/lua）；跨语言表与头部生成命令都按输入 JSON 的运行时生成，漏跑会让对应行消失；
3. 只更新 `benchmarks/history.json` 中的历史里程碑元数据；
4. 当前表格由 `report.py` 生成，不要手改 RESULTS 数字；
5. 若结论跨过目标线，只在 design08/roadmap 写一句结论并链接本文件；
6. benchmark JSON、profile 与临时图表不提交仓库；长期趋势交给 CI。
