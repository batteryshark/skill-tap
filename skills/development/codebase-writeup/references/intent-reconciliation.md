# Intent reconciliation

Use this lens when documentation, comments, diagrams, runbooks, or maintainer statements may no longer match the implemented system. The goal is to restore one trustworthy story without erasing useful history.

## Build a claim matrix

Extract material claims, then check each against the narrowest available implementation evidence.

```text
Claim:
Source and date:
Implementation evidence:
Status:
Impact:
Action:
Confidence:
```

Use these statuses:

- **Aligned:** the current implementation supports the claim.
- **Stale:** the claim described an earlier system and should be updated or clearly dated.
- **Contradicted:** current evidence directly conflicts with the claim.
- **Unimplemented intent:** the document describes a planned or desired state not present in the system.
- **Implementation drift:** behavior changed without a corresponding durable explanation.
- **Unverified:** available evidence cannot establish the claim safely.

## Choose the reconciliation action

- Update documentation when behavior is established and the text is stale.
- Update code only when the documented behavior is an active requirement and the user authorized implementation work.
- Preserve and supersede historical decision records instead of rewriting their original context.
- Mark aspirational architecture explicitly rather than presenting it as current behavior.
- Ask a narrow owner question when the mismatch affects safety, compatibility, ownership, or a consequential design choice.
- Remove duplicate or competing explanations after their unique context has been preserved in the authoritative location.

## Evidence rules

Distinguish documented intent, observed implementation, reproduced behavior, and inference. A missing code path does not prove the document was wrong; the implementation may be incomplete. A passing test establishes only the behavior it exercises. Report the scope sampled in large repositories and avoid declaring global alignment from a single execution path.
