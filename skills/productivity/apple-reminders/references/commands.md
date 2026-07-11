# Command reference

`lists` and `reminders` are read-only. Mutating subcommands must use the opaque IDs returned by a fresh read whenever possible. Dates must be ISO 8601 with an explicit offset when time-of-day matters. A list deletion can remove all reminders in it and always requires confirmation.

The command is a portable interface around a macOS-specific implementation. It must fail clearly on other operating systems and must never attempt to change privacy permissions.
