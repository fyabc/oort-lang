# 类型化字节码（`.obc` kind=1）

> **状态**：研究性规范（2026-11-23，M3/M4/S2b）。描述当前 `oort-core` typed
> 子集的 typed 字节码；格式**尚未承诺稳定**，可能随 typed IR/Rust VM 研究演进。
> 擦除式字节码（kind=0）仍由 [spec 13](13-bytecode-serialization.md) 规范；
> 指令语义的共享部分见 [spec 12](12-hir-bytecode-vm.md)。

## 1. 范围与关系

- 本文描述 `.obc` **kind=1** 的文件布局、typed 指令编码与执行语义；
- 参考实现：Python `src/oort_lang/bytecode/typed_{opcodes,compile,serialize,vm}.py`，
  Rust `rust/oort-vm/src/typed.rs`；
- 类型系统与 typed HIR 的研究背景见 [design 15](../design/15-typed-ir.md)；
- kind=0、kind=1 与 kind=2 互斥：各自读者必须拒绝其他 kind；
- kind=2 是 loader 链接后的 typed linked bundle（v3，见 design 19 §3.1），
  只保存合并声明表、扁平构造器表与 proto，不含 import/export。

## 2. 文件头与布局

```text
magic "OBC" (3 bytes) | kind u8 (=1) | version u8 (=8)
# v8 单模块布局；v10 module artifact 的头部（module_id/export/import/
# constructor 表）见 design 19
u32 adt_decl_count
adt_decl[adt_decl_count]:
  string origin
  string name
  u16    constructor_count
  constructor[constructor_count]:
    string name
    u8     arity
u32 function_count
proto[function_count]
proto(main)
```

所有多字节整数小端；`string` 为 `u32` 字节长度 + UTF-8；`bool` 为 `u8`（0/1）。

### 2.1 Proto 布局

```text
string name
bool   is_main
u16    type_count
type_desc[type_count]              # 子类型必须引用更早的表项
u16    register_count
u16    register_type_id[register_count]   # 0 = 无类型，否则 type_id + 1
u8     param_count
u16    param_type_id[param_count]
u16    ret_type_id
u16    cell_count
u16    cell_slot[cell_count]              # 帧入口包成单元格的寄存器
u32    word_count
u32    word[word_count]
u32    constant_count
constant[constant_count]
positions?:
  bool   present
  string filename
  u32    position_count (= word_count)
  (u32 line, i32 column)[position_count]
```

类型描述 tag：

| tag | 类型 | 额外字段 |
|---:|---|---|
| 1 | `Int` | — |
| 2 | `Float` | — |
| 3 | `Bool` | — |
| 4 | `Unit` | — |
| 5 | 函数引用（CALL 目标） | — |
| 6 | `String` | — |
| 7 | `List` | `u16 element_type_id` |
| 8 | `Set` | `u16 element_type_id` |
| 9 | `Dict` | `u16 key_type_id, u16 value_type_id` |
| 10 | `Tuple` | `u16 count, u16 element_type_id[count]` |
| 11 | `Iterator` | — |
| 12 | `Adt` | `u16 adt_decl_id, u16 arg_count, u16 arg_type_id[arg_count]` |

- 类型表按**后序**写入：容器类型只能引用已经出现的子类型（不允许前向引用）；
- 寄存器类型 0 表示“无类型”；参数/返回不允许 0；
- `cell_slot` 是本帧中被任意 lambda 子树读取或写入的局部/参数槽（编译期
  沿创建者链静态求得）；读取方校验每个槽 `< register_count`。帧入口按该表
  把槽值包成单元格，`LOAD_L`/`STORE_L` 对单元格透明读写；
- 常量池复用 spec 13 的 tagged 编码；kind=1 只允许 `null`/`bool`/`int`/
  `bigint`（i64 之外的整数）/`float`/`string`，其他 tag 必须显式拒绝；
- 位置表可省略；读取方缺少时使用 `<typed-bytecode>` 回退位置。

## 3. 指令编码

32 位定长：

```text
ABC: [op:8][A:8][B:8][C:8]
ABx: [op:8][A:8][Bx:16]
```

跳转使用 **绝对字索引**（`Bx`），不是相对偏移。

### 3.1 操作码

| op | 名称 | 格式 | 操作数 | 语义 |
|---:|---|---|---|---|
| 1 | `LOAD_K` | ABx | A=目标, Bx=常量 | `R[A] = constant[Bx]` |
| 2 | `LOAD_L` | ABC | A=目标, B=槽 | `R[A] = R[B]`（局部槽） |
| 3 | `STORE_L` | ABC | A=槽, B=源 | `R[A] = R[B]`（局部槽） |
| 4 | `LOAD_G` | ABx | A=目标, Bx=名字常量 | 函数/内建 `print` |
| 5 | `DEF_FUN` | ABx | A=名字常量, Bx=函数索引 | 绑定函数名 |
| 6 | `MOVE` | ABC | A=目标, B=源 | `R[A] = R[B]` |
| 10/11 | `ADD_I` / `ADD_F` | ABC | A=目标, B=左, C=右 | Int/Float 加法 |
| 12/13 | `SUB_I` / `SUB_F` | ABC | 同上 | 减法 |
| 14/15 | `MUL_I` / `MUL_F` | ABC | 同上 | 乘法 |
| 16 | `DIV_F` | ABC | 同上 | Float 除法（总是 Float） |
| 17/18 | `FLOORDIV_I` / `FLOORDIV_F` | ABC | 同上 | 向下取整除法 |
| 19/20 | `MOD_I` / `MOD_F` | ABC | 同上 | 取模（符号随除数） |
| 21/22/23 | `EQ_I` / `EQ_F` / `EQ_B` | ABC | 同上 | 相等 → Bool |
| 24/25/26 | `NE_I` / `NE_F` / `NE_B` | ABC | 同上 | 不等 → Bool |
| 27/28 | `LT_I` / `LT_F` | ABC | 同上 | 小于 → Bool |
| 29/30 | `LE_I` / `LE_F` | ABC | 同上 | 小于等于 → Bool |
| 31/32 | `GT_I` / `GT_F` | ABC | 同上 | 大于 → Bool |
| 33/34 | `GE_I` / `GE_F` | ABC | 同上 | 大于等于 → Bool |
| 35/36 | `POS_I` / `POS_F` | ABC | A=目标, B=操作数, C=0 | 一元 `+` |
| 37/38 | `NEG_I` / `NEG_F` | ABC | 同上 | 一元 `-` |
| 39 | `NOT_B` | ABC | 同上 | Bool 取反 |
| 40 | `TO_FLOAT` | ABC | A=目标, B=源, C=0 | Int → Float |
| 41 | `JMP` | ABx | A=0, Bx=目标字 | 无条件跳转 |
| 42 | `JMP_FALSE` | ABx | A=条件, Bx=目标 | 条件为 false 跳转 |
| 43 | `JMP_TRUE` | ABx | A=条件, Bx=目标 | 条件为 true 跳转 |
| 44 | `CALL` | ABC | A=窗口基址, B=实参数, C=结果寄存器 | 见 §3.2 |
| 45 | `RET` | ABC | A=返回值, B=C=0 | 返回 |
| 46/47 | `EQ_MIXED` / `NE_MIXED` | ABC | A=目标, B=左, C=右 | Int/Float 相等/不等，按数学值精确比较 |
| 48/49 | `LT_MIXED` / `LE_MIXED` | ABC | 同上 | Int/Float 小于/小于等于（精确） |
| 50/51 | `GT_MIXED` / `GE_MIXED` | ABC | 同上 | Int/Float 大于/大于等于（精确） |
| 52 | `ADD_S` | ABC | A=目标, B=左, C=右 | String 拼接 |
| 53/54 | `EQ_S` / `NE_S` | ABC | 同上 | String 相等/不等 → Bool |
| 55/56 | `LT_S` / `LE_S` | ABC | 同上 | String 小于/小于等于 → Bool |
| 57/58 | `GT_S` / `GE_S` | ABC | 同上 | String 大于/大于等于 → Bool |
| 59 | `NEW_LIST` | ABC | A=元素窗口基址, B=元素数, C=目标 | 构造 List |
| 60 | `NEW_TUPLE` | ABC | 同上 | 构造 Tuple |
| 61 | `GET_ITEM` | ABC | A=目标, B=容器, C=索引 | 下标读取 |
| 62/63 | `EQ_LIST` / `NE_LIST` | ABC | A=目标, B=左, C=右 | List 深相等/不等 → Bool |
| 64/65 | `EQ_TUPLE` / `NE_TUPLE` | ABC | 同上 | Tuple 深相等/不等 → Bool |
| 66 | `OPEN_ITER` | ABC | A=目标, B=可迭代值, C=0 | 创建迭代器（List/Tuple/Set/Dict/String 的快照） |
| 67 | `ITER_NEXT` | ABC | A=值目标, B=迭代器, C=有效标志 | `(R[A], R[C]) = next(R[B])`；结束时值为 `Unit`、标志为 false |
| 68 | `SET_ITEM` | ABC | A=容器, B=索引, C=源 | **预留**：List 原地写入；当前语言表面禁止下标赋值，编译器尚不发出 |
| 69 | `NEW_SET` | ABC | A=元素窗口基址, B=元素数, C=目标 | 构造 Set，按值相等去重 |
| 70 | `NEW_DICT` | ABC | A=窗口基址, B=条目数, C=目标 | 构造 Dict；窗口为 `key,value` 交替的 `2*B` 个寄存器 |
| 71/72 | `EQ_SET` / `NE_SET` | ABC | A=目标, B=左, C=右 | Set 深相等/不等（顺序无关）→ Bool |
| 73/74 | `EQ_DICT` / `NE_DICT` | ABC | 同上 | Dict 深相等/不等（键查找 + 值比较）→ Bool |
| 75 | `NEW_ADT` | ABC | A=payload 窗口基址, B=构造器 ID, C=目标 | 构造 ADT；v8 中 B 为声明表扁平 id，v10 artifact 中为构造器表下标（loader 回填为全局 id）；payload 数由声明 arity 决定 |
| 76 | `ADT_TAG` | ABC | A=目标 Int, B=ADT 值, C=0 | 返回构造器在声明内的索引 |
| 77 | `ADT_FIELD` | ABC | A=目标, B=ADT 值, C=字段索引 | 读取 payload 字段 |
| 78/79 | `EQ_ADT` / `NE_ADT` | ABC | A=目标, B=左, C=右 | ADT 名义 + 变体 + payload 深相等/不等 → Bool |
| 80 | `TUPLE_ITEM` | ABC | A=目标, B=Tuple, C=索引 | 静态索引读取 Tuple 元素（支持异构 Tuple） |
| 81 | `CONTAINS` | ABC | A=目标 Bool, B=容器, C=被查值 | List/Tuple 值相等、Set/Dict 键相等、String 子串 |
| 82 | `SLICE` | ABC | A=三槽窗口基址 `[容器, start, stop]`, B=flags（1=有 start,2=有 stop）, C=目标 | 切片读；缺省槽为 Unit，步长不在指令中 |
| 83/84 | `SET_UNION` / `SET_INTERSECT` | ABC | A=目标, B=左, C=右 | Set 并/交，键相等去重 → 新 Set |
| 85/86 | `SET_DIFFERENCE` / `SET_SYMMETRIC` | ABC | 同上 | Set 差/对称差 → 新 Set |
| 87 | `MK_FUN` | ABx | A=目标, Bx=函数索引 | 把函数（含非捕获 lambda）物化为一等函数值 |
| 88 | `MK_CLOSURE` | ABx | A=目标, Bx=函数索引 | 创建捕获闭包：快照当前寄存器，父链取当前执行闭包；cell 槽的快照值为单元格本身 |
| 89 | `LOAD_OUTER` | ABC | A=目标, B=深度（1 基）, C=槽 | 沿闭包父链走 B-1 步后读该帧槽 C（单元格自动解包） |
| 90 | `STORE_OUTER` | ABC | A=深度（1 基）, B=槽, C=源 | 沿父链写该帧槽 B；目标必须是单元格，否则运行时报错 |
| 91 | `FRESH_CELL` | ABC | A=槽, B=C=0 | 把本帧槽 A 重新包成新单元格（每轮迭代独立的捕获变量） |

### 3.2 调用约定

```text
CALL A B C
  callee = R[A]
  args   = R[A+1 .. A+B]
  R[C]   = invoke(callee, args)
```

- 调用者负责把 callee 与实参搬入连续窗口 `A .. A+B`；结果写入独立寄存器 `C`；
- 被调函数入口按 `param_types` 做类型守卫，失败即运行时错误；
- 实参个数必须等于 `param_types` 长度；
- 当前仅支持位置实参；关键字/尾随 block 不是 kind=1 的合法构造。

### 3.3 混合数值与字符串运算

- **算术**：`Int`/`Float` 混合时先把 `Int` 操作数用 `TO_FLOAT` 转换到临时
  寄存器，再使用 `_F` 指令；`/` 总是先转换两个操作数再 `DIV_F`。
- **比较/相等**：不同数值类型使用 `*_MIXED` 指令，按**数学值精确比较**，
  不先转换成 Float。例如 `2**53 + 1 == 2.0**53` 为 false。NaN 语义见
  [design 16](../design/16-numeric-semantics.md)：`==` 为 false，`!=` 为
  true，排序比较为 false。
- **String**：`+` 生成新字符串；比较/相等使用 `*_S` 指令，按字典序/值相等。
  `len` 是 native 调用，返回 Int（字符数）。

### 3.4 控制流与标签

typed HIR 的命名标签在编译期解析为绝对字索引；`JMP`/`JMP_FALSE`/`JMP_TRUE`
的 `Bx` 直接指向目标字。读取方不重新解析标签。

`for x in xs { ... }` 降低为：

```text
OPEN_ITER  it, xs, 0
loop:
ITER_NEXT  x, it, ok
JMP_FALSE  ok, end
... body ...
JMP        loop
end:
```

`OPEN_ITER` 接受元素类型已知的 List/Set、元素类型齐次的 Tuple、Dict 或
String（元素为单字符 String）；Set 迭代元素，Dict 迭代键。迭代器是
**快照**，循环期间修改容器不影响本次迭代。`ITER_NEXT` 的 `ok` 是编译器
分配的临时 Bool 寄存器；HIR 层不暴露该寄存器。

## 4. 执行语义

- **值表示由实现决定**：Python 参考实现使用 boxed 运行时值（差分 baseline）；
  Rust typed VM 标量使用未装箱表示，String 使用 `Rc<str>`，List/Set 使用
  `Rc<RefCell<Vec<TypedValue>>>`，Tuple 使用 `Rc<[TypedValue]>`，Dict 使用
  `Rc<RefCell<Vec<(TypedValue, TypedValue)>>>`，迭代器使用
  `Rc<RefCell<{ values, index }>>`，被捕获变量使用
  `Rc<RefCell<TypedValue>>`；只在 native `print`/`len` 与主结果边界转换；
- Dict 的实现通常保持插入顺序，但**顺序不是语言保证**；Set 同样不保证。
  Rust 参考实现用有序 `Vec` + 线性键查找，不依赖 `std::HashMap`；
- `Int` 在 Python 参考实现中使用宿主整数（任意精度）；Rust typed VM
  使用 `num-bigint` 任意精度，Rust 动态 VM 用 i64 快速路径并在溢出时提升为
  `BigInt`。`.obc` 常量池对超出 i64 的整数使用 spec 13 的 tag 6（十进制文本），
  因此大整数字面量可序列化与往返。完整数值语义见
  [design 16](../design/16-numeric-semantics.md)；
- 除零、类型守卫失败、未知全局/函数索引、未知操作码都必须显式报错，禁止静默
  执行；
- `DEF_FUN` 的绑定可在主函数执行时发生；实现可以预绑定全部函数，语义等价；
- v8 单模块文件不编码 import；v10 module artifact 用文件头的 import/export
  表与构造器表描述模块边，但函数体仍没有 import opcode——loader 在加载时完成链接；
- kind=1 **没有全局存储**（无顶层变量、无 `STORE_G`），因此实现可以在加载时
  预解析 `LOAD_G` 并缓存；若未来版本加入全局存储，写入时必须使缓存失效
  （实现采用全局版本号 + 惰性重解析）；动态 kind=0 仍走名字查找；
- 被捕获的变量按**引用语义**共享：编译器把被任意 lambda 子树读写的寄存器列进
  proto 的 `cell_slot`，帧入口把它们的值包成单元格；`LOAD_L`/`STORE_L` 透明
  读写单元格，`MK_CLOSURE` 的快照在 cell 槽上保存单元格本身。于是创建后再
  赋值、闭包内写回外层变量都对两侧可见。Python 与 Rust typed VM 的单元格
  实现不同（`TypedCell` / `Rc<RefCell<..>>`），语义一致；
- HIR `FreshLocals`（循环体入口）降低为对每个槽的 `FRESH_CELL`：每轮迭代
  重新包单元格，因此早先迭代创建的闭包保留各自的绑定；
- `FRESH_LOCALS` 本身不是 kind=1 操作码；无闭包时 `FRESH_CELL` 也不发出。

## 5. 当前边界

- 仅 `oort-core` typed 子集：`Int`/`Float`/`Bool`/`Unit`/`String`、顶层函数、
  直接调用、`if`/`while`/`for`/早返回、String 拼接/比较/`len`、List/Tuple/Set/
  Dict 字面量、List/Tuple/String/Dict 下标读取、`len`、深相等、
  List/Tuple（元素齐次）/Set/Dict/String 的 `for` 迭代；
- 集合表面（OP 0031）：`in`/`!in`、List/Dict 下标写入、List/Tuple/String
  切片读（步长拒绝）、Set `| & - ^`；
- 函数值（B2）：命名函数与 lambda 可作参数/返回值/局部变量/容器元素；
  函数类型擦除为 `FUNCTION`；非捕获 lambda 经 `MK_FUN` 物化，捕获闭包经
  `MK_CLOSURE` 创建（lambda proto 不导出、不进入接口哈希，跨模块重定位与
  命名函数一致）；
- 捕获闭包（B2 第二切片）：被捕获的变量按引用共享（单元格）。闭包内部既可
  读也可写（`LOAD_OUTER`/`STORE_OUTER`），创建者在创建后继续赋值同样对闭包
  可见；循环体每轮 `FRESH_CELL` 保证各轮闭包互不干扰；
- 支持单态与泛型 ADT（含 prelude `Option`）；类型参数进入类型表并在运行时
  作为 ADT 实例身份保留；match 支持 ADT/Int/Float/Bool/String/Tuple
  scrutinee，构造器/通配/变量/守卫/字面量/Tuple/或模式与嵌套组合；
- 无切片赋值/步长切片、Set 子集比较、列表拼接/排序；类/接口/泛型函数仍拒绝；
  函数值比较/打印仍拒绝；typed 模块导入在 loader 中解析，
  函数体不进入 kind=1 字节码；
- kind=1 有两个不再互读的版本：**v8** 为单模块程序（含 proto cell 表），
  **v10** 为 module artifact（module_id/export/import 表 + 构造器表；
  v6–v9 为历史格式）；
  ADT 模块声明表位于文件头；旧读者遇到未知 version/opcode/tag 必须报错
  而不是猜测；破坏既有布局的变更必须提升 version；
- `-t tvm` 与 `-t tbc` 共享 v10 artifact + loader 的同一链接结果（tbc 只是
  反汇编该程序）；`--cache-dir DIR`/`OORT_CACHE_DIR` 复用磁盘上的 v10 artifact，`--no-cache` 关闭，`--cache-max-size` 限制容量（缓存契约见
  [OP 0030](../proposals/0030-compilation-cache.md)）；`-t thir` 仍用
  P1a/P1b 的 HIR 拍平器，作为链接前的调试视图；
- kind=1 本身不编码跨方言边界；`oort-object → oort-core` 由 B1
  边界（OP 0028）处理，反向仍拒绝；`box`/`unbox`/blame 的稳定 ABI
  尚未定义；
- 单模块格式版本 `version=8`，module artifact 版本 `version=10`，
  linked bundle `kind=2, version=3`；不兼容变更
  必须提升 version，并保持 kind=1 的独立命名空间。

## 6. 参考实现入口

| 实现 | 入口 |
|---|---|
| Python | `bytecode/typed_compile.py`、`typed_artifact.py`、`typed_vm.py`、`typed_serialize.py` |
| CLI | `-t tbc`（反汇编）、`-t tvm`（执行） |
| Rust | `rust/oort-vm/src/typed.rs`；`oort-vm <file.obc>` 按 kind 分派；`oort-vm --link <root.obc> <dep.obc>...` 原生链接 v10 artifact |
| 差分 | `scripts/rust_vm_check.py --diff-only`（含 typed 程序） |
