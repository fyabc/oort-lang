# Changelog

All notable changes to this project are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- VSCode extension in `editors/vscode/`: TextMate syntax highlighting,
  bracket matching, comment configuration, an orbit-and-comet language file
  icon and grammar tests.
- Dialect contract: an optional first-line `#lang oort-object` directive,
  `DialectConfig` (feature gates and a per-compilation Pratt operator table),
  and explicit diagnostics for unknown, unimplemented (`oort-core`) or
  misplaced dialect declarations.
- Operator overloading: `def operator "<sym>"` methods for unary and binary
  operators, including comparisons and membership. Built-in types use the same
  dispatch table, `!=` / `!in` derive from `==` / `in`, and `is` / `!is`
  compare object identity.
- Language specification (`docs/spec/`) and a proposal process
  (`docs/proposals/`, OP 0001–0006).
- CI on Linux and Windows (Python 3.10/3.12): lint, format, type check and
  coverage gate.
- Contribution, security and issue/PR templates.

### Changed

- `oort-object` rejects `var` / `val` declarations directly in a class body.
  Instances are open field bags; fields must be created with
  `this.name = ...` in `__init__` (OP 0007).
- Source files are read as UTF-8 with optional BOM (`utf-8-sig`).
- Development roadmap is organized around dialect vertical slices on a shared
  spine: `oort-object` v1 first, a thin `oort-core` probe next, and a shared
  bytecode backend after both dialect v1s. Class slots are scoped to
  `oort-core`; `oort-object` keeps an open field bag (OP 0001 §5, OP 0007).
- Minimum Python is now 3.11 (3.10 reached end of life); CI tests 3.11 and
  3.13 on Linux, and 3.13 on Windows.
- Development dependencies updated (ruff, mypy, pytest, pytest-benchmark,
  pre-commit, virtualenv, filelock), resolving the open Dependabot alerts.

## [0.1.0] - 2026-11-18

### Added

- Dynamic core: functions, closures, classes, methods, class methods,
  multiple inheritance (C3 MRO), metaclasses, `this` / `super`.
- `for ... in` loops (destructuring, per-iteration binding), `if` / `elif` /
  `else`, `while` with `break` / `continue`.
- List, tuple, dict and set literals; subscripting and slicing; augmented
  assignment; multiple declaration targets and tuple unpacking.
- Builtins: `print`, `clock`, `type`, `super`, `len`, `range`, `str`, `repr`,
  `int`, `float`, `bool`.
- Multi-line REPL with error recovery.
- Unit and integration tests, example programs and a benchmark baseline.
- Parser generated from `grammars/Oort.g4` with a Pratt expression parser.

### Changed

- Default execution target is `eval` (tree-walking interpreter).
- Unsupported constructs are rejected with explicit `UnsupportedSyntax`
  diagnostics instead of silently doing the wrong thing.
- `USER_OP` excludes `.`, `:`, `@`; dead tokens were removed; `elif` and
  symmetric `else` forms are supported.

### Removed

- The unfinished register-based bytecode backend (silently miscompiled
  unsupported constructs). Design and reimplementation requirements are kept in
  `docs/design/02-bytecode-vm-design.md` and OP 0004.
