# Setup and confirmation

Create a Google Cloud project, enable Google Calendar API, configure the OAuth consent screen, and create a Desktop app OAuth client. Store the downloaded file at:

```text
~/.config/google-calendar-cli/credentials.json
```

Override paths with `GCAL_CREDENTIALS` and `GCAL_TOKEN_FILE`.

```sh
bin/google-calendar-cli auth
bin/google-calendar-cli calendars
bin/google-calendar-cli events --calendar primary --start 2026-07-11T00:00:00-04:00 --end 2026-07-12T00:00:00-04:00
bin/google-calendar-cli plan-create --plan /tmp/event.json --summary 'Review' --start 2026-07-12T14:00:00-04:00 --end 2026-07-12T14:30:00-04:00
bin/google-calendar-cli apply-plan /tmp/event.json --confirm HASH_FROM_PLAN
```

The OAuth token grants Calendar access and is stored with user-only permissions where supported. Do not commit either credential file.

Planning does not contact Google. Applying rehashes the plan and refuses stale or modified content. Attendee updates default to `none`; use `--notify-attendees` during planning only when invitations should be sent.

Official reference: https://developers.google.com/workspace/calendar/api/quickstart/python

