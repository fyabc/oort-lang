# HIR、字节码与寄存器 VM

本页是共享后端的**规范性文档**：描述 `-t vm`（执行）与 `-t bc`（反汇编）当前实际
接受与拒绝的行为。任何偏离都应被视为 bug。后端设计的长期目标见
[design 02](../design/02-bytecode-vm-design.md)，当前实现参考见
[design 13](../design/13-hir-design.md)，重实现约束与决策见
[OP 0004](../proposals/0004-bytecode-vm.md)。

**类型擦除边界**：HIR 与字节码**不携带任何 `oort-core` 静态类型**。两个方言
（`oort-object` 动态、`oort-core` 静态）在语义分析后降低到**同一份 HIR**；静态类型
在降低前已被擦除，只影响检查期诊断，不影响后端指令。因此泛型、变型等类型系统特性
不改变本规范。面向未来的 typed IR/VM（未装箱值、静态槽布局、单态调用/去虚拟化）
**不在本规范范围内**，见 design 02。

**核心原则**（OP 0004）：未实现的构造必须**显式拒绝**（抛 `UnsupportedSyntax` 或
对应诊断），禁止默认穿透、禁止静默产生错误结果。

## 执行与调试

| 目标 | 行为 |
|------|------|
| `-t vm` | 寄存器 VM 执行。**文件与 `-c` 的默认后端**。 |
| `-t bc` | 降低并编译到字节码，打印反汇编，不执行。 |
| `-t eval` | 树遍历解释器执行。**回退选项**；REPL 仍用它。 |
| `-t ast` / `-t astm` | 打印 AST / 带推断类型元数据的 AST，不执行。 |
| `-t hir` | 降低到 HIR 并打印，不执行。诊断视图，文本格式不承诺稳定。 |

`-t vm` 与 `-t eval` 对同一合法程序必须产生**相同的输出与返回值**（差分一致性，
见下文）；对非法程序的拒绝时机可能不同（见「显式拒绝」）。

## 编译流水线与 HIR

```text
源码 → 共享前端（词法/语法/AST）→ 方言语义分析 → 统一 HIR → 32 位字节码 → 寄存器 VM
```

HIR 是 AST 与字节码之间的**线性寄存器中间表示**：指令显式使用虚拟寄存器，局部
变量、临时值与调用参数都在寄存器中；HIR 不承载方言策略，类、ADT、match 等必须先
降低或显式拒绝。每条指令携带源码位置。

### HIR 指令集

| 指令 | 操作数 | 语义 |
|------|--------|------|
| `LoadConst` | dst, value | 宿主常量装入寄存器 |
| `LoadLocal` / `StoreLocal` | dst, slot / slot, src | 本帧 slot 读写 |
| `LoadGlobal` / `StoreGlobal` | dst, name / name, src | 全局环境按名读写 |
| `Move` | dst, src | 寄存器搬运（也用于短路逻辑与 if 结果合并） |
| `LoadOuter` / `StoreOuter` | dst, depth, slot / depth, slot, src | 沿父帧链 depth 层读写外层 slot |
| `FreshLocals` | slots | 循环体顶部为指定 slot 换新 cell（每迭代绑定） |
| `BinOp` / `UnOp` | dst, op, lhs, rhs / dst, op, operand | 二元/一元运算，op 为源语言符号 |
| `Jump` / `JumpIfFalse` / `JumpIfTrue` | [src,] target | 跳转到符号标签（条件跳转按 truthiness） |
| `Label` | name | 符号标签（字节码层解析为相对偏移） |
| `DefineFunction` | name, function_index | 顶层函数定义并绑定全局名 |
| `MakeClosure` | dst, function_index | 捕获当前帧创建闭包（lambda/嵌套函数） |
| `Call` | dst, callee, args, keywords, block | 调用（位置/关键字/尾随 block 实参） |
| `Return` | src | 返回 |
| `BuildList` / `BuildTuple` / `BuildSet` | dst, elements | 构造集合 |
| `BuildDict` | dst, items | 构造字典（key/value 对） |
| `BuildSlice` | dst, start, stop, step | 构造切片（None 表示缺省） |
| `GetItem` / `SetItem` | dst, container, index / container, index, src | 下标读写 |
| `GetAttr` / `SetAttr` | dst, value, name / value, name, src | 属性读写 |
| `BuildClass` | dst, name, bases, methods, slots, class_methods, operators, metaclass | 构造类 |
| `BuildEnum` | dst, name, constructors | 构造 ADT（构造器名 + 元数） |
| `Match` | dst, scrutinee, arms | 模式匹配（arm body 已降低为函数） |
| `OpenIterator` / `IteratorNext` | dst, iterable / value_dst, iterator, done | 迭代器协议 |
| `Unpack` | source, base, count | 多循环变量解包到连续寄存器 |
| `ImportModule` / `ImportFrom` | module_path, alias / module_path, names | 导入 |
| `RegisterExtension` | receiver, name, function_index, symbol, operand_count | 注册扩展方法/运算符 |
| `SuperProxy` | dst, receiver | 构造 super 代理 |

逻辑 `and`/`or` 无专用指令，降低为 `JumpIfFalse`/`JumpIfTrue` + `Move`（短路求值）。
`if`/`while`/`for` 均为表达式，结果寄存器初值为 `null`；`break value` 降低为
`Move result, value` 后跳 break 标签。

## 作用域、寄存器与闭包

- **全局 vs 局部**：模块顶层绑定为全局（`LoadGlobal`/`StoreGlobal`）；函数内声明为
  局部 slot。命名查找顺序：本函数词法作用域 → 外层函数（`LoadOuter`/`StoreOuter`，
  depth 为帧链距离）→ 全局。
- **寄存器分配**：单调递增、**从不复用**；上限 **256**（A/B/C 字段 8 位），超限抛
  `UnsupportedSyntax`。`local_count` 为局部寄存器水位线，`scratch_base = local_count`
  起为临时窗口。寄存器复用/类型特化属后续优化（design 02），当前不做。
- **不可变性**：赋 immutable 绑定（函数/类/import/`val`）在 lowering 期静态拒绝。
- **闭包模型**：**frame-capture**（捕获帧）而非 upvalue 表。`VMFrame` 持有
  `registers`、`parent`、`ext_env`。`_Cell` 是帧与闭包共享的可变绑定。
- **cell 协议**：函数体含 `MakeClosure` 时 `proto.uses_cells = True`，前
  `local_count` 个寄存器为 `_Cell`（scratch 区为裸值）；`LoadLocal`/`StoreLocal`/
  `Unpack`/`Fresh` 按此协议读写。`LoadOuter`/`StoreOuter` 按目标是否为 `_Cell`
  动态判定（兼容混合帧）。
- **每迭代绑定**：循环体内新声明的 slot 在循环体首条指令前插入 `FreshLocals`，每次
  迭代换新 cell，保证循环内创建的闭包不串迭代。for 循环变量不可变。
- **MAKE_CLOSURE**：`uses_cells` 时浅拷贝前 `local_count` 个寄存器槽为新帧
  （cell 引用共享、scratch 区不捕获），否则直接捕获当前帧。
- **扩展环境三通道**：闭包携带 `env`（模块全局值）与定义点 `ext_env`（扩展）；
  含 `RegisterExtension` 的 proto 每帧新建 `<extensions>` 子环境。属性/下标/运算符
  回退解析均用当前帧 `ext_env`。

## 函数与调用约定

- **函数表**：`HirModule`/`BytecodeModule` 含 `main` 与 `functions` 表，
  `function_index` 索引此表。顶层函数、类方法、类级方法、运算符方法、slot 初始化器、
  默认值表达式、match arm 都降低为独立函数。两遍 lowering：先预留函数索引，再降低
  main 与各函数体。
- **调用窗口 ABI**：HIR `Call` 的 callee/实参可为任意寄存器；字节码层窗口化——
  `MOVE base←callee`、`MOVE base+1+i←arg_i`（base = scratch_base），发 `CALL`/
  `CALL_KW`，**返回值覆写 base（callee）槽**，再 `MOVE dst←base`。关键字值续接
  `base+1+nargs`，block 再后一格。
- **scratch 需求**：`register_count = local_count + scratch`，scratch 取各类窗口
  需求最大值（调用 `1+nargs+nkw+block`、迭代器 1、集合元素数、字典 `2*对数`、切片 3、
  `SET_ATTR` 2/`GET_ATTR` 1、类 bases+metaclass、match 1）。超 256 拒绝。
- **this 槽 0**：方法 `has_this=True`，slot 0 为不可变 `this`，参数从 slot 1 起且
  **必须连续**。
- **参数绑定**：`SignatureSpec`/`ParamSpec` 描述六类参数（位置限定/位置或关键字/
  关键字限定/`*args`/`**kwargs`/`&block`）与默认索引。绑定规则与解释器**共享**
  （`runtime/call_protocol.py`），保证诊断一致。默认值**调用时求值**，可引用定义处
  闭包与更早参数（每个默认表达式降低为独立 proto，params 为此前所有参数）。
  `*args`→Tuple、`**kwargs`→Dict、`&block` 缺省 null。
- **slot 初始化器**：每个带初始化器的槽降低为无参 proto；构造实例时先逐槽求值，再
  调 `__init__`，最后检查未初始化槽。
- **match arm**：每 arm 降低为函数，params 为模式绑定名（按模式树先序，全部不可变）；
  arm 内禁止 `return`。
- **隐式返回**：main 与函数体末尾隐式 `Return`（最后表达式值，无则 null）。
- **import 提升**：main 中所有 import 先于其它语句发射；嵌套 import 拒绝。

## 字节码编码

**32 位定长字**：`op = word >> 24`（8 位），`A = (word >> 16) & 0xFF`（8 位）。

| 格式 | 字段 | 说明 |
|------|------|------|
| ABC | B=(word>>8)&0xFF, C=word&0xFF | 各 8 位 |
| ABx | Bx=word&0xFFFF | 16 位无符号（常量/函数索引） |
| AsBx | sBx∈[-0x8000,0x7FFF]，偏置 Bx=sBx+0x8000 | 跳转偏移，**相对下一条指令**：`pc_next = pc + 1 + sBx` |
| Ax | Ax=word&0xFFFFFF | 24 位，仅 `EXTEND` |

### 操作码编号

| 组 | 编号 | 操作码 |
|----|------|--------|
| 加载/存储/定义 | 1–7 | LOAD_K, LOAD_L, STORE_L, LOAD_G, STORE_G, DEF_FUN, MOVE |
| 二元 | 10–31 | ADD, SUB, MUL, DIV, FLOORDIV, MOD, POW, SHL, SHR, BAND, BOR, BXOR, EQ, NE, LT, LE, GT, GE, IN, NOT_IN, IS, IS_NOT |
| 一元 | 35–38 | POS, NEG, INVERT, NOT |
| 控制流/调用/迭代 | 40–47 | JUMP, JUMP_FALSE, JUMP_TRUE, CALL, RET, OPEN_ITER, ITER_NEXT, EXTEND |
| 复合 | 50–70 | NEW_LIST, NEW_TUPLE, NEW_SET, NEW_DICT, GET_ITEM, SET_ITEM, BUILD_SLICE, GET_ATTR, SET_ATTR, LOAD_OUTER, STORE_OUTER, MAKE_CLOSURE, BUILD_CLASS, IMPORT, BUILD_ENUM, MATCH, CALL_KW, UNPACK, FRESH, SUPER, REGISTER_EXT |

`EXTEND=47`（Ax）为**保留扩展前缀**，VM 中为 no-op。二元符号映射注意否定形式用
`!` 前缀（`!in`/`!is`，而非 `not in`）。

### 操作数字段语义（核心表）

| Op | A | B | C / Bx |
|----|---|---|--------|
| LOAD_K | dst | — | Bx=常量索引 |
| LOAD_L / STORE_L | dst / slot | slot / src | 0 |
| LOAD_G / STORE_G | dst / **src** | — | Bx=名字常量 |
| DEF_FUN | 0 | — | Bx=函数索引 |
| MOVE | dst | src | 0 |
| 二元 | dst | lhs | C=rhs |
| 一元 | dst | operand | 0 |
| JUMP / JUMP_FALSE / JUMP_TRUE | 0 / src / src | — | sBx=相对偏移 |
| CALL | base | 0 | C=位置实参数；结果写回 base |
| CALL_KW | base | — | Bx=CallSpec；结果写回 base |
| RET | src | 0 | 0 |
| OPEN_ITER | dst | iterable | 0 |
| ITER_NEXT | value_dst | iterator | C=valid 标志寄存器；编码后紧跟 `JUMP_FALSE valid→done` |
| NEW_LIST/TUPLE/SET | dst | base（元素窗口） | C=元素数（≤255） |
| NEW_DICT | dst | base（key,val 交错） | C=**对数** |
| BUILD_SLICE | dst | base | C=flags（bit0=start, bit1=stop, bit2=step） |
| GET_ATTR | base（receiver，**原地覆写为结果**） | — | Bx=属性名 |
| SET_ATTR | base（receiver） | — | Bx=名字；值在 base+1 |
| GET_ITEM / SET_ITEM | dst / container | container / index | C=index / src |
| LOAD_OUTER / STORE_OUTER | dst / depth | depth / slot | C=slot / src |
| MAKE_CLOSURE | dst | — | Bx=函数索引 |
| BUILD_CLASS | dst | — | Bx=ClassSpec；bases(+metaclass) 预 MOVE 到 scratch_base |
| BUILD_ENUM | dst | — | Bx=EnumSpec |
| MATCH | dst | — | Bx=MatchSpec；scrutinee 预 MOVE 到 scratch_base；逐 arm 匹配，守卫为真才调用 arm 函数 |
| IMPORT | 0 | — | Bx=ImportSpec |
| UNPACK | source | base（目标起始） | C=count |
| FRESH | 0 | — | Bx=slots 元组常量；仅 uses_cells 的 proto 发射 |
| SUPER | dst | receiver | 0 |
| REGISTER_EXT | receiver（类型寄存器） | — | Bx=ExtensionSpec |

### 常量池与描述符

常量池按 `(type(value).__name__, repr(value))` 去重（**区分 Bool 与 Int**），上限
65536 项，溢出拒绝。描述符对象本身作为常量池成员：

- `Proto`：name、params、register_count、code（32 位字）、constants、line_table 与
  positions（**与 code 逐字对齐**）、scratch_base、has_this、signature、local_count、
  uses_cells、defines_extensions。
- `CallSpec`：positional_count、keywords、has_block（实参值在寄存器窗口）。
- `ClassSpec`：name、base_count、methods、slots、class_methods、operators、
  has_metaclass（bases/metaclass 运行时从 scratch 窗口读）。
- `EnumSpec`：name、constructors（名+元数）。
- `MatchSpec`/`MatchArmSpec`/`PatternSpec`：arms；pattern kind 为
  wildcard/name/constructor/literal_int/literal_float/literal_string/
  literal_bool/tuple/or（递归）；literal kind 带值 `value`，MatchArmSpec 带
  `guard_index`（守卫函数索引，None 表示无守卫）。守卫函数参数为 pattern 绑定，
  返回 Bool；守卫为假时继续下一个 arm。
- `ImportSpec`：module_path、alias、names、is_from（一个 IMPORT 承载两种 import）。
- `ExtensionSpec`：name、function_index、symbol、operand_count、receiver_name。

跳转在编译期回填 sBx；超 sBx 范围、重复/缺失标签均拒绝。

### 反汇编（`-t bc`）

先 main 再各函数（前缀 `[i]`）；头行 `Proto <name> regs=<n> params=(...)`；每条
`{pc:4d}  <助记符>  ; line <n>`。助记符如 `LOAD_K R0 K1(1)`、`CALL R5 nargs=2`、
`JUMP_FALSE R3 <绝对pc>`、`BUILD_CLASS R0 Name bases=1 ...`。HIR 另有调试 dump
（`hir/dump.py`，保留符号标签），无独立 CLI 目标。

## VM 语义

- **帧与闭包**：`VMFrame`（registers/parent/ext_env）；`OortVMClosure` 实现
  `OortVMInvokable`，携带 module/proto/捕获帧/env/定义点 ext_env/defining_type。
- **调用分发**：全位置且参数全为「位置限定/位置或关键字、无默认」时走快路径（按
  param.slot 直写寄存器）；否则走与解释器共享的 `bind_arguments`。`CALL` 对
  OortType 走构造、对闭包走 invoke、其余回退 `interpreter.call_value`。native 函数
  拒收关键字实参。
- **类构造**：新建实例 → 逐槽求值初始化器 → 无 `__init__` 要求 0 实参，有则必须为
  字节码闭包 → 检查未初始化槽。
- **运算符**：Int×Int 走快路径（`/` 产 Float；除零抛 `OortRuntimeError`）；其余回退
  `interpreter.apply_binary`/`apply_unary`（支持运算符重载与扩展运算符，用帧
  ext_env 解析）。
- **数值语义**：Int/Int `/` 固定 Float；**Int 常量每次 `LOAD_K` 新建对象**（保持
  `1 is 1` 为 false 的身份语义）；bool 为单例。
- **迭代器**：`OPEN_ITER` 调 `__iter__`（须返回 callable）；`ITER_NEXT` 取
  `(value, valid:Bool)` 二元组，value=None→null，valid 写标志寄存器。
- **match**：逐 arm 匹配模式（wildcard 恒真；name 绑定；constructor 校验 variant 与
  payload 元数），命中后以绑定值为实参调 arm 闭包；全失配抛
  `OortRuntimeError("No match arm matched value ...")`。
- **模块**：每模块独立全局环境；`IMPORT` 经共享 ModuleLoader（路径解析、缓存、循环
  检测、跨方言拒绝），两种形式都激活被导入模块的顶层扩展。
- **错误位置**：运行期错误位置 = 当前 pc 的 `positions[pc]`；调用绑定错误优先用调用
  点位置，回退 `proto.positions[0]`，再回退 `<bytecode>` 1:0。

## 结构校验

`validate_module` 在 lowering 末尾校验（违反抛 `ValueError`）：

- `local_count ∈ [0, 256]`；所有读写寄存器 ∈ `[0, local_count)`。
- 标签唯一，且所有跳转/`IteratorNext.done` 目标存在。
- `function_index`/arm/method/slot 初始化器索引在 `module.functions` 范围内。
- `FreshLocals` slot < local_count；`LoadOuter`/`StoreOuter` depth≥1 且 slot<256。

## 显式拒绝

未实现构造显式拒绝，分三个时机。**VM 在 lowering/编译期拒绝的构造，解释器可能在
运行期才拒绝**——诊断措辞与时机存在已知差异（见 [spec 06](06-conformance.md)），
但都遵循「不静默错执行」。

### lowering 期（`UnsupportedSyntax`，消息模板 "HIR backend does not support X."）

| 类别 | 示例 |
|------|------|
| 调用侧展开 | `f(*args)`、`f(**kw)` |
| match arm 内控制流 | arm 内 `return`/`break`/`continue` |
| 泛型 | 泛型函数/类/方法/lambda/扩展 |
| 嵌套构造 | 嵌套 import、嵌套 class、表达式位置嵌套 def |
| 声明 | 多目标声明、无初始化器声明、多目标 slot |
| 赋值 | 属性/元组赋值目标、赋 immutable 绑定、未知复合赋值运算符 |
| 类形式 | 命名空间/匿名类、class body 内扩展、类级运算符、特殊方法（除 `__init__`/`__iter__`） |
| 顶层形式 | 顶层扩展/class method/operator 方法、顶层 return |
| 其他 | ellipsis、方法外 super、class/enum 表达式、dict 解包、infix 调用、多个尾随 block、无变量 for、循环外 break/continue、寄存器超 256 |

### 字节码编译期（`UnsupportedSyntax`）

register_count>256、未知二元/一元符号、集合>255 元素、调用>255 位置实参、重复/缺失
标签、跳转超 sBx 范围、常量池溢出。

### VM 运行期（防御错误，带位置）

常量池描述符类型校验（`Invalid ... descriptor`）、函数/方法/arm/扩展索引越界
（`Invalid bytecode ... index`）、闭包 depth 断链、未知 opcode；以及语义错误：Name
未定义、方法缺 receiver、base/metaclass 非类、扩展 receiver 非类型、扩展/构造器/
import 绑定重名、match 无匹配、模式元数不符、unpack 元数不符、除零等。

## 与解释器的差分一致性

规范行为由 `tests/unit/backend/` 锚定：

- `test_hir.py`：AST→HIR 降低快照 + 结构校验 + 参数化显式拒绝。
- `test_bytecode.py`：ABC/ABx/AsBx/Ax 编解码 round-trip、越界拒绝、常量池区分
  Bool/Int、调用 scratch 约定、各 opcode、反汇编。
- `test_vm.py`：**核心差分**——同一源码分别 `-t eval` 与 `-t vm` 执行，断言 stdout
  与返回值都相等；另有 VM 错误路径与模块/扩展/core 槽用例。
- `test_hir_dump.py`：HIR 文本 dump。
- `test_vm_error_diff.py`：错误差分，按严格度分级——strict（类型+消息+行号全同）/
  text（类型+消息同，行号允许 VM 报外层表达式）/both_fail（VM lowering 期拒绝 vs
  解释器运行期拒绝）/vm_rejects（解释器可跑但 VM 在子集边界拒绝）。

## 尚未实现

调用侧 `*`/`**` 展开、match arm 内控制流、寄存器复用与类型特化、typed IR/VM
（未装箱值、静态槽布局、单态调用/去虚拟化）。这些属 [design 02](../design/02-bytecode-vm-design.md)
的长期目标，不作为当前规范。
