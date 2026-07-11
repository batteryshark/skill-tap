# Report template

```yaml
summary:
  target_path: string
  evidence_mode: code-only|code-and-runtime
  strictness: strict|balanced
  overall_score: number
  verdict: high-alignment|moderate-alignment|low-alignment
  scope: unofficial-historical-single-player-baseline

category_scores:
  - category: string
    score: number
    maximum: number

failed_rules:
  - rule_id: string
    severity: P1|P2|P3
    finding: string
    evidence:
      - type: file|test|runtime
        ref: string

unknown_rules:
  - rule_id: string
    missing_evidence: string

recommendations:
  - priority: P1|P2|P3
    action: string
    maps_to_rules: [string]

appendix:
  rules:
    - rule_id: string
      status: PASS|FAIL|UNKNOWN
      evidence: [string]
      notes: string
```

Include every rule in the appendix. A score without the per-rule evidence table is incomplete.

