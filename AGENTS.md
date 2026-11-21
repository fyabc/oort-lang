# AGENTS.md

面向 AI 代理的仓库约定。人类贡献者请看 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 验证命令

```bash
uv run --frozen python -m pytest tests/ -q
uv run --frozen ruff check src tests benchmarks scripts
uv run --frozen ruff format --check src tests benchmarks scripts
uv run --frozen mypy src/
uv run --frozen --with "import-linter>=2" lint-imports
uv run --frozen pre-commit run --all-files
uv run --frozen --with "mkdocs-material>=9.6" mkdocs build --strict
```

性能分析用 `scripts/profile_run.py`（cProfile + 计时）；采样 profile 与统计
规则见 `benchmarks/README.md`。

## 不变量

- 新增 `src/oort_lang/` 顶层包或测试子目录时，执行 CONTRIBUTING.md 的
  「结构同步清单」（README 目录结构、位置表、import-linter layers、
  tests/README 覆盖表）。
- 未实现的构造必须以 `UnsupportedSyntax` 显式拒绝，不得静默错误执行；
  拒绝项记录在 `docs/spec/06-conformance.md`。
- `src/oort_lang/parser/grammar/` 是生成代码，勿手改。
- `uv.lock` 可能被本机镜像改写；统一用 `uv run --frozen`，lock 变脏先还原。
- `private/` 不入库。
