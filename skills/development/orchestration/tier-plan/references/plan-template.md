# Plan: <job name>

## Frame

- **Deliverable:** <what exists at the end that does not exist now>
- **Done when:** <how anyone confirms it — or "no whole-job check exists", which
  is itself the most important line in this plan>
- **Already decided:** <constraints and prior choices, not up for reconsideration>
- **Roster:** <path to roster.yaml, or what was assumed and why>
- **Pattern:** sweep | funnel | mixed | one-off graph

## Routing table

Scores are `intent / blast / coupling / novelty − verify`. Budget is
`branch + backtrack + constraints`.

| # | Unit | Deps | I | B | C | N | V | Σ | Tier | Bud | Model | Verify | On fail |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | | — | 0 | 1 | 0 | 0 | 2 | −1 | T1 | min | fast | `pytest tests/x.py` | retry ×4 |
| 2 | | 1 | | | | | | | | | | | |
| 3 | | 1 | | | | | | | | | | | |

**Overrides applied:** <which units, which override, why. Omit if none — but say
"none" rather than leaving it blank, so a reader knows it was considered.>

**Unverified units:** <the rows with V=0. This is where the risk is. If the list
is empty, say so — it is a good sign and worth stating.>

## Waves

| Wave | Units | Parallel | Write conflicts |
|---|---|---|---|
| 1 | 1, 2, 5 | yes | none — disjoint paths |
| 2 | 3, 4 | yes | 3 and 4 both write `config/` → serialize |
| 3 | 6 | — | synthesis |

**Critical path:** <the chain that sets wall-clock, and which unit on it is the
best candidate for shortening>

## Forecast

| Tier | Units | Est. tokens | Cost index | Weighted |
|---|---|---|---|---|
| T1 | | | | |
| T2 | | | | |
| T3 | | | | |
| Handoff tax | <units × tax> | | | |
| **Total** | | | | |

- **All-top-tier counterfactual:** <weighted total if every unit ran at T3>
- **Ratio:** <counterfactual ÷ total>. Below ~1.5 the orchestration is not
  earning its overhead — recommend running it straight instead.
- **Least reliable estimates:** <the 2–3 units most likely to blow the forecast,
  and what would cause it>

## Risks

| Risk | Unit(s) | Signal it is happening | Response |
|---|---|---|---|
| | | | |

## Stop conditions

- <what halts the whole run rather than escalating a single unit>
- <budget ceiling, if any>
- Any unit escalated twice without success — stop and report.
- Same failure signature on three units — template defect, fix before continuing.
