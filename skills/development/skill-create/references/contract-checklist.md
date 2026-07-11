# Portable skill contract checklist

- Directory name, frontmatter `name`, and `bin/<name>` match.
- Frontmatter contains only `name` and `description`.
- `SKILL.md` is concise, imperative, and links directly to optional detail.
- `agents/` contains a useful portable Markdown role prompt.
- `bin/` contains an executable entry point.
- `scripts/` contains useful implementation with PEP 723 metadata for Python.
- `references/` contains task-relevant guidance loaded only when needed.
- Every internal path is relative to the skill directory.
- Copying the skill directory preserves all behavior.
- Destructive workflows include preview, explicit approval, verification, and recovery.
- The package contains no README, product-specific UI metadata, caches, or generated dependency trees.
- The skill validator and representative command tests pass.
