---
name: windows-ai-controls
description: "Audit, disable, and restore selected Windows AI features through reviewable registry and policy changes with explicit elevation and verification."
---

# Control Windows AI Features

1. Identify the Windows build, edition, managed-device status, and exact feature: Recall/snapshots, Copilot, Edge assistance, typing personalization, or an app-specific capability.
2. Run `bin/windows-ai-controls audit` without elevation and read [references/policy-safety.md](references/policy-safety.md).
3. Prefer documented policy controls for that build. Generate a plan showing every registry/policy value, previous value, scope, restart requirement, and restore action.
4. Obtain explicit approval before applying machine policy or removing a package. Use the narrowest elevation method and preserve a rollback record.
5. Re-run the audit after policy refresh/restart. Report unsupported or superseded settings instead of claiming success from a registry write alone.

This skill does not copy opaque third-party "debloat" scripts or bypass organization policy. Use [agents/policy-reviewer.md](agents/policy-reviewer.md) for a second review of a proposed change set.
