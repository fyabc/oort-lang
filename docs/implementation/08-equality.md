# 相等性实现

> 对应 [OP 0016](../proposals/0016-equality-protocol.md) 与
> [规范 02](../spec/02-expressions.md#相等与成员测试)。

## 值相等

`ASTInterpreter.values_equal` 是值相等的入口：

- 身份短路（`lhs is rhs`）后，List/Tuple 逐元素递归，Dict 比较键与值，
  Set 使用键协议；
- Bool/Int 显式分支保证嵌套层严格区分；Int/Float 按宿主数值比较；
  Null/String 单独处理；
- 其他对象（用户实例、Type、Function、Module）回退到
  `apply_operator("==")`，因此用户 `operator "=="`、扩展运算符与错误传播
  都走正常分派；
- List/Tuple/Dict 的递归使用 `(id(left), id(right))` memo；已访问对象对
  直接返回真，支持循环容器；
- `NativeContext.equal` 暴露该操作给 CONTEXT 原生运算符。

## 键协议

Dict 键与 Set 元素继续使用底层 Oort 对象容器：

- Bool/Int 严格（不同 `__eq__`）；
- Int/Float 键不同（`OortInt.__eq__`/`OortFloat.__eq__` 不跨类型）；
- Tuple 递归使用 OortTuple 的 `__eq__`/`__hash__`；
- Type/Function/Module/用户实例按身份；
- List/Dict/Set 不可哈希。

因此 Dict/Set 的键查找、相等与集合代数不需要 HOST 投影。用户自定义 `==`
不会影响键身份；未来 `operator "hash"` 提案负责自定义键协议。

## 原生运算符模式

- List/Tuple/Dict 的 `==` 与 List/Tuple 的 `in`：`NativeMode.CONTEXT`，
  通过 `NativeContext.equal` / `contains` 递归调用。
- Dict 的 `in`、Set 的 `==`/`in`/`& | ^ -`：`NativeMode.VALUE`，直接操作
  Oort 容器，避免 `host_value` 深拷贝与 Bool/Int 合并。
- 内建运算符安装函数 `_install_operators` 支持 `mode=` 参数。

## 测试

`tests/unit/runtime/test_equality.py` 覆盖：

- Bool/Int 嵌套严格（List/Tuple/Dict/Set）；
- Int/Float 值相等但键区分；
- Dict/Set 相等、成员与集合代数；
- 用户 `==` 在容器值中生效、键仍按身份；
- List vs Tuple 类型敏感；
- 循环容器对象对 memo。
