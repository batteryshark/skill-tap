---
name: cron-job-manager
description: Inspect, render, install, or remove named user crontab jobs with explicit mutation confirmation and marker-bounded edits. Use on Unix-like systems when a user wants recurring local command scheduling through cron rather than a platform-specific automation service.
---

# Cron Job Manager

Use `bin/cron-job-manager`. Listing and rendering are read-only. Installation and removal require the user to approve the exact rendered entry and pass `--confirm`.

## Workflow

1. Run `list`.
2. Run `render --name ... --schedule ... --command ...` and show the exact entry.
3. Confirm command paths, quoting, environment, output handling, and schedule with the user.
4. Run `install ... --confirm`.
5. Run `list` again and report the installed marker.
6. Remove only by exact name with `remove --name ... --confirm`.

Read [references/cron-safety.md](references/cron-safety.md) before scheduling destructive, privileged, networked, or high-frequency commands.

