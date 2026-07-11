---
name: apple-reminders
description: "Manage Apple Reminders on macOS through a native EventKit command with explicit confirmation for mutations and machine-readable results."
---

# Manage Apple Reminders

1. Confirm the host is macOS and explain that the first command may trigger Reminders automation permission.
2. Run `bin/apple-reminders list-lists` or `bin/apple-reminders list-reminders` to resolve list names and current reminder IDs before mutation.
3. Present the exact title, list, due date, notes, and URL before creating or changing a reminder. Confirm deletion of a reminder or list immediately before execution.
4. Run the narrow command described in [references/commands.md](references/commands.md), request JSON when subsequent automation needs stable fields, then re-read the affected item.
5. If permission is denied, stop and direct the user to System Settings > Privacy & Security > Automation/Reminders; never weaken system privacy controls.

Use [agents/reminder-reviewer.md](agents/reminder-reviewer.md) when dates, recurrence, or destructive list operations are ambiguous.
