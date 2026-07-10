# Onboarding probe

Use a bounded newcomer task to test whether the repository's intended mental model is discoverable. This is an evidence exercise, not role-playing incompetence.

## Choose tasks

Select two to four tasks that fit the project and review boundary:

- Explain the project's purpose, primary users, and runtime in a short paragraph.
- Find authoritative setup, build, test, lint, or run commands.
- Locate the main entry point and trace one representative behavior.
- Identify which module owns a named concept or external boundary.
- Find where a small hypothetical change and its tests would belong.
- Locate operational, migration, or troubleshooting guidance when applicable.

Do not install dependencies, execute untrusted programs, mutate data, or contact external systems merely to complete a probe. Use already-authorized checks only.

## Record friction

For each task, capture:

- **Outcome:** completed, partial, blocked, or contradicted.
- **Signposts:** files, names, commands, tests, or diagrams that helped.
- **Friction:** missing link, stale instruction, competing entry point, ambiguous ownership, hidden prerequisite, or unexplained convention.
- **Impact:** extra concepts or guesses a contributor must carry.
- **Smallest improvement:** the narrowest durable fix.
- **Confidence:** direct observation or inference.

Do not penalize a specialized repository for requiring domain knowledge. Penalize knowledge that is project-specific, necessary, and needlessly undiscoverable.
