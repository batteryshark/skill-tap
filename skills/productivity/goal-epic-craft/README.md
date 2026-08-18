# goal-epic-craft

One package, three workflows over a shared written standard, for turning
rough intent into work an executor — human or autonomous agent — can run
without guessing.

- **Craft** — a short frontier-round interview: rough description in,
  bounded goal or epic out. Facts come from the environment; the interview
  only asks decisions, with a recommended answer on every question.
- **Grade** — score an existing goal or epic against the standard. Verdict
  first, then at most five ranked gaps, each with the question that cures it.
- **Split** — break a bounded epic into 3–7 vertical slices, walking
  skeleton first. Refuses input that fails the standard.

The rubric all three share is [references/STANDARD.md](references/STANDARD.md):
a goal is bounded when it carries **purpose, boundary, budget, proof** — an
outcome with a "so that", explicit out-of-scope lines, an appetite, and
acceptance criteria a machine can check.

`bin/goal-epic-craft FILE.md` scans a draft and prints mechanical evidence
(sections, checkbox grammar and caps, boundary and budget markers, open
questions). It renders no verdict; judgment stays with the grader.

Filing results into a tracker is optional. The only integration shipped is
for the Work system — [references/work-integration.md](references/work-integration.md);
everything else works on plain markdown.

Entry point: [SKILL.md](SKILL.md).
