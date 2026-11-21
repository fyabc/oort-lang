# OP 0018: 下标与缺失属性协议

- **状态**：Implemented
- **日期**：2026-11-21
- **相关**：[OP 0002](0002-dsl-support.md)、[OP 0007](0007-oort-object-object-model.md)、[规范 02](../spec/02-expressions.md)、[规范 05](../spec/05-classes.md)

## 摘要

为 `oort-object` 补齐用户类参与 `a[i]` / `a[i] = v` 与缺失属性读取的协议：

- 下标：`def operator "[]"(index)`、`def operator "[]="(index, value)`；
- 缺失属性只读 fallback：`def on_missing(name)`；
- 不引入 `__getitem__` / `__getattr__` / `__setattr__` 等 Python 风格魔术名；
- 字段初始化器语法糖不在本提案范围。

## 动机

当前运行时下标直接执行宿主 `value[index]`（`visit_subscript` 留有 TODO），属性查找没有
缺失钩子。用户类因此无法实现字典式容器、代理对象或计算属性，只能提供普通方法。

## 跨语言调研

| 语言 | 读 | 写 | 形式与特点 |
|---|---|---|---|
| Python | `__getitem__(self, key)` | `__setitem__(self, key, value)` | 特殊方法；切片作为单个 `slice` 对象；`__getattr__` 仅在正常查找失败后调用 |
| Ruby | `[]` 方法 | `[]=` 方法 | 方法名就是符号；支持范围/多参数 |
| Kotlin | `operator fun get(...)` | `operator fun set(..., value)` | 方括号翻译为 get/set；支持多下标；成员或扩展函数 |
| C# | indexer `get` | indexer `set` | 声明 `this[...]` 访问器 |
| Scala | `apply(args)` | `update(args, value)` | 无专用语法；调用与下标共用 apply/update |
| Rust | `Index::index` | `IndexMut::index_mut` | trait + 返回引用；写入需可变借用 |
| Swift | `subscript(...) { get }` | `set` 块 | 一个声明同时描述读写；支持多参数 |
| D | `opIndex(...)` | `opIndexAssign(value, ...)` | 名字即协议；切片对象作为参数 |
| Lua | `__index` | `__newindex` | 元方法；表键缺失时触发 |

结论：

1. **读写是两个操作**，写入的 value 在参数最后；没有语言把 `[]` 当成普通中缀运算符。
2. 切片通常作为单个 index 对象传递；多下标在 Kotlin/Swift/D 中拆成多个参数。
3. 属性读取钩子通常是“正常查找失败后的 fallback”；全量 `__setattr__` 会拦截所有字段写入，
   需要显式绕过机制（Python 的 `object.__setattr__`）。
4. Oort 已有字符串命名运算符（`def operator "+"`）与 `__iter__` 等少量特殊方法。
   下标用运算符方法更符合既有文化；属性用显式 `on_missing` 对应设计 04 的 Missing 钩子。

## 设计

### 1. 下标运算符

```oort
class Bag {
    def __init__ { this.items = {:} }

    def operator "[]"(key) { this.items[key] }
    def operator "[]="(key, value) { this.items[key] = value }
}

val b = Bag()
b["x"] = 1
print(b["x"])
b["x"] += 1
```

- `"[]"` 接收 **1 个参数**（index）；`"[]="` 接收 **2 个参数**（index、value）。
  两者都隐含接收者 `this`。
- 复用 `OortType.operators` 表，键为 `("[]", 2)` 与 `("[]=", 3)`；
  `validate_operator_definition` 为这两个符号增加受限元数例外。
- 分派顺序：用户实例先查类/继承/扩展运算符；找不到时：
  - 内置容器（List/Tuple/Dict/String 等）继续走原生 `value[index]`；
  - 用户实例报 `Type 'C' does not support subscripting`（或赋值版本）。
  内置类型保持原生行为，扩展下标运算符不会覆盖内置下标。
- 多下标 `a[i, j]` 按现有语法组成一个 Tuple 作为 index；切片 `a[1:3]` 传入 `Slice` 对象。
- 读/写分别独立：只定义 getter 时赋值报缺少 `"[]="`；反之读报缺少 `"[]"`。
- 增强赋值 `a[i] += v` 先走 getter，再走 setter。
- 扩展运算符 `def C.operator "[]"(i)` / `"[]="(i, v)` 可用，沿用词法作用域与歧义规则。

### 2. 缺失属性读取

```oort
class C {
    def on_missing(name) { "missing:" + name }
}

print(C().unknown)   # missing:unknown
```

- 查找顺序：实例字段 → 类 MRO → 元类 MRO（现有规则）→ 扩展方法 → `on_missing` → 报错。
- 仅在正常查找失败后调用；字段/方法/扩展存在时不会调用。
- `name` 是 String；返回值就是属性值。
- 递归保护：执行某个实例的 `on_missing` 时，该实例再次缺失属性不会重入钩子，而是按普通
  `OortAttributeError` 报错，避免无限递归。
- 只读：不提供 `__setattr__`/全量写入钩子；`this.x = ...` 仍直接写入开放字段袋。
- 名字是普通方法名（非 dunder），可被继承；`oort-core` 静态类显式拒绝该名字，
  因为静态属性类型无法由动态 fallback 满足。

### 3. 明确不做（本切片）

- `__getitem__`/`__setitem__`/`__getattr__`/`__setattr__` 等 Python 魔术名；
- `del a[i]`；
- 多下标拆成多个方法参数（仍按 Tuple 传递）；
- Handler 对象与 `onGet`/`onSet`/PASS 协议；
- 字段初始化器语法糖；
- 属性写钩子与计算属性 setter。

## 替代方案

1. **Python 特殊方法**：可实现且熟悉，但与 Oort 的字符串运算符风格冲突，并扩大 dunder
   特例面；放弃。
2. **`def operator "[]="` 作为普通三元运算符**：operator 表/校验按一/二元设计；改为仅对
   `[]`/`[]=` 开受限例外，避免影响其他符号。
3. **Handler 对象（设计 04 完整版）**：表达力最强，但需要 PASS 哨兵、Handler 生命周期与
   递归规则；第一切片用实例方法 `on_missing` 实现同一 Missing 钩子的最小版本。
4. **全量 `__setattr__`**：会拦截 `__init__` 与所有字段写入，需要 `object.__setattr__`
   式绕过；留待属性访问器/Handler 提案。

## 实现与测试

- `parser/operator_defs.py`：`SPECIAL_OPERATOR_ARITY` 与 `[]`/`[]=` 校验。
- `runtime/interpreter.py`：
  - `visit_subscript` / `_assign` 下标分支调用 `_find_operator` + `_invoke_operator`；
  - `visit_attribute` 在扩展 miss 后调用 `on_missing`，并用接收者 id 栈防重入；
  - 内置容器继续原生下标。
- `semantics/core/checker.py`：静态类拒绝 `on_missing`，运算符方法仍拒绝。
- 测试：`tests/unit/runtime/test_protocols.py` 覆盖读写/增强赋值/Tuple/Slice/扩展/
  fallback/递归保护/内置不变；示例 `examples/03_oop/03_03_protocols.ort`。
- 文档：规范 02/05/06、实现笔记 03/04、roadmap、CHANGELOG。

## 未决

- 多下标是否改为多参数（Kotlin/Swift 风格）。
- `del a[i]` 与属性删除。
- 属性写钩子、计算属性与 Handler/PASS 协议。
- `oort-core` 的静态下标协议与属性访问器。
