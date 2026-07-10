# Tracker schema

Use this compact default for `.project/tracker.md`:

```markdown
# Project Tracker: PROJECT

Updated: YYYY-MM-DD

## Current state

- Objective:
- Status:
- Main constraint:
- Blocked on:
- Next action:

## Active workstreams

### Workstream name

- Status: active | paused | blocked
- Owner:
- Current evidence:
- Completion evidence:
- Next action:
- Stop condition:

## Important paths and artifacts

- `relative/path`: why it matters

## Recent attempts and results

### YYYY-MM-DD — Short attempt

- Intent:
- Method:
- Result:
- Evidence:
- Follow-up:

## Decisions

### Decision

- Choice:
- Rationale:
- Alternatives rejected:
- Reconsider when:

## Open questions and theories

### Question or theory

- Type: question | theory
- Status: open | testing | answered | weakened | disproven | deferred
- Evidence:
- Evidence needed:
- Next validation:

## Completed or resolved

- YYYY-MM-DD: concise outcome
```

Session notes under `.project/sessions/` may contain fuller evidence:

```markdown
# Session: TITLE

Date: YYYY-MM-DD HH:MM

## Starting context
## Work performed
## Evidence and results
## Decisions and pivots
## Artifacts
## Open questions
## Next actions
```

Keep the dashboard authoritative for current state. Session notes support it; they do not replace it.
