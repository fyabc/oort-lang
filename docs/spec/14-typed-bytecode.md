# 类型化字节码（`.obc` kind=1）

> **状态**：研究性规范（2026-11-22，M3/M4）。描述当前 `oort-core` 标量子集的
> typed 字节码；格式**尚未承诺稳定**，可能随 typed IR/Rust VM 研究演进。
> 擦除式字节码（kind=0）仍由 [spec 13](13-bytecode-serialization.md) 规范；
> 指令语义的共享部分见 [spec 12](12-hir-bytecode-vm.md)。

## 1. 范围与关系

- 本文描述 `.obc` **kind=1** 的文件布局、typed 指令编码与执行语义；
- 参考实现：Python `src/oort_lang/bytecode/typed_{opcodes,compile,serialize,vm}.py`，
  Rust `rust/oort-vm/src/typed.rs`；
- 类型系统与 typed HIR 的研究背景见 [design 15](../design/15-typed-ir.md)；
- kind=1 与 kind=0 **互斥**：kind=0 读者必须拒绝 kind=1，反之亦然。

## 2. 文件头与布局

```text
magic "OBC" (3 bytes) | kind u8 (=1) | version u8 (=1)
u32 function_count
proto[function_count]
proto(main)
```

所有多字节整数小端；`string` 为 `u32` 字节长度 + UTF-8；`bool` 为 `u8`（0/1）。

### 2.1 Proto 布局

```text
string name
bool   is_main
u16    register_count
u8     register_type[register_count]
u8     param_count
u8     param_type[param_count]
u8     ret_type
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

类型标签：

| tag | 类型 |
|---:|---|
| 0 | 无类型（仅寄存器表、未使用的寄存器） |
| 1 | `Int` |
| 2 | `Float` |
| 3 | `Bool` |
| 4 | `Unit` |
| 5 | 函数引用（CALL 目标） |

- 参数与返回类型不允许 tag 0；
- 常量池复用 spec 13 的 tagged 编码；kind=1 只允许 `null`/`bool`/`int`/`float`/
  `string`，其他 tag 必须显式拒绝；
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

### 3.3 混合数值运算

编译器不为 `Int`/`Float` 组合生成专用操作码：先把 `Int` 操作数用 `TO_FLOAT`
转换到临时寄存器，再使用 `_F` 指令；`/` 总是先转换两个操作数再 `DIV_F`。

### 3.4 控制流与标签

typed HIR 的命名标签在编译期解析为绝对字索引；`JMP`/`JMP_FALSE`/`JMP_TRUE`
的 `Bx` 直接指向目标字。读取方不重新解析标签。

## 4. 执行语义

- 值与 kind=0 共享运行时值模型（当前实现仍是 boxed 值）；未装箱寄存器是后续
  M4 工作，不属于本版本；
- `Int` 在 Python 参考实现中使用宿主整数；Rust spike 使用 `i64`，溢出会报错。
  这是 spike 的表示限制，不是语言语义；跨实现差分测试避免溢出输入；
- 除零、类型守卫失败、未知全局/函数索引、未知操作码都必须显式报错，禁止静默
  执行；
- `DEF_FUN` 的绑定可在主函数执行时发生；实现可以预绑定全部函数，语义等价；
- `FRESH_LOCALS` 在标量子集中不可观察（无闭包），kind=1 不编码该指令。

## 5. 当前边界

- 仅 `oort-core` 标量子集：`Int`/`Float`/`Bool`/`Unit`、顶层函数、直接调用、
  `if`/`while`/早返回；
- 无 String、集合、ADT/`match`、类/接口/泛型/lambda、模块导入；
- 无动态↔静态边界、`box`/`unbox`/blame；跨方言调用仍拒绝；
- 格式版本 `version=1`；不兼容变更必须提升 version，并保持 kind=1 的独立
  命名空间。

## 6. 参考实现入口

| 实现 | 入口 |
|---|---|
| Python | `bytecode/typed_compile.py`、`typed_vm.py`、`typed_serialize.py` |
| CLI | `-t tbc`（反汇编）、`-t tvm`（执行） |
| Rust | `rust/oort-vm/src/typed.rs`；`oort-vm <file.obc>` 按 kind 分派 |
| 差分 | `scripts/rust_vm_check.py --diff-only`（含 typed 程序） |
