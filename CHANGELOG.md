# Changelog

All notable changes to this project are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- Language specification (`docs/spec/`) and a proposal process
  (`docs/proposals/`, OP 0001–0006).
- CI on Linux and Windows (Python 3.10/3.12): lint, format, type check and
  coverage gate.
- Contribution, security and issue/PR templates.

## [0.0.1] - 2026-11-18

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
