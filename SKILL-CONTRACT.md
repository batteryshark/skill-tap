# Skill contract

Skills in this repository are portable packages. They must not depend on one agent vendor's metadata, directory conventions, or orchestration API.

## Package layout

Place each skill at `skills/<category>[/<group>...]/<skill-name>/` with this shape:

```text
skills/
└── development/
    └── related-workflows/    # optional organizational group
        ├── first-skill/
        └── second-skill/
```

Categories and optional groups may be nested to any depth. Skill discovery is
recursive: every `SKILL.md` below `skills/` identifies a skill package rooted
at its parent directory. Category and group names use lowercase letters,
digits, and hyphens.

Groups are organizational only. A skill must not depend on a parent group or a
sibling skill; copying its own directory must preserve all of its behavior.

Each skill package has this shape:

```text
skill-name/
├── SKILL.md
├── agents/
├── bin/
├── references/
└── scripts/
```

All five entries are required and must contain useful material:

- `SKILL.md` defines the trigger and core workflow. Its YAML frontmatter contains only `name` and `description`.
- `agents/` contains portable Markdown role prompts for optional subagents. Product-specific YAML or UI metadata does not belong here.
- `bin/` contains executable entry points intended for humans and agents.
- `scripts/` contains implementation code used by the skill or its entry points.
- `references/` contains details loaded only when the task needs them.

The skill directory name, frontmatter `name`, and primary `bin/` command must match. Use lowercase letters, digits, and hyphens.

## Portability

Write instructions in platform-neutral language. Say `agent`, `subagent`, `workspace`, and `skill path` unless a specific integration is the subject of the skill. Keep tool-specific configuration outside skill packages.

Role prompts in `agents/` describe the role, inputs, evidence standard, constraints, and expected output. They must work as plain Markdown prompts and must not assume a named orchestration system.

Use relative paths inside a skill. A copied skill must keep working without the rest of this repository.

## Executable code

Prefer the language standard library. Add a dependency only when it materially improves correctness or removes fragile custom code.

Python scripts must include [PEP 723](https://peps.python.org/pep-0723/) inline metadata. Declare an empty dependency list for standard-library-only scripts:

```python
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
```

Favor `uv run --script` in launchers and examples. A standard-library-only tool may fall back to `python3` when `uv` is unavailable.

Commit runnable JavaScript as `.mjs`. If TypeScript source is included, commit its compiled `.mjs` sibling so users do not need a TypeScript toolchain to run the skill. Do not put generated dependency trees or build caches in a skill.

Shell code is appropriate for thin launchers and genuinely shell-native tasks. Put reusable parsing, traversal, and policy logic in a testable script.

## Writing and scope

Keep `SKILL.md` concise. Put extended rubrics, examples, and variant-specific guidance in `references/`, linked directly from `SKILL.md`. Do not duplicate the same rules across both places.

Scripts report evidence, not conclusions that require judgment. Destructive actions require an explicit workflow step, a reviewable scope, and a recovery path.

Do not add a README inside an individual skill. The root README is the catalog; `SKILL.md` is the package entry point.

## Validation

Run the repository checks before publishing:

```sh
python3 scripts/validate_skills.py
python3 -m unittest discover -s tests
```

Also run every changed `bin/` command against a representative fixture or repository. Treat scanner output as review candidates unless the skill explicitly defines a hard failure.
