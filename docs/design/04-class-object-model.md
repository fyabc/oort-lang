# 类与对象模型设计

> 整理自项目早期的设计讨论（原始记录未纳入仓库）。

---

## 1. 对象模型概览

Oort 的对象模型建立在 **"一切皆对象"** 的原则之上。类本身也是对象，由元类（Metaclass）描述其创建行为。对象模型的核心关注点：

- **统一性**：实例调用和类调用使用同一套查找逻辑
- **正交性**：子类型关系（`<:`）与实例关系（`::`）是两个独立维度
- **渐进类型兼容**：对象模型不阻碍静态分析，属性查找路径可预测
- **DSL 友好**：通过词法作用域机制支持隐式接收者

### 1.1 核心数据结构

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Instance   │     │    Class    │     │  Metaclass  │
│             │     │             │     │             │
│ klass ──────┼────►│ klass ──────┼────►│ klass ──────┼──► ...
│ fields (Bag)│     │ super       │     │ super       │
│             │     │ instance_dict│    │             │
└─────────────┘     │ class_dict  │     └─────────────┘
                    │ meta_type   │
                    │ name        │
                    └─────────────┘
```

- **Instance**：普通对象，包含类型指针 `klass` 和动态属性字典 `fields`
- **Class**：类对象，包含实例方法表 `instance_dict`、类方法表 `class_dict`、父类指针 `super`、元类类型指针 `meta_type`
- **Metaclass**：元类对象，控制类的创建过程和类级别行为

### 1.2 方法存储位置

| 方法类型 | 调用方式 | 存储位置 | `self` 绑定 |
|---------|---------|---------|------------|
| 实例方法 | `obj.method()` | `Class.instance_dict` | 实例对象 |
| 类方法 | `Class.method()` | `Class.class_dict` | 类对象 |
| 静态方法 | `Class.static()` | `Class.instance_dict`（无绑定标记） | 无 |

**设计依据**：采用 Smalltalk/Ruby 模型而非 Python 模型。类方法的存在位置决定了它的行为，无需 `@classmethod` 等特殊标记。查找链一致——`dog.speak()` 和 `Animal.count()` 走完全相同的查找逻辑。

---

## 2. 元类系统

### 2.1 设计选型

**选择 Smalltalk/Ruby 模型**，并在此基础上做扁平化和共享优化。

| 特性 | Smalltalk | Python | **Oort** |
|------|-----------|--------|---------|
| 元类创建 | 自动，每类唯一 | 手动，多类共享 | **手动定义，多类共享** |
| 元类继承 | 平行镜像类继承链 | 独立继承链 | **扁平独立** |
| 类方法存储 | 元类实例中 | `__dict__` + 描述符 | **类对象 `class_dict`** |
| 类方法语法 | `def self.f` | `@classmethod` | **`def class.f`** |

### 2.2 核心决策

1. **扁平化元类**：类的继承链与其元类的继承链**无关**（参考 Newspeak）。`Dog < Animal` 不意味着 `DogMeta < AnimalMeta`
2. **共享元类类型**：多个类可以共享同一个元类类型。默认所有类共享全局 `DefaultMeta`
3. **类方法直接存储**：类方法存储在 `Class.class_dict` 中，而非元类实例的方法表。元类仅在类创建阶段发挥作用
4. **隐式元类创建**：当类定义中出现 `def class.f` 语法时，若尚未指定元类，解释器自动创建隐式元类 `ClassName#Meta`

### 2.3 两层宇宙与自反终止

```
实例层:  x :: C           # x 是类 C 的实例
类层:    C < Object :: M  # C 继承 Object，C 是元类 M 的实例
元类层:  M < Type         # 元类 M 继承 Type
顶层:    Type :: Type     # 自反终止
```

- **`Type` 是元类的基类**，所有元类必须直接或间接继承 `Type`
- **`Type :: Type`**：Type 是自身的实例，终止无限递归
- **`Type < Object`**：元类本身也是对象（可调用方法、持有属性）
- **`Object :: Type`**：Object 是 Type 的实例（所有类默认是 Type 的实例）

**Type/Object 交叉依赖**（非循环）：

```
Type < Object    # 子类型关系：元类是对象的子类
Object :: Type   # 实例关系：Object 是 Type 的实例
Type :: Type     # 自反终止
```

这两条关系正交，不构成逻辑循环。编译器引导阶段通过 `setup_type_system()` 特殊处理：先创建 `Object` 和 `Type`，再通过 `unsafe_set_instance_of` 建立交叉关系。

### 2.4 元类层级限制

禁止创建超过两层的元类层级。错误处理：

```oort
metaclass MetaType < Type       # ✓ 允许
metaclass Forbidden < MetaType  # ✗ 编译错误:
    # "Metaclass hierarchy exceeds 2 levels.
    #  Type :: Type is the termination point."

class BadMeta < Object          # ✓ 允许（普通类）
class C < Object :: BadMeta     # ✗ 编译错误:
    # "Metaclass must be a subclass of Type, but BadMeta <: Object"
```

---

## 3. 类声明语法

### 3.1 统一子类型符号 `<`

```oort
class A < B, I1, I2
```

- `<` 统一表示子类型关系（`A <: B`, `A <: I1`, `A <: I2`）
- 编译器根据 `B`/`I1`/`I2` 的类型种类（class / interface / mixin）自动区分语义
- 类型理论层面，"继承类"和"实现接口"都贡献相同的子类型关系

### 3.2 元类实例符号 `::`

```oort
class A < B, I1, I2 :: M
```

| 语法片段 | 含义 | 类型理论对应 |
|---------|------|------------|
| `A < B` | A 是 B 的子类型 | `A <: B` |
| `A :: M` | A 是元类 M 的实例 | `A : M` |

`::` 的选择理由：
- 在类型理论中常用于表示 kind 层级（类型的类型）
- 视觉上暗示"层级上升"，与 `<` 形成互补：`<` 表示横向子类型关系，`::` 表示纵向实例/类型关系
- 避免与类型注解 `:` 混淆

### 3.3 `metaclass` 关键字

提供可选的 `metaclass` 关键字作为语法糖，提升可读性：

```oort
metaclass ValidatingMeta < Type {
    def class.validate_schema() -> Bool { ... }
}
# 等价于: class ValidatingMeta < Type { ... }
```

- **底层机制**：保留统一 `class X < Y` 语法，根据 `Y <: Type` 自动判定元类
- **工具链支持**：编辑器高亮 `metaclass`，编译器对未标记的元类发出警告

### 3.4 元类参与类型检查

类型检查器维护两类关系图：`subtype_graph`（A <: B）和 `instance_graph`（C :: M）。

关键推导规则：
- **Instance-Declare**：`class C :: M` 且 `M <: Type` → `C :: M`
- **Metaclass-Subtype**：`C :: M1` 且 `M1 <: M2` → `C :: M2`

```oort
metaclass ValidatingMeta < Type {
    def class.validate_schema() -> Bool { ... }
}
class User < Object :: ValidatingMeta { ... }

User.validate_schema()  # ✓ 类对象可调用元类方法
let x: User = User()
x.validate_schema()     # ✗ 实例无此方法
```

---

## 4. 属性查找（Slot-Bag-Handler 模型）

> **实现状态**：`oort-object` 只实现 Bag（开放实例字段）与简化的 MRO 查找。
> `oort-core` 薄探针已实现固定 Slots（声明、初始化顺序、确定赋值、`val` 只读）；
> Handler 进一步排在扩展方法/属性协议之后。

### 4.1 三层内存模型

- **Slots（槽）**：类定义时声明的固定属性/方法，访问速度快，支持 Getter/Setter
- **Bag（袋）**：实例运行时的动态属性字典，支持任意添加
- **Handler（处理器）**：可选的拦截器对象，用于 AOP、代理或 ORM 映射

### 4.2 设计理念

1. **声明优先**：类定义的属性优先级高于动态添加的属性
2. **读写分离**：读取和设置的查找路径略有不同，支持只读/计算属性
3. **显式拦截**：通过 Handler 对象实现，而非 `__getattr__` 等魔术方法名
4. **元类隔离**：元类仅影响类对象本身，不介入实例查找

### 4.3 属性读取 `a.x`

1. **Handler 拦截**：`handler.onGet(a, 'x')`，可返回 `PASS` 继续后续查找
2. **类层级 Slot/方法**：沿继承链查找 → Property 调用 getter / Method 返回绑定方法 / Slot 直接读值
3. **实例 Bag**：`a.bag['x']`
4. **Missing 钩子**：`a.onMissing('x')`，未定义则抛 `AttributeError`

### 4.4 属性设置 `a.x = value`

1. **Handler 拦截**：`handler.onSet(a, 'x', value)`
2. **类层级 Slot/属性**：Property → setter / Slot → 写内存 / Method → **报错**（禁止覆盖方法）
3. **实例 Bag**：`a.bag['x'] = value`

### 4.5 方法绑定规则

- 来自类层级 Method → 自动绑定 `this`
- 来自实例 Bag 的普通函数 → **不绑定** `this`（避免 Python/JS 的 this 丢失问题）

### 4.6 元类隔离

- **实例查找**：`a` → `Class(a)` → `Parent(Class(a))`。**不直接查找元类**
- **类查找**：`A` → `Metaclass(A)` → `Parent(Metaclass(A))`

### 4.7 含 Mixin 的完整查找顺序

```
Handler → 本地 Slot → Traits/Mixins (按引入顺序逆序) → 父类 → 实例 Bag → Missing Hook
```

### 4.8 性能优化

- **内联缓存（Inline Caching）**：对热点属性缓存查找结果
- **避免递归**：Handler 中访问自身属性需特殊标记

---

## 5. Mixin/Trait 支持

### 5.1 Mixin 与类的核心差异

| 特性 | 普通类 (Class) | Mixin / Trait |
|------|---------------|--------------|
| 核心隐喻 | "Is-A"（分类） | "Can-Do"（能力组合） |
| 实例化 | 可直接实例化 | **禁止直接实例化** |
| 完整性 | 自包含 | 通常不完整，依赖宿主类 |
| 状态 | 拥有独立字段 | **建议无字段**（或抽象状态访问） |
| 构造函数 | 独立 `init` | 链式 `init`（通过 `super()` 串联） |

### 5.2 状态管理策略

**推荐方案：Trait 无字段**（Rust 风格）

- Trait 只能定义方法签名和默认实现
- 若需访问状态，通过抽象方法（getter/setter）要求宿主类提供
- 保持对象内存布局扁平（Flat Layout），利于 JIT 优化和 FFI

若允许状态（备选方案）：
- 编译器在类实例化时将所有 Mixin 字段线性化合并到主对象中
- 冲突检测：若多个 Mixin 定义同名字段，类创建时报错

### 5.3 MRO 与 C3 线性化

采用 **C3 线性化算法** 确定方法解析顺序：

- 保证单调性（子类优先于父类）
- 保证局部优先次序（声明在前的 Mixin 优先）
- 避免钻石继承问题（Diamond Problem）

```oort
class Bird < Animal, Flyable, Serializable
# MRO: Bird → Flyable → Serializable → Animal → Object
```

### 5.4 `super()` 语义

`super()` 不是"调用父类"，而是 **"调用 MRO 链中的下一个"**：

- 对 Mixin 的可组合性至关重要
- `super` 必须是动态绑定的（基于 MRO），而非静态绑定到父类
- 当 Mixin 调用 `super()` 且位于 MRO 链末端时，指向基类 `Object`

### 5.5 冲突处理

- **默认报错**：若两个 Mixin 有同名方法且默认实现不同，编译期报错
- **显式解决**：提供重命名和覆盖语法
  ```oort
  class C < Object, A, B {
      override def foo() { A::foo() }  # 显式选择 A 的实现
  }
  ```

### 5.6 Orphan Rule（孤儿规则）

跨模块 Trait 实现需遵守孤儿规则（参考 Rust）：

- **不能**为"外部类型"实现"外部 Trait"
- 必须在类型定义所在模块或 Trait 定义所在模块进行实现
- 防止不同模块对同一 (Type, Trait) 组合产生冲突实现

```oort
# 模块 A 定义了 UserId
# 模块 B 定义了 JsonSerialize
# 模块 C 不能同时为 UserId 实现 JsonSerialize（除非 C 定义了其中之一）
```

### 5.7 Self 类型支持

Trait 内部允许引用 `Self` 类型，表示"最终实现该 Trait 的具体类"：

```oort
trait Cloneable {
    def clone() -> Self { ... }
}
```

---

## 6. `this` 绑定策略

### 6.1 核心决策

**显式 `this` 为默认，仅在 DSL 作用域块中允许隐式。**

| 特性 | 决策 | 理由 |
|------|------|------|
| `this` 绑定方式 | **词法作用域变量** | 支持闭包捕获，对 DSL 嵌套至关重要 |
| `this` 类型签名 | **接收者参数** | 保证渐进类型的可推断性 |
| `this` 语法可见性 | **默认显式** | 保护类型推断，明确符号来源 |
| 成员访问歧义 | **强制前缀**（`this.` 或 `@`） | 区分局部变量和成员变量 |
| 动态性 | **词法绑定，非 JS 式动态 `this`** | 避免类型推断灾难 |

### 6.2 模型选择

**采用 `this` 为词法作用域变量**（Java/C#/Kotlin 模式）：
- 方法签名中不包含 `this`，函数体内有特殊标识符 `this`
- 闭包自然捕获 `this`，DSL 嵌套流畅
- **绝对禁止** JS 式动态 `this`（由调用方式决定），编译器无法静态确定类型
- Oort 采用**词法绑定**：`this` 在定义时确定，而非调用时

### 6.3 DSL 支持：Lambda with Receiver

引入 `with`/`apply` 作用域块，在块内允许隐式 `this`：

```oort
class Player {
    def move(dx, dy) {
        this.x += dx       # 显式 this（普通类方法）
        this.y += dy
    }
}

# DSL 场景
build_rect {
    x = 10          # 隐式 this.x（with 块内）
    y = 20
    color("red")
}
```

类型系统层面，`this` 是签名的一部分：`let f: Rect.() -> Int = rect.area`

嵌套 DSL 块中使用标签语法访问外层：`this@UI.title = "Main"`

### 6.4 避坑清单

1. ❌ 不做 JS 式动态 `this`（由调用方式决定）
2. ❌ 不做 Python 式显式 `self` 参数（DSL 噪音过大）
3. ❌ 不混淆实例变量和局部变量（`x = 1` 必须是局部赋值）
4. ✅ 成员变量强制前缀（`this.x` 或 `@x`），局部变量无前缀

---

## 7. 扩展方法

> **实现状态**：已实现（[OP 0014](../proposals/0014-extension-methods.md)，
> 规范见 [10-extensions.md](../spec/10-extensions.md)）。

### 7.1 核心设计

- **动态分发**：基于运行时类型 + MRO 查找（非 Kotlin 式静态解析）
- **词法作用域**：扩展方法可见性由定义位置与 `import` 控制
- **外部调度表**：存储在 `Environment` 中，不修改目标类（非 Monkey Patching）
- **成员/字段/类内运算符优先**：普通查找成功时永远不查扩展

### 7.2 实现机制

`Environment` 通过链式 `outer` 指针形成作用域链。每个环境持有
`extensions[(TargetType, Name)]` 与
`extension_operators[(TargetType, Symbol, Arity)]` 两张表。

查找**先按作用域分层，再按 MRO 具体度**：

```python
def lookup_extension(self, receiver_type, name):
    for env in self -> env.outer:                 # 1. 词法作用域：内层优先
        # 1a. 本地扩展绝对优先（即使导入的扩展更“具体”）
        for cls in receiver_type.mro():
            if (cls, name) in env.extensions:
                return env.extensions[(cls, name)], cls

        # 1b. 本层导入的模块合成一个候选池，按 MRO 距离取最具体
        best = min over scopes of mro_index(scope, receiver_type, name)
        candidates = [matches at best]
        if len(unique(candidates)) > 1:
            raise AmbiguousExtension(...)          # 调用点报歧义
        if candidates:
            return candidates[0]
    return None
```

旧版伪代码是 MRO-first（外层循环遍历 MRO），会让外层更具体的扩展压过内层
扩展，与词法作用域直觉冲突；现已改为作用域分层优先。

### 7.3 调用分发优先级

1. 实例字段、实例/类原生方法（动态查找）
2. 扩展方法（动态解析 + 作用域链）；类内运算符同样先于扩展运算符
3. 抛出 `AttributeError`

### 7.4 作用域与语法示例

```oort
def Int.double: this * 2
def String.shout: this + "!"

print("hello".shout())  # hello!

def local_scope() {
    def List.second: this[1]
    [1, 2, 3].second()  # ✓ 作用域内可用
}
# [1, 2, 3].second()    # ✗ 离开作用域后失效
```

- `import` / `from` 激活被导入模块顶层定义的扩展；非传递、不导出。
- 扩展运算符与扩展方法共用上述规则；类/原生运算符永远优先。
- **性能优化**：扩展查找只在普通属性/运算符 miss 时发生；当前不做内联缓存，
  基准见 `benchmarks/test_extensions.py`。

### 7.5 参考语言对比

| 特性 | Kotlin | Groovy | Ruby Refinements | **Oort** |
|------|--------|--------|-----------------|---------|
| 分发 | 静态 | 动态 | 动态 | **动态** |
| 作用域 | Import | Import (全局) | 词法块 | **词法环境** |
| 优先级 | 成员 > 扩展 | 成员 > 扩展 | 扩展 > 成员 | **成员 > 扩展** |

---

## 8. 与其他语言对比

### 8.1 元类系统

| 语言 | 元类模型 | 类方法存储 | 元类继承 | 类型系统 |
|------|---------|-----------|---------|---------|
| Smalltalk | 隐式，每类唯一 | 元类实例 | 平行镜像 | 无 |
| Python | 显式 `type` | `__dict__` + 描述符 | 单继承 | 弱 |
| Ruby | 隐式 eigenclass | eigenclass | 每对象独立 | 无 |
| CLOS/MOP | 一等对象 | 泛化函数 | 可定制 | 内省 |
| **Oort** | **显式，扁平** | **`class_dict`** | **扁平** | **参与检查** |

### 8.2 属性查找

| 特性 | Python | Ruby | **Oort** |
|------|--------|------|---------|
| 属性本质 | 描述符 + 字典 | 方法 | **Slot + Bag + Handler** |
| 实例覆盖类 | 允许 | 允许 | **默认禁止** |
| 拦截机制 | `__getattr__` | `method_missing` | **Handler 对象** |
| 元类介入 | 介入实例查找 | N/A | **仅影响类对象** |

### 8.3 `this` 绑定与扩展方法

| 语言 | `this` 模型 | 绑定方式 | 扩展分发 | 扩展作用域 |
|------|-----------|---------|---------|-----------|
| Python | 显式 `self` | 第一参数 | N/A | N/A |
| JavaScript | 隐式动态 | 调用时决定 | N/A | N/A |
| Kotlin | 隐式 | 词法 | 静态 | Import |
| Ruby | 隐式 | 词法 | 动态 | 词法块 |
| **Oort** | **显式 + DSL 隐式** | **词法** | **动态** | **词法环境** |

---

## 9. 参考资料

- **元类**：Smalltalk-80 Metaclass / Python `type` 元类 / Newspeak 扁平化 / CLOS MOP / Raku 6model
- **属性查找**：Python 描述符协议 / Ruby `method_missing` + eigenclass / JS Proxy
- **Mixin/Trait**：Rust Trait (无状态, Orphan Rule, Self) / Scala Trait (线性化) / C3 线性化 / Swift Protocol Extension
- **`this` 绑定**：Kotlin Lambda with Receiver / Ruby `instance_eval` / JS 箭头函数词法 `this`
- **扩展方法**：Ruby Refinements (`refine`/`using`) / Groovy `@ExtensionModule` / Kotlin Extension Function
