# Python portability rules

- Put PEP 723 metadata within the first eight lines of every runnable Python file.
- Declare `dependencies = []` for standard-library-only scripts.
- Prefer minimum compatible constraints when a tested lower bound is known; do not invent one.
- Treat sibling modules as local, not PyPI dependencies.
- Use `uv run --script path/to/tool.py` so metadata travels with the script.
- Permit a `python3` fallback only for empty dependency lists.
- Resolve paths relative to the launcher or script, never the caller’s current directory.
- Test from a directory outside the skill and from a path containing spaces.
