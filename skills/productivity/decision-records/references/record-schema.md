# Decision-record schema

Adapt the depth to the consequence and reversibility of the decision. A short record is preferable to padded certainty.

## Identity and lifecycle

- **Title:** describe the choice, not a topic area.
- **Date:** use the date the decision was made or recorded and distinguish them when needed.
- **Status:** proposed, accepted, rejected, superseded, or deprecated.
- **Owners:** name the accountable role or group when useful.
- **Relationships:** link records this one supersedes, depends on, or is superseded by.

## Context

State the problem, scope, affected people or systems, and why a decision was needed. Include binding constraints and evidence available at the time. Distinguish later discoveries from original context.

## Decision and alternatives

State the chosen direction precisely enough to guide action. Include only alternatives that were genuinely considered or remain plausible. Describe each alternative's relevant strengths and why it was not selected under the stated constraints.

## Consequences

Record expected benefits, accepted costs, risks, compatibility or migration effects, follow-up obligations, and what becomes easier or harder. Avoid predictions that cannot be observed.

## Evidence, validation, and uncertainty

- Cite requirements, implementation, tests, measurements, incidents, notes, or explicit statements.
- Separate observed facts, documented intent, reproduced behavior, and inference.
- State what evidence would validate the choice and what remains unknown.
- Ask for confirmation when an inferred motive would affect future changes.

## Reconsideration

Name concrete triggers such as a scale boundary, changed requirement, failed metric, new platform capability, maintenance threshold, contract change, or removal of the original constraint. Avoid vague phrases such as "if needed."
