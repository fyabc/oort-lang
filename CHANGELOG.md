# Changelog

All notable changes to this project are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- VSCode extension in `editors/vscode/`: TextMate syntax highlighting,
  bracket matching, comment configuration, an orbit-and-comet language file
  icon and grammar tests.
- Anonymous lambda parameters `$0` / `$1` for lambdas without an explicit
  parameter list (`do: $0 * 2`, `do: $0 + $1`).
- Full parameter binding: call-time default values, keyword arguments,
  positional-only (`/`) and keyword-only (`*`) parameters, `*args` as a Tuple,
  `**kwargs` as a Dict, and `&block` with trailing-block or keyword syntax.
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
- CI on Linux and Windows (Python 3.11–3.13): lint, format, type check and a
  coverage gate.
- Contribution, security and issue/PR templates.

### Changed

- Name resolution now attaches a typed `Binding` (scope depth plus slot
  index) to AST name nodes instead of writing untyped `metadata` keys; scope
  layouts are shared with the future slot/upvalue backend.
- Each interpreter now owns an isolated `Runtime` with its own built-in type
  table and `null`/`true`/`false` singletons, so multiple interpreters can
  share a process without overwriting each other's types.
- mypy is now an effective gate: generated parser/lexer code is excluded,
  hand-written code is checked with `check_untyped_defs` and strict optionals,
  and pre-commit uses the project's locked tool versions.
- Operator precedence now follows Python/Rust: bitwise `& ^ |` bind tighter than
  comparisons, and comparisons are non-associative (`a < b < c` is an error).
- `Bool` is no longer a subtype of `Int`: boolean arithmetic and `true == 1` are
  rejected; container membership keeps booleans and integers distinct.
- Identifiers no longer accept a trailing `!`, so `a!=b`, `x!in xs` and `a!is b`
  lex correctly without spaces.
- All parameter lists now require parentheses. Bare forms such as `def f x: ...`
  and `do x: ...` are syntax errors, removing the `:` type-vs-body ambiguity.
- Implicit infix calls (`a b c`) are disabled until the explicit `infix` design
  lands; `def C.f`, `class A.B` and explicit `super(...)` calls are rejected.
- `break expr` makes `while` / `for` expressions return a value; a line starting
  with `.` continues a method chain; `//=` is supported.
- Dict/set display uses Oort literal delimiters (`{: ... :}` / `{. ... .}`).
- `oort-object` rejects `var` / `val` declarations directly in a class body.
  Instances are open field bags; fields must be created with
  `this.name = ...` in `__init__` (OP 0007).
- Instance fields can no longer shadow instance or class methods; missing
  attributes raise `OortAttributeError`. Default equality and hashing use
  object identity.
- Source files are read as UTF-8 with optional BOM (`utf-8-sig`).
- Development roadmap is organized around dialect vertical slices on a shared
  spine: `oort-object` v1 first, a thin `oort-core` probe next, and a shared
  bytecode backend after both dialect v1s. Class slots are scoped to
  `oort-core`; `oort-object` keeps an open field bag (OP 0001 §5, OP 0007).
- Minimum Python is now 3.11 (3.10 reached end of life); CI tests 3.11 and
  3.13 on Linux, and 3.13 on Windows.
- Development dependencies updated (ruff, mypy, pytest, pytest-benchmark,
  pre-commit, virtualenv, filelock), resolving the open Dependabot alerts.

### Fixed

- `break` / `continue` inside a function defined in a loop no longer escape to
  the outer loop.
- Parameter-layout validation now handles variadic keyword and trailing block
  parameters at index 0, and the marker-order diagnostic is corrected.
- Pratt binding powers are integers instead of floating-point epsilon values.

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
