---
name: google-calendar-cli
description: Authenticate a desktop Google Calendar client, inspect calendars and events, query free/busy data, and create or delete events through a reviewable plan with hash-bound explicit confirmation. Use when a user wants direct Google Calendar CLI automation without an MCP server.
---

# Google Calendar CLI

Use `bin/google-calendar-cli`. Read operations execute directly. Calendar mutations require a plan file and the exact confirmation hash printed during planning.

## Workflow

1. Read [references/setup-and-confirmation.md](references/setup-and-confirmation.md).
2. Authenticate once with the required account.
3. Use read commands to resolve calendar IDs, event IDs, dates, and time zones.
4. Generate a create or delete plan.
5. Show the complete plan to the user, including attendees and notification behavior.
6. Only after explicit approval, run `apply-plan <file> --confirm <hash>`.
7. Relay the returned event ID and link or deletion result.

Never infer approval from the original scheduling request. A calendar mutation needs confirmation after the concrete plan exists.

