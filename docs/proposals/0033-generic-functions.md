# OP 0033：泛型函数

| | |
|---|---|
| 状态 | Implemented（B6a checker/动态路径 + B6b typed 单态化） |
| 日期 | 2026-11-28 |
| 前置 | [OP 0022](0022-generic-adts.md)（类型参数与 `ForallType`/`unify` 机制）、[design 03](../design/03-type-system-design.md) §2.5、[design 14](../design/14-core-typechecking.md) |

## 1. 动机

`oort-core` 已有泛型 ADT（`Option[T]` 等），但函数不能声明类型参数——
`def first[T](xs: List[T]) -> T` 在 checker 直接拒绝（"Generic functions
are not implemented yet"）。集合助手（`first`/`swap`/通用 `map` 类形状）与
B 段后续的 `sorted(key=...)` 都需要函数级多态。

## 2. 语言表面

```oort
def id[T](x: T) -> T { x }
def first[T](xs: List[T]) -> T { xs[0] }
def pair[T, U](a: T, b: U) -> Tuple[T, U] { (a, b) }

print(id(1), id("a"))          # 实参推断：T=Int / T=String
val xs: List[Int] = [1, 2]
print(first(xs))               # T=Int
```

- 语法沿用 enum 的类型参数声明 `[T]`/`[T, U]`；**variance 限定与上界/默认值
  显式拒绝**（与 OP 0022 对 ADT 的初始立场一致：无 traits 可作上界）；
- 返回类型**必须显式标注**（非泛型函数可省略推断；泛型体在刚性 T 下推断
  返回值语义微妙，v1 不做）；
- 函数体在**刚性类型参数**下检查一次：`T` 只能透传、装箱进 `List[T]` 等
  容器、作返回；对 `T` 使用运算符/字面量操作（`x + 1`）按现有运算符规则
  拒绝——这正是"无上界"的语义；
- 递归：体内自调用按同一泛型签名合一（`first(xs)` 绑定 T:=T 刚性），
  对应单态化后的同一实例。

**T 能绑定的种类**：基本类型、容器（含嵌套 `List[List[T]]`）、ADT 应用
（`Option[T]`）、函数类型（unify 按结构匹配）；`Set[T]`/`Dict[T, _]` 出现在
签名中被键安全检查拒绝（刚性 T 不是合法键类型，语义正确）。无值参数
（C++ non-type / Rust const generics）。

## 3. 推断

复用 OP 0022 为构造器建好的调用点机制，零新增求解器：

- **infer 模式**：逐参 `unify(param_pattern, arg_type, bindings)`；未绑定
  的参数报 `Cannot infer type argument 'T' of function 'f'; add a type annotation.`；
- **expected 模式**：期望类型（如 `val x: Option[Int] = ...`）先给返回形状
  提供绑定，再按绑定后的形参类型检查实参；
- 期望驱动的函数值特化（`val f: (Int) -> Int = id`）经
  `_check_generic_value_expected` 对整个签名合一——构造器路径已有。

调用点把求得的实例记录在 `node.metadata["generic_args"]`（按声明顺序），
供 typed 后端单态化。

## 4. 后端策略

- **动态路径（eval/vm）**：擦除。泛型函数就是普通函数（HIR 不携带类型），
  放开 `lower.py`/解释器侧的 `type_params` 拒绝即可，运行时零改动；
- **typed 路径（tvm/tbc）**：**单态化**。`lower_typed_module` 预扫描调用
  点，按 `(函数名, 实例参数)` 复制泛型函数体：结构克隆 AST、把
  `type_obj` 等元数据经 `substitute(bindings)` 代换、剥掉 `type_params`、
  改名为 `<generic:{module_id}:{name}:{N}>`，调用点重定向到实例名。体内
  递归调用在代换后同样命中 memo，落回同一实例；
- **实例名的 module_id 盐**：实例经合并 globals 表**按名字**调用（区别于
  按索引调用的 lambda），两个链接模块各自的同名私有泛型若共用同一个内部
  名会静默互相遮蔽——不是 C++ 式的链接报错，而是错误分派（见 §5 的调研
  与回归测试 `test_same_named_generics_in_linked_modules_do_not_collide`）；
- **跨模块（v1）**：checker/动态路径可用；typed 路径显式拒绝（依赖
  artifact 不携带泛型源体，需要 export kind 4 + 链接期实例化，另行设计）；
- 泛型函数作**裸值**传递（`val f = id` 后经变量调用）在推断期就报
  "Cannot infer type argument"（无实参可绑定）；期望驱动的特化值在动态
  路径可用，typed 路径暂拒绝。

## 5. 跨语言对照（调研）

OP 0022 的对照聚焦"运行时是否保留类型实参"；本节聚焦**检查模型**与
**实例化的链接语义**——泛型函数与泛型 ADT 在这两点上决策不同。

### 5.1 检查模型

| | C++ 模板 | Rust 泛型 | ML/OCaml | **Oort** |
|---|---|---|---|---|
| 体检查时机 | **每次实例化各查一遍**（鸭子类型） | 声明处一次（trait 授予能力） | 声明处一次（不透明参数） | 声明处一次（**刚性、零能力**） |
| `x + 1`（T 无约束） | 实例化时按 `operator+` 存在与否定夺 | 编译错（无 `Add` bound） | 编译错 | 编译错 |
| 能力来源 | 实例化期成员查找 | trait bound | 无（模块函子换能力） | 无（上界显式拒绝） |
| 显式指定实例 | `f<int>(x)` | `f::<i32>(x)` | `f 0`（推理为主，可注解） | ❌ 仅推断 |
| 元编程 | 图灵完备（特化/SFINAE/变参/值参数） | 受限（无特化） | 无 | 无 |

Oort 的检查侧最接近 **ML 的 prenex 多态**（`ForallType` scheme + 参数驱动的
一阶合一），而不是 C++ 模板：体只检查一次、类型参数完全不透明。这换来的
性质是：错误总在声明处报一次（不会 `f<BadType>` 时才爆），不存在
"两阶段名字查找"问题，代价是上界（traits/接口）落地前 `T` 没有任何能力。

- Rust 泛型与 trait：
  <https://doc.rust-lang.org/reference/items/generics.html>；
- C++ 模板（实例化期检查、特化）：
  <https://en.cppreference.com/w/cpp/language/templates>；
- Hindley–Milner 与 let 多态：
  <https://en.wikipedia.org/wiki/Hindley%E2%80%93Milner_type_system>。

### 5.2 实例化的链接语义（C++ 的老问题）

C++ 模板在头文件中定义，每个翻译单元各自实例化 `f<int>`，链接器需要对
弱符号做 COMDAT 折叠；ODR 要求各处实例化逐字一致，违反即是 UB
（<https://en.cppreference.com/w/cpp/language/definition>）。Rust 单态化后
的符号带 mangling（含类型实参），由符号名天然去重。Go 用字典 + GC shape
共享代码，多数实例不生成新函数
（<https://github.com/golang/proposal/blob/master/design/43651-dictionaries.md>）。

Oort v1 的结构不同：**typed 路径的泛型不跨模块**，实例化只发生在声明所在
模块内，因此不存在"多翻译单元重复实例化同一泛型"的输入形状。但实现期间
发现一个可达的近亲问题（已修复）：两个模块各有一个**同名的私有泛型**，
各自本地实例化后产生同名内部函数 `<generic:name:1>`；实例按名字经合并
globals 表调用，后加载者静默遮蔽前者，调用点跨分派到错误实例。与 C++
"链接器至少报重复符号"相比，这是**静默错误分派**，更危险。修复为实例名
携带 module_id 盐（§4）；泛型类与跨模块实例化（export kind 4）设计时要在
两条路线里选一：各模块带盐各自实例化（代码可能重复，实现简单），或
链接器按泛型源体哈希做 COMDAT 式合并（省代码，要求 artifact 携带源体
指纹）。

## 6. 与其他泛型载体的关系

Oort 的参数化多态有三个载体，**提案分开、机制共享**：

| 载体 | 决策记录 | 载体特有决策 |
|---|---|---|
| 泛型 ADT（enum） | [OP 0022](0022-generic-adts.md) | 声明处变型 + 极性检查；构造器即多态值；运行时保留实例身份 |
| 泛型函数 | 本提案 | 调用点推断 + 后端擦除/单态化；无变型 |
| 泛型类 | 未实现（显式拒绝），待 B7 typed 类之后独立提案 | 届时裁决：每实例独立槽布局、方法分发、变型是否扩展到槽 |

共享的机制与不变式（`TypeParameterType`/`ForallType`、`unify`、`substitute`、
刚性体检查、"无上界 ⇒ 参数零能力"）不在提案间复制；统一的概念框架与跨语言
取舍记录在 [design 03](../design/03-type-system-design.md) §2.5（编译期表示 /
实例化 / 布局 ABI 三层，§2.5.4 已裁决"静态侧单态化 + 动态侧擦除"）。新载体
的提案引用该框架，只记录载体特有的决策与验收。

## 7. 明确不做

上界 `T: Bound`、变型 `[out T]`、类型参数默认值、泛型方法/扩展/lambda、
泛型接口、泛型类、显式类型实参语法（`f[Int](x)`）、链接期跨模块实例化、
基于字典的统一表示（dyn dispatch）。

## 8. 测试与验收

- `tests/integration/test_core_generic_functions.py`：三目标
  （eval/vm/tvm）一致性（透传/容器/多参数/递归/期望驱动）、无法推断/上界/
  运算符误用错误、链接模块同名泛型不互相遮蔽（回归）、实例去重；
- `rust_vm_check.py` 增 `typed_generic_functions` 差分；
- 示例 `08_24_generic_functions.ort` 进 docs/examples 与 tvm 矩阵。
