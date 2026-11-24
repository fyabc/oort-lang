# 字节码序列化（`.obc`）

本页是 Oort 字节码**文件格式**的规范性文档，描述 `oort_lang.bytecode.serialize`
实际写出/读入的二进制布局。任何偏离都应被视为 bug。指令编码、操作码编号与常量池
描述符的**语义**见 [spec 12](12-hir-bytecode-vm.md)；本页只新增**文件层**（头、
布局、tagged 编码），不重复指令语义。

**类型擦除边界**：本格式承载的是动态/类型擦除字节码（与 spec 12 一致），不携带
`oort-core` 静态类型，方言中立。

## 扩展名与种类

- 扩展名 **`.obc`**（Oort ByteCode）。它不是 `.ort`，模块加载器只认 `.ort`，故
  `.obc` 文件不会被误当源码模块。
- **`.obc` 是通用「Oort 编译字节码」扩展名**：未来 typed/静态字节码共用 `.obc`，
  靠文件头的 **kind** 字段区分（见下）。kind 分「种类」、version 分「修订」，二者
  分离，避免扩展名 proliferation。

## 编码原语

全部**小端**：

| 记法 | 含义 |
|------|------|
| `u8`/`u16`/`u32` | 无符号整数（1/2/4 字节） |
| `i32`/`i64` | 有符号整数（4/8 字节，补码） |
| `f64` | IEEE-754 双精度（8 字节） |
| `bool` | `u8`，0/1 |
| `string` | `u32` 字节长度 + UTF-8 字节 |
| `opt<T>` | `bool` 存在标志 + 存在时的 `T` |
| `seq<T>` | `u32` 个数 + 逐个 `T` |

## 文件头

```text
magic "OBC" (3 字节) | kind u8 | version u8
```

- `kind`：字节码种类。`0` = 动态/类型擦除（当前）；`1` = typed 标量子集
  （研究性，见 [spec 14](14-typed-bytecode.md)）；`2+` 预留。读入方遇到不支持的
  kind 必须显式拒绝。
- `version`：该 kind 的格式修订号，当前写出 `2`（OP 0023：模式字面量值、
  MatchArm guard 字段）；读入兼容 `1` 与 `2`。不支持的 version 显式拒绝。

## 模块布局

```text
seq<Proto> functions   # 扁平函数表；所有 function_index 指向此表
Proto main             # 模块顶层 proto（独立于函数表）
```

`function_index`（`DEF_FUN`/`MAKE_CLOSURE` 的 Bx、ClassSpec 各方法/槽初始化器、
MatchArmSpec、ExtensionSpec、ParamSpec.default_index）一律索引 **functions 表**，
不含 main。

## Proto 布局

按序：

| 字段 | 编码 |
|------|------|
| name | `string` |
| params | `seq<string>` |
| register_count | `u16` |
| local_count | `u16` |
| scratch_base | `u16` |
| flags | `u8`：bit0 has_this、bit1 uses_cells、bit2 defines_extensions |
| signature | 见下 |
| code | `seq<u32>`（32 位指令字，编码见 spec 12） |
| constants | `seq<Constant>`（tagged，见下） |
| positions | `bool` 存在标志 + 存在时：`string` filename + `seq<Position>` |

`Position` = `u32` start_line + `i32` start_column（`-1` 表示无列）。positions
可选——VM 有兜底位置；`line_table` 由 positions 的行号派生，不单独落盘。

**SignatureSpec**：`bool` has_this + `seq<ParamSpec>`。
**ParamSpec**：`string` name + `u8` kind + `u16` slot + `bool` has_default +
`opt<u32>` default_index。kind 编号：0 POS_ONLY、1 POS_OR_KW、2 VAR_POS、
3 KW_ONLY、4 VAR_KW、5 BLOCK。

## 常量池（tagged）

每项 = `u8` tag + payload。**保留类型标签**（VM 按类型校验描述符）。

| tag | 类型 | payload |
|-----|------|---------|
| 0 | Null | 无 |
| 1 | Bool | `bool` |
| 2 | Int | `i64` |
| 3 | Float | `f64` |
| 4 | String | `string` |
| 5 | SlotsTuple | `seq<u16>`（FRESH 的寄存器槽号） |
| 6 | BigInt | `string`（十进制文本，用于超出 i64 的 Int） |
| 10 | ClassSpec | 见下 |
| 11 | CallSpec | `u16` positional_count + `seq<string>` keywords + `bool` has_block |
| 12 | EnumSpec | `string` name + `seq<(string, u16)>` constructors（名, 元数） |
| 13 | MatchSpec | `seq<MatchArm>` |
| 15 | ImportSpec | `string` module_path + `opt<string>` alias + `seq<(string, opt<string>)>` names + `bool` is_from |
| 16 | ExtensionSpec | `string` name + `u32` function_index + `opt<string>` symbol + `u16` operand_count + `string` receiver_name |

**ClassSpec**：`string` name + `u16` base_count + `seq<(string, u32)>` methods +
`seq<(string, bool, opt<u32>)>` slots（名, mutable, 初始化器索引）+
`seq<(string, u32)>` class_methods + `seq<(string, u16, u32)>` operators
（symbol, operand_count, 索引）+ `bool` has_metaclass。

**MatchArm** = `Pattern` + `u32` function_index + `opt<u32>` guard_index。
guard_index 自 version 2 起写出/读入；version 1 的 arm 没有该字段，读入时
视为 `None`。

**Pattern**（递归）= `u8` kind + `string` name + `seq<Pattern>` args；kind 编号：
0 wildcard、1 name、2 constructor、3 literal_int、4 literal_float、
5 literal_string、6 literal_bool、7 tuple、8 or。version 2 中 literal 类 kind
在 args 之后追加一个 tagged `Constant` 作为模式字面量值（version 1 无此字段）。

描述符字段语义见 spec 12 与 `bytecode/code.py`。

## 限制与校验

- **Int 范围**：`Int` 常量按值大小选择 tag 2（i64）或 tag 6（十进制文本，
  任意精度）。tag 6 只用于超出 i64 的值，因此旧文件布局不变；不认识 tag 6
  的旧读者必须显式拒绝，不能截断。读入时校验文本为合法十进制整数。
- **加载期校验**：magic/kind/version 匹配；函数索引 < len(functions)；
  register_count ≤ 256；常量池 ≤ 65536 项。
- 常量池去重规则（区分 Bool/Int/Float）由编译期保证（spec 12），文件按编译产物
  原样承载。

## 实现与往返

- 写出/读入：`oort_lang.bytecode.serialize.write_obc` / `read_obc`。
- 发射：`scripts/compile_obc.py input.ort [-o output.obc]`。
- 往返测试：`tests/unit/backend/test_serialize.py`（结构相等 + 读回模块交 Python
  VM 执行输出一致）。
