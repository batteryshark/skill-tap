---
name: reverse-brief
description: "Reconstruct a concise implementation brief from an existing codebase or artifact when original requirements are missing, stale, or incomplete."
---

# Reconstruct an Implementation Brief

1. Run `bin/reverse-brief PATH` to collect a bounded repository inventory.
2. Inspect entry points, tests, public interfaces, configuration, examples, history, and user-visible text. Treat code as evidence of implementation, not proof of original intent.
3. Write the brief using [references/brief-template.md](references/brief-template.md): problem, users, observed behavior, constraints, acceptance criteria, inferred decisions, contradictions, and open questions.
4. Label every non-obvious statement as observed, inferred, or unknown. Cite concrete files and commands.
5. Reconcile documentation against behavior and tests; surface contradictions instead of silently choosing a story.

Use [agents/brief-reviewer.md](agents/brief-reviewer.md) for an independent intent-versus-evidence pass.
