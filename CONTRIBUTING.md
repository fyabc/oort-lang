# Contributing to Oort

Thanks for helping! Oort is a learning-oriented language project, so clarity and
explicit design decisions matter more than feature count.

## Development setup

```bash
uv sync --extra dev
pre-commit install

uv run --frozen pytest tests/
uv run --frozen ruff check src tests benchmarks scripts
uv run --frozen ruff format --check src tests benchmarks scripts
uv run --frozen mypy src/
```

Java 17+ is only needed to regenerate the parser from `grammars/Oort.g4`:

```bash
uv sync --extra build-grammar
python scripts/build_grammar.py   # or: make build-grammar
```

Do not hand-edit files in `src/oort_lang/parser/grammar/`; they are generated.

The documentation site is built with MkDocs Material:

```bash
make docs-serve   # preview at http://127.0.0.1:8000/
make docs         # strict build, same as CI
```

## Where things live

| Path | What |
|------|------|
| `docs/spec/` | Normative language reference (must match the implementation) |
| `docs/proposals/` | PEP/RFC-style design proposals |
| `docs/implementation/` | Compiler implementation notes |
| `mkdocs.yml` | Documentation site navigation and theme configuration |
| `src/oort_lang/source/` | Source text, positions and input abstractions |
| `src/oort_lang/diagnostics/` | Exceptions, error handler and ANTLR error listener |
| `src/oort_lang/ast/` | AST nodes, visitor, typed bindings and printer |
| `src/oort_lang/parser/` | Grammar, Pratt parser and AST builder |
| `src/oort_lang/semantics/` | Name resolution and semantic checks |
| `src/oort_lang/runtime/` | Tree-walking runtime and object model |
| `src/oort_lang/driver/` | Compiler, REPL and CLI entry point |
| `tests/unit/`, `tests/integration/` | Unit tests, CLI/REPL/example tests |

## Rules for language changes

1. **Open a proposal first** for anything non-trivial (new syntax, semantics,
   type-system changes). Copy `docs/proposals/0000-template.md`.
2. **No half-features.** If a construct is parsed but not implemented, it must be
   rejected with `UnsupportedSyntax` in `src/oort_lang/semantics/pass1.py`, and
   listed in `docs/spec/06-conformance.md`.
3. **Update the spec and tests together.** A feature is not done until
   `docs/spec/` and `tests/` reflect it.
4. **Keep features orthogonal.** Avoid special cases for particular types or
   syntax; prefer explicit, composable mechanisms.
5. **Do not add metaprogramming shortcuts** (macros, `comptime`, hidden code
   generation) before the runtime semantics are stable.

## Tests

- Add or extend tests under `tests/unit/` for the subsystem you touch.
- CLI/REPL/example behavior belongs in `tests/integration/`.
- New examples must be registered in `tests/integration/test_examples.py`.
- Core code is expected to stay above the CI coverage threshold (87%).

## Quality gates

`make check` runs lint, formatting, mypy, import boundaries and tests. The
following optional gates run in the `quality` CI job or via `make quality`:

| Gate | Tool | Command |
|------|------|---------|
| Security | bandit | `make security` |
| Dependency CVEs | pip-audit | `make audit` |
| Dependency hygiene | deptry | `make deps` |
| Dead code | vulture | `make dead-code` |
| Property tests | hypothesis | `make property` |
| Markdown | markdownlint-cli2 | `make markdown` |

Mutmut/`cosmic-ray` mutation testing is an occasional local check rather than
a per-push gate; run it against `src/oort_lang/runtime` when changing the
interpreter core.

## Commits and pull requests

- Use conventional commit subjects (`feat:`, `fix:`, `docs:`, `test:`, ...).
- Keep each commit focused; avoid mixing refactors with behavior changes.
- In the PR description, state what changed, why, which proposal/spec section
  applies, and how it was tested.
- CI must pass on Linux and Windows.

## Reporting bugs

Please include a minimal `.ort` reproducer, the command you ran, and the full
diagnostic output. For security issues, see [SECURITY.md](SECURITY.md).
