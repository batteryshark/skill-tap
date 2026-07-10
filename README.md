# Skills Tap

![Skills Tap — a retro comic-book developer mascot](assets/skills-tap.png)

Skills Tap is a public collection of portable skills for software-development agents. Each skill is self-contained, readable without a specific agent platform, and backed by small command-line tools where deterministic checks help.

## Skills

| Skill | Use it to |
|---|---|
| [`architecture-for-comprehension`](skills/development/architecture-for-comprehension/) | Review whether a system is coherent, navigable, and explainable as a whole. |
| [`deliverable-hygiene`](skills/development/deliverable-hygiene/) | Keep a repository shaped like finished work and recover one that has accumulated process residue. |
| [`publish-ready`](skills/development/publish-ready/) | Run a final, evidence-backed cleanup before sharing or releasing a repository. |
| [`work-product-audit`](skills/development/work-product-audit/) | Find public prose that leaks internal reasoning, defensive framing, or generated-sounding filler. |

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
