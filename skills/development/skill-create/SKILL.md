---
name: skill-create
description: Scaffold a complete portable skill package that follows the Skills Tap contract. Use when creating a new reusable agent skill, turning a repeated workflow into a skill, or generating SKILL.md plus portable agents, a matching bin command, PEP 723 scripts, references, and validation-ready structure.
---

# Create a Portable Skill

1. Extract the reusable workflow, inputs, outputs, failure modes, verification, and scope boundaries from the request or recent work.
2. Read [references/contract-checklist.md](references/contract-checklist.md).
3. Choose a lowercase kebab-case name and a trigger description that states what the skill does and when to use it.
4. Run `bin/skill-create NAME --description "..." --target-dir PATH`.
5. Replace the generated evidence collector, role prompt, and reference content with workflow-specific material; the scaffold is a conforming starting point, not finished expertise.
6. Run the target tap’s validator and every generated `bin/` command against a representative fixture.

For an independent design pass, give the workflow evidence and proposed scope to [agents/skill-designer.md](agents/skill-designer.md).
