---
name: google-maps-query
description: Query current Google Maps Platform geocoding, Places, and Routes APIs from a thin JSON CLI using an environment-supplied API key and explicit billable-call execution. Use when a user needs place IDs, coordinates, place details, text search, or route distance and duration from Google Maps data.
---

# Google Maps Query

Use `bin/google-maps-query`. Calls may incur Google Cloud charges and transmit the supplied locations to Google.

## Workflow

1. Read [references/setup-and-privacy.md](references/setup-and-privacy.md).
2. Select the narrowest command.
3. Show the user the query and confirm that a billable external call is intended unless their request already explicitly authorizes it.
4. Run with `--execute`.
5. Treat returned data as time-sensitive and retain place IDs for unambiguous follow-up calls.

Never print or persist `GOOGLE_MAPS_API_KEY`.

