---
name: windows-elevation
description: "Choose and execute the narrowest Windows elevation method while preserving output, with a guarded SYSTEM fallback for exceptional protected operations."
---

# Elevate a Windows Operation

1. Run `bin/windows-elevation` to inspect the current identity and available mechanisms.
2. Read [references/elevation-model.md](references/elevation-model.md). First determine whether elevation is actually required and narrow the command, target, and duration.
3. Prefer the operating system's supported interactive administrator elevation. Preserve stdout/stderr when possible, but never trade away the visible UAC consent boundary.
4. Show the exact elevated command and expected effects, obtain approval, execute it once, and verify the intended state with an unprivileged read.
5. Use a scheduled task running as SYSTEM only when administrator access is demonstrably insufficient. SYSTEM is non-interactive, isolated from the desktop, and should write bounded output to a pre-created protected location; remove the temporary task and files afterward.

Use [agents/elevation-reviewer.md](agents/elevation-reviewer.md) before any SYSTEM-level plan.
