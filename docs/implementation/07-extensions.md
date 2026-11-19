# 扩展方法与扩展运算符的实现

> 对应 [OP 0014](../proposals/0014-extension-methods.md) 与
> [规范 10](../spec/10-extensions.md)。

## 前端分类

`FunctionDef.names` 保存点分名字：`def C.f` → `["C", "f"]`，
`def C.operator "+"(x)` → `["C", 'operator "+"']`，
`def class.f` → `["class", "f"]`。文法无需改动。

`FunctionDef` 提供：

- `has_class_prefix`：`names[0] == "class"`；
- `is_class_method`：恰好两段且前缀为 `class`；
- `is_extension`：恰好两段且前缀不是 `class`；
- `extension_receiver`：扩展时返回 `names[0]`，否则 `None`。

Pass1（`semantics/functions.py`）的分类顺序：

1. 泛型函数拒绝；
2. 超过两段的函数名给出结构诊断（`class.A.f` 与 `A.B.f` 分开报）；
3. 类方法位置检查；
4. 扩展：类体拒绝、`__x__` 特殊名拒绝、运算符走
   `_check_operator_definition`（放宽“必须在类内”）；扩展名**不** declare/define；
5. 普通函数保持原逻辑。

`resolve_function` 为扩展设置 `OutsideDeclType.EXTENSION_METHOD`，其
`is_function` 与 `is_method` 均为 true，因此 `this`、`return`、隐式 `super`
的语义分析与普通方法一致。

## 运行时扩展表

`Environment` 持有三份状态：

```python
self.extensions: dict[tuple[OortType, str], OortFunction]
self.extension_operators: dict[tuple[OortType, str, int], OortFunction]
self.imported_extension_scopes: list[Environment]
```

- `register_extension` / `register_extension_operator`：同作用域重复注册返回
  `DefineResult.REDEFINED`；模块根/REPL（`allow_redefine=True`）允许覆盖。
- `add_imported_extension_scope(module.env)`：按身份去重；只读取该环境的
  本地两张表。
- `lookup_extension` / `lookup_extension_operator`：返回
  `ExtensionLookup(match=..., ambiguous=...)`，不抛诊断异常。

查找算法（`_lookup_extension`）：

```text
for env in self -> outer:
    local = nearest(env.table, receiver_type.mro(), suffix)
    if local: return it                     # 本地子层绝对优先
    for each imported scope:
        index, match = nearest(scope.table, ...)
        keep candidates at the smallest index
    if one unique candidate: return it       # 按函数身份去重
    if several: return ambiguous
return no match
```

`nearest` 只是按 MRO 顺序做 dict 查找，复杂度 O(作用域深度 × MRO 长度)；
只在属性/运算符 miss 时执行。

## 运行时注册与分派

`ASTInterpreter.visit_function_def`：

- 非扩展：照旧 `env.define(name, func)`。
- 扩展：`env.get(receiver_name)` 解析接收者，要求 `OortType`；构造
  `OortFunction(node, closure=self.env)`；按 `node.is_operator` 注册到运算符表
  或方法表。定义不产生普通名字。

`visit_attribute`：

1. `value.get(attr)` 命中成员/字段 → 返回；
2. `OortSuperProxy` → 直接报错，绝不回退到扩展；
3. `env.lookup_extension(value.type, attr)`：
   - 歧义 → `OortAttributeError`（列出候选来源模块）；
   - 命中 → `dispatch._bind_extension_method(receiver, func, matched_type)`；
4. 否则报属性缺失。

`_find_operator`：

1. `_get_operator_from_cls` 命中类/继承/原生运算符 → 返回；
2. `env.lookup_extension_operator(receiver.type, symbol, arity)`；
3. 命中则同样绑定为 `OortMethod`，歧义报 `OortTypeError`。

`_apply_binary` / `_apply_unary` 无需改动：`in` 查右操作数、`!=` 回退 `==`、
增强赋值与一元分派都经过 `_find_operator`。`call_value`/`apply_operator`
（集合助手 `sorted` 使用）也会走扩展兜底。

## 导入激活

- `visit_import_stmt`：加载模块、绑定模块名后调用
  `self.env.add_imported_extension_scope(module.env)`。
- `visit_import_from_stmt`：`ModuleLoader.import_names` 现在返回
  `(module, values)`，绑定名字后同样激活扩展表。
- 只读取模块环境本地的两张表，因此扩展不会传递式重导出。
- 模块缓存保证同一模块只执行一次，扩展只注册一次。

## `super` 与继承

- 绑定时 `defining_type` 是 MRO 中实际命中的类型；`super.f()` 从该类型之后
  搜索类成员。
- `OortSuperProxy.get` 在 MRO 末尾返回 `None`，使 `Object` 扩展中的
  `super.f()` 产生干净的 `OortAttributeError`，而不是 `IndexError`。
- 扩展表按 `OortType` 身份键控；类重新定义会创建新的类型对象。

## 测试

- `tests/unit/runtime/test_extensions.py`：基本调用、参数/默认值/尾随块、
  内置类型、成员/字段/类方法优先、继承、作用域与闭包、`super`、运算符、
  导入激活/歧义/非传递、重复定义、接收者错误、运行时隔离。
- `tests/unit/frontend/test_ast.py`：AST 属性。
- `examples/03_oop/03_02_extensions.ort`：端到端示例。
- `benchmarks/test_extensions.py`：成员调用 vs 扩展调用 vs 扩展运算符。
