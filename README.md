# Skills Tap

![Skills Tap — a retro comic-book mascot](assets/skills-tap.png)

Skills Tap is a public collection of portable, reusable skills for agents. It is a general-purpose catalog of repeatable workflows, organized by category as it grows. Each skill is self-contained, readable without a specific agent platform, and backed by small command-line tools where deterministic checks help.

## Skills

### Development

| Skill | Use it to |
|---|---|
| [`architecture-for-comprehension`](skills/development/architecture-for-comprehension/) | Review whether a system is coherent, navigable, and explainable as a whole. |
| [`code-quality-review`](skills/development/code-quality-review/) | Audit or improve local code quality with evidence and behavior-preserving refactoring. |
| [`codebase-archeology`](skills/development/codebase-archeology/) | Map inherited or archived projects and decide what to preserve, merge, or retire. |
| [`codebase-writeup`](skills/development/codebase-writeup/) | Produce an evidence-backed technical explanation of how a codebase works. |
| [`deliverable-hygiene`](skills/development/deliverable-hygiene/) | Keep a repository shaped like finished work and recover one that has accumulated process residue. |
| [`github-publish`](skills/development/github-publish/) | Preflight and publish a local project to GitHub without leaking or staging unrelated state. |
| [`publish-ready`](skills/development/publish-ready/) | Run a final, evidence-backed cleanup before sharing or releasing a repository. |
| [`work-product-audit`](skills/development/work-product-audit/) | Find public prose that leaks internal reasoning, defensive framing, or generated-sounding filler. |

### Productivity

| Skill | Use it to |
|---|---|
| [`project-retrospective`](skills/productivity/project-retrospective/) | Extract concrete lessons and improvements from completed or paused work. |
| [`project-tracker`](skills/productivity/project-tracker/) | Maintain compact durable project memory across sessions and handoffs. |

### Utilities

| Skill | Use it to |
|---|---|
| [`intellidiff`](skills/utilities/intellidiff/) | Compare files or folders, calculate SHA-256 hashes, and find exact duplicates. |

## Use a skill

Copy a complete skill directory into your agent's skill path, or point the agent directly at its `SKILL.md`. Keep the directory intact: scripts, references, and role prompts are part of the skill.

```sh
git clone https://github.com/batteryshark/skills-tap.git
cp -R skills-tap/skills/development/publish-ready /path/to/your/agent/skills/
```

Every Python tool can run with `uv` or the system Python. The executable in each skill's `bin/` directory prefers `uv` and falls back to `python3` when the tool has no third-party dependencies.

```sh
skills/development/publish-ready/bin/publish-ready .
```

## Add a skill

Put new skills under a broad category in `skills/`, follow the [skill contract](SKILL-CONTRACT.md), and run:

```sh
python3 scripts/validate_skills.py
python3 -m unittest discover -s tests
```

## License

MIT. See [LICENSE](LICENSE).
