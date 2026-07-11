---
name: skill-node-portability
description: Audit and modernize Node.js scripts inside portable skills with explicit dependencies, committed lockfiles, local npm commands, compiled runnable JavaScript, and no global-tool assumptions. Use when a skill contains JavaScript or TypeScript, relies on global npm installs, lacks deterministic setup, or fails when copied to another machine.
---

# Improve Node Skill Portability

1. Run `bin/skill-node-portability SKILL_PATH` to inventory runnable files, import specifiers, package metadata, lockfiles, and TypeScript siblings.
2. Read [references/node-portability.md](references/node-portability.md).
3. Present ambiguous imports and runtime choices before editing.
4. Prefer Node built-ins; declare unavoidable third-party packages and commit `package-lock.json`.
5. Keep runnable JavaScript as `.mjs`; if TypeScript remains, commit the corresponding `.mjs` output.
6. Use local `npm --prefix ... ci` and `npm --prefix ... run ...` commands—never global installs.
7. Test from outside the skill directory and run the tap validator.

Use [agents/node-portability-reviewer.md](agents/node-portability-reviewer.md) for an independent supply-chain and invocation review.
