# Language guidance

Project conventions and configured tooling win over these defaults.

## Python

- Keep public contracts explicit with type hints where the project uses them.
- Prefer specific exceptions or typed results over broad catches and sentinel mixtures.
- Use Ruff, Black, mypy, pyright, pytest, or the project's configured equivalents rather than hand-enforcing layout.
- Avoid mutable default arguments and implicit module-level state.

## Rust

- Model closed variants with enums and invalid states with types when the added type clarifies real rules.
- Propagate or handle `Result` and `Option` deliberately; investigate routine `unwrap`, broad `allow`, and unexplained `unsafe`.
- Prefer borrowing to cloning when ownership remains clear, but do not contort APIs to avoid a justified clone.
- Use rustfmt, Clippy, compiler checks, and focused tests.

## JavaScript and TypeScript

- Keep boundary types explicit and narrow `unknown` before use; investigate `any` where it erases a real contract.
- Make asynchronous failure, cancellation, and cleanup visible.
- Prefer literal unions or enums when they represent a stable closed set; do not replace simple values with ceremony.
- Use the configured formatter, linter, type checker, and test runner.

## Go

- Keep error wrapping and ownership clear; do not discard returned errors without evidence.
- Make context cancellation and goroutine lifecycle explicit.
- Use gofmt, go vet, staticcheck when configured, and focused tests.

## Shell

- Treat quoting, word splitting, destructive operations, and partial failure as correctness concerns.
- Use shell for shell-native orchestration; move complex parsing and policy into a testable language.
