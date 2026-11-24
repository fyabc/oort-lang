# OP 0032: `oort-core` 的可排序契约、List 拼接/字典序与 `sorted`

- **状态**：Implemented（C5a–C5c）
- **作者**：Oort 设计讨论
- **创建日期**：2026-11-25
- **相关**：[OP 0031](0031-core-collection-surface.md)、[spec 11](../spec/11-core-probe.md)、
  [spec 14](../spec/14-typed-bytecode.md)、[design 15](../design/15-typed-ir.md)

## 摘要

动态方言已有 `sorted`、List/Tuple `+` 与字典序比较；`oort-core` 因缺少
“可排序”契约一直没有开放这些能力（OP 0031 的 C5）。本提案先定义一个
**内建可排序类型集合**（`Int`、`Float`、`String`），在此之上补齐：

- `List[T] + List[T]`（拼接，任意 `T`）；
- `List[T]` 的字典序 `< <= > >=`（`T` 可排序）；
- `sorted(xs: List[T]) -> List[T]`（`T` 可排序，稳定升序，返回新列表）。

自定义类型的排序（ADT、类、接口）留给类型系统出现 bound/trait 之后；
`key`/比较函数参数留给回调边界（B3）。

## 动机

动态侧的行为已经存在：

- `sorted(xs)` 按元素 `<` 排序，可选 `key`/`reverse`；
- List/Tuple `+` 生成新序列；`<` 按字典序逐元素比较，再比较长度。

core 的类型检查器目前只允许数值与 String 排序、只允许数值 `+`，因此
`List[Int] + List[Int]`、`[1, 2] < [1, 3]`、`sorted([3, 1, 2])` 都无法表达。
把“动态已有但 core 没有”的能力补齐，是 OP 0031 的既定方向；难点不在
实现，而在**排序约束如何静态表达**。没有泛型函数与 bound 之前，内建封闭
集合是最小的可信契约。

## 设计

### D1：内建可排序集合（初始契约）

```text
orderable(T) ::= T = Int | Float | String
```

- `Bool` 不参与排序（core 的 `Bool` 目前只有相等/逻辑运算）；需要时单独
  提案，避免把“真值顺序”偷偷引入。
- ADT/类/接口/容器元素不在初始集合；动态侧可运行时比较，core 不承诺。
- 该集合是**封闭**的：编译器据元素类型直接判定，不需要用户声明。
- 未来引入 bound/trait（例如 `Ord`）时，可把它扩展为用户类型；内建集合
  成为预定义实现。

### D2：List 拼接

- `List[T] + List[T] -> List[T]`，两侧元素类型必须相同；
- 结果为新列表；元素是运行时值（引用/不可变标量），不复制内部结构；
- 不修改操作数；`List[ADT]`、`List[List[Int]]` 等任意 `T` 均可拼接。

### D3：List 字典序比较

- `List[T] < <= > >= List[T]`，要求同一 `T` 且 `orderable(T)`；
- 语义与动态一致：逐元素比较，先按值相等跳过公共前缀，再比较第一个
  不同元素；公共前缀相同时较短者更小；
- 元素相等使用 typed 值相等；元素先后使用 `<`（数值精确、String 字典序）；
- 结果 `Bool`；不引入全序之外的隐式规则。

### D4：`sorted`

```oort
sorted(xs: List[T]) -> List[T]   # orderable(T)
```

- 接受 `List[T]`，返回新 `List[T]`，**稳定升序**；
- 不改变实参；
- 第一切片不支持 `key`/`reverse`：
  - `key` 需要跨 VM 回调（typed native → typed 函数），属于 B3 边界能力；
  - `reverse` 可以后加为第二位置参数，但为保持语义一致（动态签名是
    `sorted(xs, key, reverse)`），先不引入位置歧义。
- 只接受 List（不接受 Set/Dict/String/迭代器），编译期拒绝。

### D5：实现

- 新操作码：
  - `CMP_LIST`（A=目标 Int，B=左，C=右）返回 `-1/0/1`；
  - `LIST_CONCAT`（A=目标，B=左，C=右）返回新 List；
  - List 的四个比较由 `CMP_LIST` + `LOAD_K 0` + 既有 `*_I` 比较组合，
    不新增 4 个布尔 opcode；
- `sorted` 作为 native（`print`/`len` 同类）：
  - Python typed VM 复用动态 builtin 的稳定排序与 `<` 语义；
  - Rust typed VM 增加 `TypedNative::Sorted`，用标量比较器排序，未知元素
    类型显式报错；
- 版本提升：kind=1 **v10**、artifact **v12**、linked bundle **v5**；
  缓存按版本自然失效。

## 与其他语言对照

| 语言/系统 | 排序约束 | 自定义类型 | 备注 |
|---|---|---|---|
| Rust | `Ord`/`PartialOrd` trait | 实现 trait | `sort` 稳定、`sort_unstable` 快 |
| Haskell | `Ord` typeclass | 实例化 | `sort` 稳定 |
| Swift | `Comparable` 协议 | 遵循协议 | `sorted()` 稳定 |
| Java | `Comparable<T>` / `Comparator` | 实现接口 | `List.sort` 稳定 |
| Go 1.21+ | `cmp.Ordered` 约束 | 用 `cmp.Compare`/自定义 | `slices.Sort` 不稳定，`SortStableFunc` 稳定 |
| C++20 | `std::totally_ordered` concept | concept 约束 | `stable_sort` 显式 |
| Python | 运行时 `__lt__`（鸭子类型） | 自定义 `__lt__` | `sorted` 稳定 |
| Kotlin | `Comparable` 接口 | 实现接口 | `sorted()` 稳定 |

结论：成熟语言都把“可排序”放在类型系统里（trait/接口/concept），而
动态语言靠运行时协议。Oort core 还没有泛型函数的 bound，因此先用**封闭
内建集合**，语义与 Python 的标量部分一致；等 bound 落地后升级为
`Ord` 契约，内建集合成为预定义实现，List 的字典序与 `sorted` 只依赖
“元素可排序”，无需改调用点。

## 替代方案

1. **现在就引入 `Ord` 接口/bound**：需要泛型函数与约束求解，范围过大；
   接口目前是类方法契约，不能约束任意 `T`。
2. **运行时鸭子类型**：core 是静态方言，会把错误推迟到运行期，违背
   “编译期显式拒绝”的原则。
3. **只做 `sorted(xs, cmp)`**：比较函数需要 typed native 回调 typed VM
   （跨执行器重入），且动态侧没有 `cmp` 参数；留待 B3。
4. **先做 `reverse`**：位置参数与动态 `sorted(xs, key, reverse)` 冲突，
   推迟到 key 一起设计。

## 向后兼容

- 只扩展 core 表面；动态方言行为不变；
- 新 opcode 提升 kind=1 版本，旧 artifact 显式拒绝，缓存自然 miss；
- 既有 `List` 相等/成员/切片不受影响。

## 实现计划

| 阶段 | 内容 | 验收 |
|---|---|---|
| C5a（已实现） | List `+`、`LIST_CONCAT` | 与动态一致；元素类型不同的 List 拒绝 |
| C5b（已实现） | List 字典序比较、`CMP_LIST` | 公共前缀/长度/空列表/嵌套值覆盖；非可排序元素拒绝 |
| C5c（已实现） | `sorted(xs)` native + Rust 实现 | 稳定升序；与动态一致；非 List/非可排序元素拒绝 |
| 后续 | `key`/`reverse`、ADT/类排序、嵌套容器排序、`Ord` bound | 依赖 B3/泛型 |

## 未解决问题

- `Bool` 是否需要排序（Map 到 0/1）？
- `sorted` 是否应保证稳定性为语言契约（本提案按“是”处理）？
- NaN 在 List 比较/排序中的位置：当前按“与任何值都不小于”的相等跳过，
  等价于稳定插入；是否要显式定义？
- 自定义类型排序是走接口（`Ord`）还是显式比较函数？
- 嵌套 List（`List[List[Int]]`）的递归可排序是否开放？
