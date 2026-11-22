# 类型化 ADT 设计（S4）

> **状态**：设计草案 + **S4a/S4b 原型**（2026-11-23）。单态与泛型 ADT（含
> prelude `Option`）已进入 typed HIR / kind=1 v6 / Python typed VM / Rust typed
> VM；泛型实例类型参数已保留，字面量/Tuple/或模式已支持。**不改变语言表面**。
>
> 关联：[design 15](15-typed-ir.md) 的 S4 扩展；[design 03](03-type-system-design.md)
> 的泛型表示；[design 14](14-core-typechecking.md) 的 ADT 检查；[spec 14](../spec/14-typed-bytecode.md)
> 的 typed 字节码格式；[design 16](16-numeric-semantics.md) 的值相等语义。

## 1. 目标与范围

### 1.1 目标

让以下 `oort-core` 程序在 typed 路径上运行，并与 `-t vm` 输出一致：

```oort
#lang oort-core

enum Shape {
    Circle(radius: Int),
    Rect(width: Int, height: Int),
    Empty,
}

def area(shape: Shape) -> Int {
    match shape {
        Circle(r) => r * r * 3,
        Rect(w, h) => w * h,
        Empty => 0,
    }
}

print(area(Circle(2)))
print(area(Rect(3, 4)) == 12)
```

具体要求：

- 名义 ADT 类型、构造器、载荷；
- `match` 与构造器/通配/变量/嵌套模式；
- ADT 结构相等与打印；
- 递归 ADT（如 `Tree`）；
- 与 Python typed VM、Rust typed VM 的差分；
- `.obc` 序列化 round-trip。

### 1.2 非目标

- 不实现类、接口、typed 闭包、函数值跨 ADT；
- 不在 S4 做跨模块 ADT（module import 仍被 typed 子集拒绝）；
- 不改变 `match` 的穷尽性规则；
- 不做决策树/跳转表优化（先线性匹配，后优化）；
- 不承诺内存布局 ABI；初始载荷是 boxed 值的数组；
- 不引入 GC（见 §7）。

## 2. 现状与约束

### 2.1 `oort-core` 已有语义

- `enum E[T]` 是名义泛型 ADT；支持声明处变型、内建 `Option`/`Result`；
- 构造器可带载荷；模式支持构造器、字面量、Tuple、或模式、守卫；
- 检查器已做穷尽性检查；ADT 使用结构相等；
- 运行时 `OortADT` 保存 `type`、`variant`（构造器名）与 `values`；
- 擦除式 HIR 用 `BuildEnum` 建立类型/构造器，用 `Match` 的 arm 函数执行匹配。

### 2.2 typed 路径现状

- S4a 之前 `IrTypeLike = IrType | ContainerType`，没有名义类型；
- S4a 之前 `lower_typed_module` 拒绝 `EnumDef`/`Match`；
- S4a 之前 kind=1 类型表是每 proto 的后序表（v4，tag 1–11）；
- kind=1 没有全局存储；函数通过 `DEF_FUN`/`LOAD_G` 绑定；
- Python typed VM 是 boxed baseline，Rust typed VM 使用未装箱标量 + `Rc` 容器；
- typed 路径仍单模块，prelude 的 synthetic enum 被跳过。

这些约束决定了 S4 的主要设计点不是“再加一个值类型”，而是：

1. 名义类型如何进入类型表；
2. 构造器如何在不引入全局存储的前提下表示；
3. `Match` 如何绕过现有 arm 函数而保持模式语义；
4. 泛型实例如何在不同 proto 间保持同一身份。

## 3. 先行研究

| 系统 | ADT 表示 | 匹配实现 | 对 Oort 的启示 |
|---|---|---|---|
| **Rust enum** | 单态化后的判别式 + union；可做 niche 优化 | 编译为 switch/决策树 | 静态身份 + 单态化布局是长期目标 |
| **Swift enum** | 名义 enum，载荷内联，`indirect` 处理递归 | 编译为分支/跳转 | 递归与载荷布局必须显式设计 |
| **OCaml variant** | 统一 block：tag + 字段；多态不单态化 | 子句匹配/决策树 | 统一 tagged payload 是最简单的起点 |
| **Haskell ADT** | lifted constructors，info table；统一堆对象 | 模式匹配编译 | 不必第一步就为每个 ADT 生成专用布局 |
| **Java sealed interface** | 引用对象，名义类型，无载荷内联 | `instanceof`/switch | 名义身份与运行时类型检查可以分离 |
| **C++ `std::variant`** | 库级 tagged union | `visit` | 判别式 + payload 足以表达语义 |

**提炼**：S4 先采用“名义声明 + 统一 tagged payload”的保守布局，与
OCaml/`std::variant` 接近；单态化、niche、决策树留到 S4c 性能阶段。类型身份
必须来自声明的 `(origin, name)`，不能只把构造器名当字符串比较。

## 4. 类型模型

### 4.1 名义 ADT 类型

typed 路径新增：

```python
@dataclass(frozen=True)
class AdtType:
    origin: str          # 模块 origin，prelude 为 <core-prelude>
    name: str            # enum 名
    args: tuple[IrTypeLike, ...] = ()
```

`IrTypeLike = IrType | ContainerType | AdtType`。

- 相等性：`origin` + `name` + `args` 结构相等；
- 类型表去重键相同；
- 单态 enum 是 `args=()` 的特例；
- 构造器载荷类型从检查器的 `ConstructorInfo` 读取，typed lowering 不重新推断。

### 4.2 模块级声明表

ADT 是模块级声明，构造器 ID 必须跨 proto 稳定，因此不能继续只放在每 proto
类型表里。kind=1 v6 增加模块头：

```text
u32 adt_decl_count
adt_decl[adt_decl_count]:
  string origin
  string name
  u16    ctor_count
  ctor[ctor_count]:
    string name
    u8     arity
```

- `adt_decl_id` 是模块内稳定索引；
- 构造器 ID 可以是 `(decl_id, ctor_index)`，加载时展开；
- 载荷的具体类型不在模块头重复：`AdtType` 的类型参数与检查器元数据已经足够；
- 名字/arity 只用于运行时构造、打印和边界守卫；不用于重新类型检查。

### 4.3 类型表 tag

S4a（单态）在每 proto 类型表新增：

```text
tag 12: AdtDeclRef
  u16 adt_decl_id
```

S4b 支持类型参数：

```text
AdtType(origin, name, args)
```

类型表 tag 12 写入 `u16 adt_decl_id, u16 arg_count, u16 arg_type_id[]`；运行时
ADT 值保存具体实例类型（decl + args），用于守卫与相等。格式版本提升为 **v6**。

## 5. 构造器与值

### 5.1 构造器调用的 lowering

现有擦除路径通过 `BuildEnum` 把构造器绑定为全局值，再用 `Call` 调用。typed
路径没有全局存储，且构造器不是普通用户函数。typed lowerer 识别“目标为构造器
的直接调用”，生成：

```text
NEW_ADT  A=payload 窗口基址, B=构造器 ID, C=目标寄存器
```

- 载荷按声明顺序连续搬入窗口，和 `NEW_LIST`/`NEW_DICT` 的窗口约定一致；
- 载荷个数由模块声明表的 `arity` 决定，因此不需要额外的 count 操作数；
- 空载荷构造器直接 `NEW_ADT A=0, B=ctor, C=dst`；
- 构造器作为一等函数值仍显式拒绝（typed 路径本来就不支持函数值）。

这避免为构造器新增全局表，也不改变擦除路径。

### 5.2 运行时值

初始布局采用**统一 tagged payload**：

```rust
struct TypedAdt {
    decl_id: u16,
    variant: u16,
    payload: Box<[TypedValue]>,
}
```

- Python typed VM 复用 `OortADT`，保持打印和相等语义；
- Rust 使用 `Rc<TypedAdt>`；
- 载荷元素是 `TypedValue`，暂不单态化内联；
- 空载荷构造器仍分配一个小的 ADT 值，不等同于 `Unit`；
- ADT 值不可变；递归 ADT 的有限树不会形成环。

S4c 再评估按声明/实例生成专用 Rust enum、内联标量载荷或 niche 优化。

## 6. 匹配

### 6.1 不让 typed 路径复用 arm 函数

共享 HIR 的 `Match` 把每个 arm 降低为带绑定的函数，再由 VM 调用。这适合擦除
路径，但 typed 路径没有 typed 闭包/函数值，且 arm 参数类型需要从 scrutinee
反推。S4 建议 typed lowerer **单独降低 match**：

1. 校验 scrutinee 的静态类型是 ADT（或后续 Tuple/字面量）；
2. 按声明顺序生成构造器测试和字段提取；
3. 绑定通过 `MOVE` 写入 arm 的局部槽；
4. 守卫在绑定后求值；
5. 无匹配时报告运行时“non-exhaustive match”错误。

新增 typed 指令：

```text
ADT_TAG   A=目标 Int, B=ADT 值, C=0
ADT_FIELD A=目标, B=ADT 值, C=字段索引
```

`ADT_TAG` 返回变体索引；`ADT_FIELD` 越界/错误变体必须显式报错。构造器模式
编译成：

```text
ADT_TAG   tag, value
JMP_IF_NE tag, CtorIndex, next_arm
ADT_FIELD field0, value, 0
...绑定...
...arm body...
JMP end
```

S4a 支持：

- 通配 `_`、变量绑定；
- 构造器模式（可嵌套）；
- 空载荷/带载荷构造器；
- arm 守卫（布尔表达式）。

S4b 已支持：

- 字面量/Tuple/或模式与嵌套组合；
- 泛型 ADT 的载荷；
- ADT/Int/Float/Bool/String/Tuple scrutinee。

`match` 的穷尽性仍由 core 检查器负责；typed 路径只消费检查结果，不重新检查。

### 6.2 后续优化

S4c 已把同一 match 内重复的 `ADT_TAG` 提取缓存到临时寄存器。决策树/跳转表和
单态布局尚未实现：当前线性测试 + tag 缓存足够支撑语义验证，性能优化应等
ADT 基准出现明确热点后再做，避免过早绑定布局 ABI。

## 7. 相等、打印与 GC

- **相等**：名义 `(origin, name, args)` + 变体 + 载荷递归 `typed_equal`；
  与动态 `values_equal` 对齐；
- **打印**：`Ctor` 或 `Ctor(v0, v1)`，空载荷不打印括号，和 `OortADT.__str__`
  一致；
- **GC**：S4 的 ADT 值不可变，递归 ADT 是由已求值构造器组成的有限树；
  `Rc`/`RefCell` 足够，不引入 tracing GC。若后续允许 ADT 持有可变 List/类实例
  或 typed 闭包，必须与 Rust VM v2/design 01 一起重新评估环回收。

## 8. 序列化与兼容性

- kind=1 版本提升为 **v6**；
- 文件头增加模块级 ADT 声明表，再写 functions/main；
- 每 proto 类型表新增 tag 12；
- 新 opcode：`NEW_ADT`、`ADT_TAG`、`ADT_FIELD`、`EQ_ADT`、`NE_ADT`；
- 旧读者遇到 v6/未知 opcode/tag 必须显式拒绝；
- 不改变 kind=0 格式；
- 单模块 S4a 不涉及跨模块 origin；v6 预留 `origin` 字段，跨模块 ADT 在 B2/
  后续扩展中启用。

## 9. 里程碑

| 阶段 | 范围 | 退出条件 |
|---|---|---|
| **S4a 单态 ADT** | 模块声明表；构造器；同构/递归单态 enum；`NEW_ADT`/`ADT_TAG`/`ADT_FIELD`；构造器/通配/变量/守卫匹配；相等/打印 | 示例与差分通过；round-trip；Rust 一致 |
| **S4b 泛型 ADT** | `Option`/`Result`、泛型载荷、reified 实例类型参数、字面量/Tuple/或模式 | **已完成（原型）** |
| **S4c 优化** | 已做 match tag 缓存；决策树/跳转表、单态布局、标量载荷内联待基准证明 | **部分完成**；暂不引入布局 ABI |

S4a 的实现顺序：

1. 类型模型 + 模块声明表 + v6 序列化；
2. typed HIR 识别 `EnumDef`/构造器调用/match；
3. Python typed VM 的构造/匹配/相等/打印；
4. Rust typed VM 同步；
5. `-t tvm` vs `-t vm`、Rust 差分、round-trip、示例。

## 10. 风险与开放问题

1. **构造器识别**：检查器是否保留构造器调用与普通函数的明确区别？typed
   lowerer 不能靠名字猜测。
2. **match arm 函数 vs 内联 lowering**：本文倾向前者不用、typed 专用 lowering；
   需要确认共享 HIR 的 arm 元数据不会丢失绑定顺序。
3. **泛型实例身份**：S4b 是否采用模块级 instance 表/单态化，还是运行时携带
   类型参数；这会影响 `.obc` 和相等性。
4. **递归声明**：`Tree` 的载荷引用自身，类型表/声明表必须允许非类型表的
   自我引用，不能沿用容器类型的“后序无环”规则。
5. **跨模块 origin**：`m.Type` 的运行时身份与导出/导入；S4a 先限定单模块。
6. **prelude**：`Option`/`Result` 的 synthetic enum 如何进入模块声明表，
   以及是否在 S4a 就支持。
7. **GC**：当前 ADT 不可变无环；一旦 ADT 可持有可变的 List/类实例，环可能出现。
8. **ABI/性能**：统一 payload 是语义优先方案；S4c 的专用布局需要重新评估
   `.obc` 是否携带布局元数据。

## 11. S4a 实现状态（2026-11-23）

已实现：

- `AdtType(origin, name)` 进入 `IrTypeLike`；S4a 使用固定 origin
  `"<typed-module>"`（跨模块身份留 B2）；
- 模块级 `AdtDecl`/`AdtConstructor` 表；kind=1 **v6** 文件头写入 origin/
  name/构造器名/arity；
- typed HIR 新增 `BuildAdt`/`AdtTag`/`AdtField`；`EnumDef` 不再写入 main，
  构造器直接调用/空载荷引用会转成 `BuildAdt`；
- typed `match` 专用 lowering：构造器/通配/变量/嵌套构造器模式 + 守卫；
  字面量/Tuple/或模式仍显式拒绝；
- opcode 75–79：`NEW_ADT`/`ADT_TAG`/`ADT_FIELD`/`EQ_ADT`/`NE_ADT`；
- Python typed VM 复用 `OortADT`/`OortType`；Rust 使用 `TypedValue::Adt` +
  `TypedAdt`；相等、打印、递归 ADT 与主结果转换已对齐；
- 验收：`examples/08_core/08_18_typed_adts.ort`、typed 单测、OBC round-trip、
  Rust differential `typed_adts`。

已知限制：

- 只支持单态 enum；`Option`/`Result` 等泛型构造器仍拒绝；
- `AdtField` 的校验按字段索引放宽（同一索引在不同构造器可有不同类型）；
- 序列化不保存构造器 payload 类型，只保存 arity；读取后的 `.obc` 用于执行，
  不用于重新类型检查；
- 无跨模块 ADT、无类/接口/typed 闭包、无 GC 变更。

## 11.1 S4b 实现状态（2026-11-23）

已实现：

- `AdtType.args` 进入静态 typed 类型；用户泛型 enum 与 prelude `Option` 可用；
- 泛型构造器类型实参由检查器的期望类型/实参推断，typed lowerer 读取检查结果；
- `match` 的 payload 类型通过 `substitute` 从实例类型参数得到；
- prelude `Option`/`Result` 的 synthetic enum 进入模块 ADT 声明表；
- Rust/Python typed VM 使用相同的构造器/标签/payload 执行路径；
- 验收：`examples/08_core/08_19_typed_generic_adts.ort`、typed 单测、
  differential `typed_generic_adts`。

S4b 原型的限制与备注：

- 运行时 ADT 值携带 `AdtType` 实例身份（decl + args），守卫/相等可区分
  `Option[Int]` 与 `Option[String]`；
- v6 类型表 tag 12 保存参数列表；反汇编/round-trip 保留实例参数；
- 字面量/Tuple/或模式已实现；`TupleItem` 提供静态 Tuple 字段读取；
- prelude 的 Option/Result 声明会出现在每个 typed 模块的声明表中；
- `AdtField` 对泛型字段仍做宽松校验（字段 payload 模板不写入声明表）；
- 跨模块 ADT、边界转换仍留后续。

## 11.2 P1 类型化模块链接（2026-11-23）

第一个 P1 切片支持 core→core 的 `from "./lib" import f` 和
`import "./lib"` 的函数访问：

- 链接器（`hir/typed_link.py`）递归加载依赖、独立 lowering，然后把函数和
  ADT 声明合并成一个 `TypedModule`；
- 导入模块的构造器 ID 重映射到合并后的模块声明表；root 函数保持在前，
  使入口 main 的 `DefineFunction` 索引不变；
- 生成的 kind=1 `.obc` 是已链接的单模块，Rust typed VM 无需多模块加载器；
- B1 导入的 core 模块也可以继续 `from` 导入其他 core 模块。

当前限制：

- 支持 `from ... import` 函数和 namespace import 的函数访问；
  导入构造器仍未开放；导入类型可用于类型注解（如 `lib.Color`）；
- 导入模块不能有顶层副作用（只允许函数定义和 Unit 初始化）；
- 跨模块函数名冲突显式拒绝；不做模块前缀/重导出；
- root 可以使用 imported type 写标注（如 `lib.Color`），但不能构造/匹配
  导入 ADT 的构造器；导入 ADT 值仍主要通过函数返回值/参数获得。

## 12. 推荐决策

- **先 S4a 单态 ADT**，把名义身份、构造、匹配、相等、打印和 v6 格式跑通；
- **类型身份用 `(origin, name, args)`**，不要用构造器名字符串；
- **值布局先用统一 tagged payload**，不提前做 Rust enum 单态化；
- **match 用 typed 专用 lowering + `ADT_TAG`/`ADT_FIELD`**，不复用 arm 函数；
- **S4b 已引入 reified 泛型参数、Option/Result prelude 与复杂模式**；
- **S4 不引入 GC**，但记录“ADT 持有可变对象/闭包后需重新评估”。
