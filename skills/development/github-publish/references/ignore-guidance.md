# Ignore guidance

Start from files the project actually creates. Prefer a short accurate `.gitignore` over a pasted universal template.

## Usually ignore

- OS metadata such as `.DS_Store` and `Thumbs.db`.
- Language caches such as `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`, and `.gradle/`.
- Dependency trees such as `node_modules/` and local virtual environments.
- Reproducible build and coverage output such as `dist/`, `build/`, `target/`, and `coverage/` when not shipped.
- Local secrets and environment overrides such as `.env`, credentials, tokens, and tool-specific local state.
- Editor swap, backup, and crash files.

## Review before ignoring

- Dependency lockfiles: applications and tools normally commit them for reproducibility; library conventions vary.
- Editor configuration: shared format, task, and extension settings may belong in the project.
- Generated code: commit it when consumers build without the generator or when project policy treats it as source.
- Test fixtures, snapshots, corpora, and golden files: these may be load-bearing behavior evidence.
- Workspace files and local databases: some are durable project inputs, others are machine state.

## Secret rule

Ignoring a secret does not remove it from history. If a credential was committed or pushed, stop publication, rotate or revoke it, then use the repository's approved history-remediation process.
