---
name: skill-python-portability
description: Audit and modernize Python scripts inside portable skills with PEP 723 dependency metadata, stable uv launchers, standard-library fallbacks, and no hidden virtualenv or global-package assumptions. Use when a skill invokes Python directly, has undeclared imports, fails outside its author’s machine, or needs contract-compliant bin and scripts structure.
---

# Improve Python Skill Portability

1. Run `bin/skill-python-portability SKILL_PATH` to inventory Python files, imports, PEP 723 blocks, and launcher coverage.
2. Read [references/python-portability.md](references/python-portability.md).
3. Present the audit before editing when dependency mapping or runtime support is ambiguous.
4. Add PEP 723 metadata to every runnable Python script, including an empty dependency list for standard-library-only tools.
5. Route the matching `bin/<skill-name>` launcher through `uv run --script`; fall back to `python3` only when dependencies are empty.
6. Run every changed command with realistic and failure fixtures, then run the tap validator.

Use [agents/python-portability-reviewer.md](agents/python-portability-reviewer.md) for an independent dependency and launcher review.
