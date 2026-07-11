# Cron safety

- Cron runs with a minimal environment. Prefer absolute executable and file paths.
- Redirect output deliberately or expect local cron mail.
- Prevent overlap for long-running jobs with a lock appropriate to the platform.
- Do not place secrets directly in the crontab.
- Avoid broad shell deletion, unbounded network retries, or sub-minute emulation.
- Use the narrowest user account; this tool manages only the current user's crontab.
- Preserve unrelated lines. This tool changes only blocks bounded by its exact name markers.

Five-field format: minute, hour, day of month, month, day of week.

