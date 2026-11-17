# 测试

```
tests/
├── conftest.py          # 共享 fixture：run_source、compiler_factory
├── helpers.py           # get_compiler、示例/资产路径
├── assets/              # 固定的 .ort 源文件与期望 AST
├── unit/
│   ├── frontend/        # 词法、解析、AST、语义分析、拒绝清单
│   └── runtime/         # 解释器：基础语句、控制流、函数、类、容器、内建
└── integration/         # CLI 端到端、全部示例程序
```

## 运行

```bash
uv run pytest tests/                  # 全部测试
uv run pytest tests/unit              # 单元测试
uv run pytest tests/integration       # 集成测试
uv run pytest tests/ -k "collections" # 按名字筛选
```

## 编写约定

- 需要执行一段 Oort 源码时，使用 `run_source` fixture：

  ```python
  def test_something(run_source):
      result = run_source("print(1 + 2)\n")
      assert result.stdout == "3\n"
      assert result.value == 3
  ```

- 需要构造编译器（例如测试错误路径）时，使用 `get_compiler("NOT_EXIST -t eval")`。
  语法/语义错误通过 `SystemExit` 结束；运行期错误通过 `CompilerError` 结束。
- 未实现特性的诊断放在 `unit/frontend/test_unsupported.py`，用参数化列表维护。
- 新增示例时，在 `integration/test_examples.py` 的 `EXPECTED_OUTPUTS` 中登记输出；
  非确定性输出（如计时）单独处理。
- 测试文件按**被测子系统**命名，而不是按实现文件命名。

## 覆盖范围

| 领域 | 测试文件 |
|------|----------|
| 词法 | `unit/frontend/test_lexer.py` |
| 解析与优先级 | `unit/frontend/test_parser.py` |
| AST 打印 | `unit/frontend/test_ast.py` |
| 名称解析/作用域 | `unit/frontend/test_semantic.py` |
| 未实现特性诊断 | `unit/frontend/test_unsupported.py` |
| 基础语句/增强赋值 | `unit/runtime/test_basic.py` |
| 控制流 | `unit/runtime/test_control_flow.py` |
| 声明与解包 | `unit/runtime/test_declarations.py` |
| 函数与闭包 | `unit/runtime/test_functions.py` |
| 类与继承 | `unit/runtime/test_classes.py` |
| 容器与切片 | `unit/runtime/test_collections.py` |
| 内建函数 | `unit/runtime/test_builtins.py` |
| CLI | `integration/test_cli.py` |
| REPL | `integration/test_repl.py` |
| 示例程序 | `integration/test_examples.py` |
