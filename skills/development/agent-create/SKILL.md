---
name: agent-create
description: Scaffold a portable Markdown role prompt for a focused subagent or independent review role. Use when creating an agent definition, extracting a specialist role from a workflow, or defining explicit inputs, evidence standards, constraints, and output without depending on one orchestration vendor.
---

# Create a Portable Agent Prompt

1. Define the single responsibility, inputs, evidence boundary, prohibited assumptions, and expected output.
2. Read [references/agent-design.md](references/agent-design.md).
3. Run `bin/agent-create NAME --purpose "..." --target-dir PATH`.
4. Replace placeholders with domain-specific constraints and realistic acceptance criteria.
5. Test the prompt in a fresh context using raw artifacts rather than leaking the intended answer.

Use [agents/agent-prompt-reviewer.md](agents/agent-prompt-reviewer.md) for an independent scope review.
