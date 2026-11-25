# 更新日志

本文件记录本项目所有值得注意的变更。
格式基于 [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)，
本项目遵循 [语义化版本](https://semver.org/)。

## [0.6.0] - 2026-11-25

### 新增

- **oort-core 类型化后端**（design 15、OP 0027）：`-t thir` 打印逐模块 typed
  HIR，`-t tbc` 把 typed units 编译并链接成 typed 字节码后反汇编，`-t tvm`
  执行同一链接结果。每个模块产出 v12 artifact（module id、export/import 表、
  ABI hash、构造器表），由 linker 校验 ABI 并重定位；kind=2 链接 bundle 可被
  Rust VM 直接消费，或用 `oort-vm --link` 原生链接 v12 artifact。typed 子集
  覆盖标量、String、List/Tuple/Set/Dict、单态与泛型 ADT、完整模式匹配、
  命名函数值、非捕获 lambda 与捕获闭包（含写共享 cells）。
- **oort-core 集合表面**（OP 0031）：`in`/`!in`、List/Dict 下标写入、
  List/Tuple/String 切片读、Set 的 `| & - ^` 以及 `< <= > >=` 子集/超集比较；
  非集合操作数的诊断会区分“集合关系”与普通比较。
- **oort-core 排序与拼接**（OP 0032）：List `+`、List 字典序（元素限
  Int/Float/String）与 `sorted(xs)`（稳定升序，返回新 List）；不可排序元素与
  混合列表在检查期拒绝。
- **类型化编译缓存**（OP 0030）：按源码、编译器版本、模块 id 与直接依赖接口
  哈希寻址的 `.obc` 缓存；single-flight 写锁、sidecar、LRU 限额、统计与清理；
  CLI 提供 `--cache-dir`、`OORT_CACHE_DIR`、`--no-cache`、`--cache-stats`、
  `--cache-clean`、`--cache-max-size`。
- **任意精度整数**：Rust 动态 VM 使用 i64 快速路径，溢出后提升为 `BigInt`；
  Rust typed VM 的 `Int` 始终为任意精度。`.obc` 增加 tag 6 大整数常量
  （kind=0 仍为 v2）。混合 Int/Float 比较使用精确有理数，NaN 排序与 Python
  一致；`//`/`%` 采用向下取整。
- **标准诊断输出**：CLI 诊断改为 GCC/Clang 风格
  `file:line:col: error[Kind]: message` + 源码行 + caret，输出到 stderr；
  新增 `--color=auto|always|never`（遵循 `NO_COLOR`/`FORCE_COLOR`），
  `--plain` 等价于不彩色；汇总行只在数量非零时打印，rich 仅用于 REPL。
- **Rust VM 调试工具**：运行时错误使用 `.obc` 位置表，首行给出来源位置并追加
  `note: called from ...` 调用帧；`--trace` 逐指令跟踪到 stderr；`--disasm`
  打印 kind=0/1/2 反汇编，`--disasm --link` 先链接 v12 artifact 再打印。
- **object→core 边界原型**（OP 0028）：object 入口可导入 core 模块；core
  模块编译为 typed 字节码执行，边界做参数/返回值守卫与容器深拷贝，ADT 按模块
  origin 区分与复制；core→object 导入仍显式拒绝。
- **示例**：新增 `08_15`–`08_23`（typed 子集、集合、ADT、模式、函数值、
  闭包、集合表面、排序）与 `09_00_object_calls_core` 边界示例。

### 变更

- 默认后端仍是 `-t vm`。Python `eval`/`vm`/`tvm` 进入冻结状态（只修 bug），
  新的执行语义只进入 Rust VM。
- `-t tvm` 不再执行 typed HIR，改为执行链接后的 typed 字节码；`-t thir`
  成为逐模块 typed HIR 调试视图。旧的 HIR 合并 linker 已删除，artifact loader
  是唯一的执行 linker。
- 诊断不再带时间戳、logger 名或 rich 折行；`-t` 帮助文本修正为
  `thir/tbc/tvm` 的真实语义。
- `.obc` 版本：typed proto **v10**、单模块 artifact **v12**、链接 bundle
  **v5**；kind=0 保持 **v2**。

### 修复

- typed 顶层 block 捕获 main 局部变量时 `STORE_OUTER` 失败（main 现在同样
  参与 creator 链与 cell 槽）。
- i64 范围外的大整数常量无法写入 `.obc`。
- Python 3.11 下测试 argv 中选项位于位置参数之后触发 `SystemExit: 2`。

### 工程化

- Rust `typed.rs` 按职责拆为 `typed/{mod,decode,link,value,opcodes,vm}.rs`；
  kind=0 操作码常量与名字表移到 `opcodes.rs`，VM、trace 与反汇编共用。
- `scripts/rust_vm_check.py` 覆盖动态/typed 差分、错误路径（两边失败且源行
  一致）、trace 与反汇编；Rust 单测 33 项。
- Python 测试默认只跑 `tests/`；benchmarks 需显式 `pytest benchmarks/`。

## [0.5.0] - 2026-11-22

### 新增

- **oort-core 静态接口**（OP 0026）：`interface I { def m(x: Int) -> Int }`
  声明只有方法签名、没有状态/构造器的契约；类用 `class C < Base, I1, I2`
  实现（至多一个类基类且必须第一），接口用 `interface J < I1, I2` 继承。
  接口要求的方法参数精确、返回协变；接口类型可用于参数/变量/返回值/槽/
  集合/ADT，运行时仍是类实例并按身份相等。接口是纯静态的：声明与接口基项
  在 HIR/解释器执行时擦除，`.obc` 不变；`from` 导入接口名报 type-only 导出。
  默认方法、属性访问器、泛型接口与 `Self` 仍显式拒绝。
- **oort-core 静态类单继承**（OP 0025 增量 B）：`class Derived < Base`；子类沿
  基类链继承槽与方法，可覆盖方法（参数精确、返回协变），`super.__init__(...)`
  与 `super.method(...)` 分别调用基类构造器/方法。类引入名义子类型：
  `Derived` 可赋给 `Base`，分支合并取最近公共基类；函数类型参数改为逆变。
  继承槽纳入确定赋值分析（`super.__init__` 视为初始化基类未赋值槽）；无
  `__init__` 的派生类要求继承槽均有初始化器且继承构造器不带参数。多类继承
  与属性访问器仍显式拒绝（接口由 OP 0026 实现）。运行时/HIR/VM 复用已有 bases/MRO/`SUPER`，
  字节码格式不变。
- **oort-core 跨模块类型标注**（OP 0025 增量 A）：模块检查结束时快照本模块
  声明的类与 enum 到独立的类型导出，`m.Shape` / `m.Color` / `m.Tree[Int]`
  可用于参数、变量、返回值、槽与集合标注；`from` 导入类会同时绑定构造器值
  与类类型，enum 类型名只能模块限定（`from "m" import E` 报
  type-only 导出诊断，提示 `m.E`）。类型标注检查后擦除，运行时与 `.obc`
  格式不变；预置 `Option`/`Result` 与导入类型不会被再导出。
- **oort-core 泛型 ADT**（OP 0022 增量 A）：`enum Maybe[T] { Just(value: T), Nothing }`
  形式的类型参数声明与 `Maybe[Int]` 类型应用。构造器类型实参由期望类型
  （`val x: Option[Int] = Some(1)`、`Some([])`）或实参类型（`Some(1)`）确定；
  无法推断（`val x = None`）或冲突时显式报错。`match` 按 scrutinee 的实参
  代换构造器载荷类型；支持自递归泛型载荷（`MyList[T]`）。类型参数在 HIR/字节码
  前擦除，解释器与 VM 无改动。上界与类型参数默认值仍未实现。
- **oort-core 声明处变型**（OP 0022 增量 B）：泛型 enum 的类型参数可写
  `[out T]`（协变）/ `[in T]`（逆变），缺省不变型。声明处按 payload 使用
  位置做极性检查：函数参数翻转、内建不可变集合保持协变、嵌套 ADT 按声明
  变型复合（不变型实参把出现位置压成不变）；`enum Bad[out T] { B(f: (T) -> Int) }`
  等误用定位到字段报错。`out` 仍是普通标识符；非法变型文本由 AST builder
  报语法错误。当前无子类型（继承/接口），变型关系尚不可观察，但检查已启用，
  `is_assignable` 也按变型逐参比较，为后续对象模型预置健全性。
- **oort-core 内建 `Option` / `Result`**（OP 0022 增量 C）：每个 core 模块
  隐式获得 `Option[out T]`（`Some`/`None`）与 `Result[out T, out E]`
  （`Ok`/`Err`），无需 import。预置以普通 AST 节点注入语义分析前的模块
  （`-t ast` 不注入），`Option`/`Result` 与四个构造器是模块级保留名，
  预置构造器不进入模块导出；固定名义 origin 使 `Option[Int]` 跨模块
  统一。类型参数继续在后端擦除，解释器/VM/`.obc` 无改动。
- **oort-core 完整模式匹配**（OP 0023）：`match` 支持字面量模式（Int/Float/
  String/Bool，可带 `-`）、元组模式（`()`、`(p1, p2)`；`(p)` 为分组）、或模式
  `p1 | p2` 与守卫 `pattern if cond => body`；scrutinee 扩展到
  Bool/Int/Float/String/Tuple。穷尽性改为 Maranget usefulness 的嵌套检查
  并报告具体 witness（如 `Some(false)`、`(false, _)`）；守卫 arm 不计入覆盖。
  解释器与 VM 同步实现，`.obc` 版本升到 2（模式字面量值 + guard 字段，仍兼容
  读取 v1）。决策树编译留作后续性能切片。
- **oort-core ADT 相等与槽对象相等**（OP 0024）：ADT 采用结构化值相等
  （同构造器、载荷递归比较），可用于 `==`/`!=`、容器相等，以及 `Dict`/`Set`
  键（key-safe 载荷；Bool/Int 严格、Int/Float 键不同）。静态类实例采用身份
  相等/键；类实例仍不可打印。含函数载荷的 ADT 相等、含 List/Dict/Set/函数
  载荷的 ADT 作键在检查期显式拒绝。
- **oort-core 函数返回类型推断**（OP 0005）：顶层 `def`、`do` lambda 与**类方法**
  可省略返回标注，从各 `return` 类型与尾表达式类型合并推断；lambda 还可由期望
  函数类型下推返回类型（`val f: (Int) -> Int = do(x: Int) { x }`）。类方法按调用
  依赖**拓扑序**推断（被调者先推，回填 `class_type.methods`）。**递归函数/方法
  仍需显式返回标注**（对齐 Kotlin/Scala）。推断类型正确跨模块导出。新增
  [design 14](docs/design/14-core-typechecking.md) 记录已实现的双向检查/局部推断
  算法与跨语言对比。

### 变更

- **默认执行后端切换为寄存器 VM**（`-t vm`）：文件与 `-c` 执行默认走共享
  HIR/32 位字节码的 VM；`-t eval` 树遍历解释器保留为回退选项，REPL 仍用
  eval。切换依据 design08 §6.2 门禁：差分一致性通过，fib(15) 2.92×、
  loop10000 2.05× 稳定 ≥2×（以 fib/loop 为口径）；method dispatch 1.44×
  为已知弱项，待调用点缓存继续优化。启动增加约 25 ms 一次性模块 import
  成本。注意：VM 下部分子集外构造在**编译期**拒绝（解释器在运行期），
  诊断措辞/时机略有差异，见 [spec 06](docs/spec/06-conformance.md)。
- `.obc` 格式 version 升到 **2**（OP 0023）：pattern 字面量值以 tagged 常量
  追加、MatchArm 增加 `opt<u32>` guard 字段；`read_obc` 仍接受 version 1。
  Rust spike 同步接受 v2。
- 浮点字面量要求整数部分（OP 0021）：`PointFloat` 收紧为
  `Digit+ '.' Digit+`，`.5` 不再合法（写作 `0.5`）；与既有 `1.` 禁用
  对称。解析失败时附带 `Leading-dot floats are not supported; did you
  mean '0.5'?` 提示。`0.5`/`1.5e3`/`2e3` 不受影响。

### 修复

- 诊断消息分类与定位（OP 0020，方法论对齐 Python 3.10+）：
  - 词法错误（如未闭合的字符串 `'1`）转换为带位置与源码行的 Oort 诊断
    并以非零码退出；此前 ANTLR 词法错误直接透出到 stderr，且程序可能以
    退出码 0 静默"成功"。消息按类别命名：
    `Unterminated string literal`、`Unterminated triple-quoted string
    literal`、`Invalid character 'x' (U+XXXX)`（Python 风格码点）；
  - 定界符错误指向根因而非解析器放弃处：`{: '1':` 报
    `'{:' was never closed`（指向开括号），`]` 报 `Unmatched ']'`；
    级联解析错误被替换为该单条诊断；REPL 的未闭合判定与 EOF 诊断同步
    受益。
  - Python 习惯的 `{1, 2}` / `{1: 2}` 在解析失败时附带
    `Did you mean a Set/Dict literal …?` 警告（定向 did-you-mean），
    指向 Oort 的 `{. … .}` / `{: … :}` 定界符。
  - Python 习惯建议：`None`/`True`/`False`/`self` 的名称错误与
    `&&`/`||`/`!` 的运算符错误附带 `(did you mean …?)`（解释器运行期与
    VM 编译期拒绝均附带）；`val d = {}`（空代码块陷阱）、行首 `//`
    （注释习惯）、`i++`（无后缀运算符）、`lambda`、条件内 `=` 附带
    SyntaxWarning 提示。
  - 新增 `--plain` 选项：诊断输出不走 rich 控制台、每条记录一行，
    避免折行拆断消息，便于管道处理。

### 工程化

- import-linter 分层契约纳入 `hir`/`bytecode`（driver > bytecode > hir >
  runtime|semantics > parser > ast|diagnostics > source；VM 执行器到
  bytecode 的两条边显式豁免）。
- README 与 CONTRIBUTING 的目录结构同步补上 `hir/`、`bytecode/`；新增
  AGENTS.md 与「结构同步清单」，防止新顶层包造成文档/契约漂移。
- 新增 `scripts/profile_run.py`：单程序 cProfile 热函数报告与计时
  （`-t eval|vm`、`--repeat`、`--sort`）。

### 文档

- 新增 [spec 12](docs/spec/12-hir-bytecode-vm.md)：HIR、32 位字节码编码与寄存器 VM
  的正式规范（类型擦除后端；指令集、调用约定、闭包/cell、显式拒绝、差分一致性）。
  收口 design 13 预留的「正式规范」项；同步修正 design 13/02、spec index/11 中
  「`-t eval` 仍是默认」的过时表述（默认已是 VM）。
- `oort-lang 0.4.0` 已发布到 PyPI；README 增加 PyPI 徽章与 `pip install oort-lang`
  安装说明，Getting Started 补充 PyPI 与源码安装路径，并链接到发布流程文档。

## [0.4.0] - 2026-11-22

### 新增

- `oort-core` 轻量探针：`#lang oort-core` 搭配独立的静态检查器，支持 `Int`、`Bool`、
  `Unit`、带注解的函数、`val`/`var`、`if`/`return`、`print` 以及一小组运算符。
  同一份源码仍可在 `oort-object` 下动态运行，此时注解不做检查（OP 0017）。
- 通过静态检查的核心模块在现有解释器上执行；`-t astm` 显示推断出的静态类型，
  `Unit` 映射为运行时 `null`。
- 同一方言内的 `oort-core` 模块导入：`import "m"` / `from "m" import f`
  暴露带类型的模块导出，支持再导出，并在编译期检测缺失的导出与循环导入。
  跨方言导入和原生导入仍被拒绝。
- 单态 `oort-core` ADT：顶层 `enum` 声明、构造器值、带通配符/绑定/嵌套构造器
  模式的 `match` 表达式，以及顶层构造器的穷尽性检查。枚举值可以打印；枚举相等性、
  泛型 ADT 和完整的嵌套穷尽性检查暂缓。`oort-object` 显式拒绝 `enum`/`match`。
- `oort-core` 中的函数类型、lambda 与一等函数值：`(Int, Bool) -> Int`、
  `do(x: Int) -> Int { ... }`、高阶函数、函数值变量/ADT 载荷，以及从核心模块
  导出的函数值。函数类型箭头是右结合的（`Int -> Int -> Int` =
  `Int -> (Int -> Int)`），调用可以沿函数值链式进行（`add(1)(2)`）。多参数函数
  不会自动柯里化。匿名/泛型/默认参数 lambda 仍被拒绝。
- `oort-core` 中的双向期望类型传播：注解、赋值、返回、函数体和调用实参现在会把
  期望类型推入 `if` 分支、块尾和 `match` 分支，从而在确切的分支或参数处
  给出更好的诊断。
- VSCode 语法（0.1.3）高亮 `enum` 声明与名称、`match`、`=>` 和 `Unit`；
  0.1.2 添加了最初的 enum/match 作用域。
- 内部后端基础：一个共享的线性寄存器 HIR、一个 32 位字节码编译器/反汇编器，
  以及一个用于动态标量/集合/函数/循环子集的寄存器 VM，包括容器切片、属性读写、
  lambda 和被帧捕获的闭包。函数值可以存储、返回、索引和调用，并能传给 `map`
  等原生高阶辅助函数。顶层动态类和实例方法（包括继承、`__init__` 和
  `__iter__`）、模块导入（`import`/`from`、别名、相对路径和 `-I`）以及
  `oort-core` 子集（带类型的静态槽位、带 `match` 的单态 ADT，以及
  `break`/`continue`，含 `break value`）现在也能在 VM 上运行。导入的模块在
  同一 VM 上执行，全局环境相互隔离，并且每个 `examples/08_core` 程序都能在
  `-t vm` 下运行。完整的参数绑定（调用时默认值、关键字参数和仅位置/仅关键字
  参数、`*args`、`**kwargs`、`&block`）现在通过 `CALL_KW` 描述符在解释器和 VM
  之间共享同一个绑定器。嵌套的具名函数现在会降级为带自递归局部绑定的闭包；
  循环内创建的函数使用每轮独立 cell，因此每个迭代闭包捕获自己的绑定。
  `-t bc` 打印反汇编，`-t vm` 执行该子集；`-t eval` 仍是默认后端。
- HIR/VM 动态类补充类方法与运算符方法：`def class.f` 写入元类并在类/子类上绑定，
  `def operator "<sym>"` 注册到类型运算符表；下标读写改走共享的
  `get_item`/`set_item`，因此用户 `"[]"`/`"[]="` 与 `on_missing` 在 VM 下生效。
  增强赋值（名字、属性、下标目标）也降低为读-改-写；`examples/03_oop/03_03_protocols.ort`
  现可在 VM 下运行。VM 还支持元类、`super`、扩展方法与扩展运算符（含词法作用域、
  导入激活和扩展内 `super`）；`examples/` 现已全部可在 VM 下运行。
- `oort-object` 下标与缺失属性协议（OP 0018）：`def operator "[]"(index)` /
  `def operator "[]="(index, value)` 用于用户自定义索引（包括切片和元组索引），
  以及在字段、方法和扩展之后进行只读的 `on_missing(name)` 回退。内建容器保留
  原生索引；没有 `__setattr__` 风格的写钩子。
- `oort-core` 静态类与槽位：带固定类型 `val`/`var` 槽位的顶层类、在 `__init__`
  之前运行的每实例槽位初始化器、构造函数的确定性赋值检查、只读 `val` 槽位、
  带类型的方法/`this`，以及构造函数调用。继承、元类、类方法、运算符方法和
  动态字段仍被拒绝。
- `oort-core` 集合与循环：`List[T]`、`Set[T]`、`Dict[K, V]` 和 `Tuple[...]`
  注解，同构/空字面量检查，索引，特殊的 `len` 内建函数，同类型集合相等性，以及
  针对列表、集合、字典键、字符串和同构元组的 `while`/`for` 循环。集合是不可变的，
  切片、`in`、排序和异构元组迭代仍被拒绝。
- `oort-core` 标量表达式：`Float` 和 `String` 类型及字面量，混合 Int/Float
  算术，`/`（始终为 `Float`），数值和 String 的比较/相等性，以及二者的带注解
  参数/返回值。数值注解仍然严格（`val x: Float = 1` 会被拒绝）；`**` 仍不受
  支持，因为其结果类型取决于指数。

### 变更

- List/Tuple 排序现在使用递归的 Oort 比较（元素用 Oort 的 `==`/`<` 比较，包括
  用户运算符），而不是 Python 宿主比较；Dict 不再支持排序，Set 排序使用键协议。
  `Bool` 这类不可排序的元素现在会报错。
- List/Tuple 的 `+` 和 `*` 是值级运算符，会构建共享元素对象的新序列，而不是进行
  `HOST` 往返复制。
- 除 `__init__` 和 `__iter__` 之外的 dunder 方法在类体中被拒绝
  （`Special method '<name>' is not supported.`），而不是被存储却从不分派；
  未使用的 `__op_*__` 字段和被遮蔽的 `super` 内建函数已移除。
- `enum` 和 `match` 现在是硬关键字，`=>` 是保留的 `FATARROW` 记号（不是用户
  运算符），用于 `match` 分支；原先名为 `enum`/`match` 的标识符和拼写为 `=>`
  的用户运算符不再有效。
- 方言边界是显式的：`oort-core` 可以导入其他核心模块，而加载器在 FFI 跳板
  落地之前仍会拒绝 `oort-object` ↔ `oort-core` 导入。
- REPL 仍仅支持 `oort-object`，现在会以清晰的错误消息拒绝 `#lang` 指令，
  而不是静默地把提交内容当作动态代码处理。

### 修复

- 向 List 等内建对象赋值属性时，现在会报告
  `Cannot set attribute ... on 'List' object`，而不是内部断言。

- 在内建容器内部进行比较或成员测试时抛出的错误，现在会报告用户表达式的源码
  位置，而不是 `<builtin>`。
- 在没有显式参数列表的具名 `def` 中，`$0`/`$1` 不再被静默绑定到外层 lambda
  的匿名参数。
- 初始化导入模块时（REPL 中的 Ctrl-C）发生 `KeyboardInterrupt`，会丢弃失败的
  记录，以便可以重试导入。
- `zip` 的文档现在说明它会急切地耗尽所有输入，并在无限可迭代对象上挂起。
- `OortIterator.take_remaining` 始终返回其底层列表的副本。
- 已移除语法中 `.` 之前多余的 `NEWLINE*`；行首点号续行仍由词法记号后处理器
  处理。

## [0.3.1] - 2026-11-20

### 变更

- 相等性现在有一个递归的值协议和一个独立的键协议（OP 0016）：嵌套的
  `Bool`/`Int` 保持不同，Dict/Set 相等性和集合代数使用键相等性，Int/Float 仍
  值相等但键不同。相等性、成员测试或集合代数不再使用宿主投影。
- 带显式参数列表的 lambda 现在是 `$0`/`$1` 解析的屏障，因此它无法静默捕获
  外层的匿名参数。
- 行首 `.` 续行在解析前从解析器记号流中移除；REPL 仍要求 `\`，因为它看不到
  下一行。
- JSON 展示程序对无参数方法使用仅花括号的定义（`def parse { ... }`）。

### 修复

- 类对象写入（`C.f = ...`）不再能替换通过类/元类 MRO 继承的可调用成员。

## [0.3.0] - 2026-11-20

### 新增

- 模块系统（OP 0006）：`.ort` 模块，支持 `import "m" [as x]` 和
  `from "m" import a, b as c`，急切的顶层提升初始化，规范路径缓存，
  循环导入诊断，带自动再导出的模块命名空间，以及 `-I/--module-path`
  搜索目录。
- `examples/04_modules/` 下的多文件示例。
- 诊断信息现在让每个错误与其自身的源码输入配对，并跨文件排序，因此导入模块的
  错误会指向正确的文件和行。
- 最小标准库（OP 0012）：急切的 `map`、`filter`、`zip`、`enumerate` 和稳定的
  `sorted` 内建函数，以及可通过 `import "math"` / `from "string" import upper`
  导入的原生 `math` 和 `string` 模块。
- `examples/05_stdlib/` 下的标准库示例，以及 `benchmarks/test_stdlib.py` 中的
  宿主/标准库基准测试。
- 迭代器协议（OP 0013）：用户类实现 `__iter__`，返回一个产出 `(value, valid)`
  元组的可调用对象；`for` 是流式的，内建容器通过原生 `Iterator` 类型暴露
  同一协议。
- `examples/06_iterators/` 下的用户迭代器示例，以及
  `benchmarks/test_iterators.py` 中的内建/用户迭代器基准测试。
- 扩展方法（OP 0014）：`def C.f` 在类外部为现有类型定义方法。扩展具有词法
  作用域，由 `import`/`from` 激活，按运行时类型 MRO 分派，且从不覆盖成员、
  字段或内建运算符。扩展中的 `super` 只搜索类成员。
- 扩展运算符：`def C.operator "+"(x)` 填补目标类型未定义的运算符；类和原生
  运算符始终优先。
- `examples/03_oop/03_02_extensions.ort` 下的扩展示例和
  `benchmarks/test_extensions.py`。
- 最小 I/O 与进程支持（OP 0015）：用于 UTF-8 整文件访问的 `io.read_file` /
  `io.write_file`，`os.args` / `os.script` / `os.exit`，以及
  `string.ord` / `string.chr`。
- `examples/07_showcase/07_00_json.ort` 的 JSON 解析器/格式化器展示，包括
  `\uXXXX`/代理对处理和 CLI 文件参数。
- 使用 MkDocs Material 构建并部署到 GitHub Pages 的文档站点：
  <https://fyabc.github.io/oort-lang/>，新增了入门和示例页面。

### 变更

- 宿主边界重构：`OortObject.py_value` 变为 `host_value`，引入 `HostBridge`、
  HOST/VALUE/CONTEXT 原生调用模式和用于高阶原生函数的 `NativeContext`。
  `len` 不再投影整个容器。
- 导入只允许在模块顶层；嵌套导入会以显式诊断被拒绝。
- 每个模块拥有隔离的全局环境；全局查找针对定义该名字的模块解析，因此函数和
  方法在其他地方被调用时仍保有自己的模块全局。
- 语法不再内嵌宿主语言动作（OP 0008）：括号跟踪、换行过滤和行转义移至纯
  记号后处理器（`parser/token_processor.py`），词法分析器始终发出 `NEWLINE`。
- REPL 现在是 `ReplSession` + `ConsoleIO`：每次提交都重新解析其缓冲区，而不是
  修改 ANTLR 词法/语法分析器的内部状态。Ctrl-C 会取消当前输入或中断正在执行的
  语句而不退出；非 TTY 输入时隐藏提示符，EOF 干净退出。在 Windows 上，EOF 是
  Ctrl-Z 后跟 Enter；`exit` / `quit` 也会关闭 REPL。

### 修复

- VSCode 语法现在将 `import`、`from` 和 `as` 着色为导入关键字
  （`keyword.control.import.oort`）；此前 `as` 与运算符词共享作用域，某些主题
  下可能不着色。扩展版本 0.1.1。
- 不匹配的右括号（`)`、`]`、`}`）现在产生正常的语法诊断，而不是来自词法
  分析器栈动作的 `IndexError`。
- 管道/重定向的 REPL 输入在 EOF 时干净退出，而不会以 traceback 结束，语法
  错误也不再中止会话。

## [0.2.0] - 2026-11-19

### 新增

- `editors/vscode/` 中的 VSCode 扩展：TextMate 语法高亮、括号匹配、注释配置、
  轨道与彗星语言文件图标以及语法测试。
- 用于没有显式参数列表的 lambda 的匿名 lambda 参数 `$0` / `$1`
  （`do: $0 * 2`、`do: $0 + $1`；OP 0010）。
- 完整参数绑定：调用时默认值、关键字参数、仅位置（`/`）和仅关键字（`*`）
  参数、作为 Tuple 的 `*args`、作为 Dict 的 `**kwargs`，以及支持尾随块或
  关键字语法的 `&block`（OP 0011）。
- 方言契约：可选的首行 `#lang oort-object` 指令、`DialectConfig`（特性开关和
  每次编译的 Pratt 运算符表），以及针对未知、未实现（`oort-core`）或位置错误
  的方言声明的显式诊断。
- 运算符重载：用于一元和二元运算符（包括比较和成员测试）的
  `def operator "<sym>"` 方法。内建类型使用同一张分派表，`!=` / `!in` 由
  `==` / `in` 派生，`is` / `!is` 比较对象标识。
- 表达式与表层语法清理（OP 0009）：Python/Rust 优先级，严格的 `Bool`/`Int`
  分离，带括号的参数列表，禁用隐式中缀，`break value`，DOT 续行和 Oort
  容器显示。
- 语言规范（`docs/spec/`）和提案流程（`docs/proposals/`，OP 0001–0011）。
- Linux 和 Windows 上的 CI（Python 3.11–3.13）：lint、格式、类型检查和
  覆盖率门禁。
- 贡献、安全和 issue/PR 模板。

### 变更

- 质量基础设施现在包括 bandit、pip-audit、deptry、vulture、hypothesis 属性
  测试、markdown/actionlint 检查和 CI 中的 wheel/sdist 安装冒烟测试。
- 基准测试基础设施现在覆盖微操作、宏工作负载、启动、内存上限和历史
  Fibonacci，并带有 CI 历史工作流和性能分析说明。
- 包被重组为 `source/`、`diagnostics/`、`ast/`、`parser/`、`semantics/`、
  `runtime/` 和 `driver/` 层。`objects.py`、`ast_builder.py` 和 `pass1.py`
  按职责拆分，import-linter 契约保持层边界强制执行。
- 名称解析现在向 AST 名称节点附加带类型的 `Binding`（作用域深度加槽位索引），
  而不是写入无类型的 `metadata` 键；作用域布局与未来的槽位/上值后端共享。
- 每个解释器现在拥有独立的 `Runtime`，带有自己的内建类型表和
  `null`/`true`/`false` 单例，因此多个解释器可以在同一进程中共享而不会互相
  覆盖类型。
- mypy 现在是有效的门禁：排除生成的解析器/词法分析器代码，手写代码以
  `check_untyped_defs` 和严格 optional 检查，pre-commit 使用项目锁定的
  工具版本。
- 运算符优先级现在遵循 Python/Rust：按位 `& ^ |` 比较运算符绑得更紧，比较
  运算符不具结合性（`a < b < c` 会报错）。
- `Bool` 不再是 `Int` 的子类型：布尔运算和 `true == 1` 会被拒绝；容器成员
  测试保持布尔值与整数不同。
- 标识符不再接受尾随 `!`，因此 `a!=b`、`x!in xs` 和 `a!is b` 在无空格时也能
  正确分词。
- 所有参数列表现在都要求括号。`def f x: ...` 和 `do x: ...` 等裸形式是语法
  错误，消除了 `:` 类型与函数体的歧义。
- 隐式中缀调用（`a b c`）在显式 `infix` 设计落地之前被禁用；`def C.f`、
  `class A.B` 和显式 `super(...)` 调用会被拒绝。
- `break expr` 使 `while` / `for` 表达式返回值；以 `.` 开头的行继续方法链；
  支持 `//=`。
- Dict/set 显示使用 Oort 字面量分隔符（`{: ... :}` / `{. ... .}`）。
- `oort-object` 拒绝在类体中直接声明 `var` / `val`。实例是开放的字段包；
  字段必须在 `__init__` 中用 `this.name = ...` 创建（OP 0007）。
- 实例字段不再能遮蔽实例方法或类方法；缺失属性抛出 `OortAttributeError`。
  默认相等性和哈希使用对象标识。
- 源文件以 UTF-8 读取，可选 BOM（`utf-8-sig`）。
- 公开路线图现在是高层次的；详细规划位于私有账本和 GitHub 里程碑/issue 中。
  开发围绕共享主干上的方言垂直切片组织：先 `oort-object` v1，接着是轻量
  `oort-core` 探针，两个方言 v1 之后是共享字节码后端。类槽位限定在
  `oort-core`；`oort-object` 保持开放字段包（OP 0001 §5、OP 0007）。
- 最低 Python 版本现在是 3.11（3.10 已到生命周期终点）；CI 在 Linux 上测试
  3.11–3.13，在 Windows 上测试 3.13。
- 开发依赖已更新（ruff、mypy、pytest、pytest-benchmark、pre-commit、
  virtualenv、filelock），解决了未决的 Dependabot 警报。

### 修复

- 在循环内定义的函数中的 `break` / `continue` 不再逃逸到外层循环。
- 参数布局验证现在能处理索引 0 处的可变关键字参数和尾随块参数，并修正了
  标记顺序诊断。
- Pratt 绑定力是整数，而不是浮点 epsilon 值。

## [0.1.0] - 2026-11-18

### 新增

- 动态核心：函数、闭包、类、方法、类方法、多继承（C3 MRO）、元类、
  `this` / `super`。
- `for ... in` 循环（解构、逐次迭代绑定）、`if` / `elif` / `else`、带
  `break` / `continue` 的 `while`。
- List、tuple、dict 和 set 字面量；下标与切片；增强赋值；多声明目标和
  元组解包。
- 内建函数：`print`、`clock`、`type`、`super`、`len`、`range`、`str`、
  `repr`、`int`、`float`、`bool`。
- 带错误恢复的多行 REPL。
- 单元测试和集成测试、示例程序以及基准基线。
- 从 `grammars/Oort.g4` 生成的解析器，带有 Pratt 表达式解析器。

### 变更

- 默认执行目标是 `eval`（树遍历解释器）。
- 不支持的构造会以显式的 `UnsupportedSyntax` 诊断被拒绝，而不是静默地做出
  错误行为。
- `USER_OP` 排除 `.`、`:`、`@`；移除了死记号；支持 `elif` 和对称的 `else`
  形式。

### 移除

- 未完成的基于寄存器的字节码后端（会静默地错误编译不支持的构造）。设计与
  重新实现要求保留在 `docs/design/02-bytecode-vm-design.md` 和 OP 0004 中。
