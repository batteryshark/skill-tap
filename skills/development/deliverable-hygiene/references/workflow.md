# Workflow

## Doctrine Mode

Use doctrine mode during ordinary implementation or cleanup.

1. Inventory the human surface with `rg --files`, manifests, tests, docs, and source roots.
2. Identify generated, vendored, build, cache, and dependency output to ignore.
3. Keep scratch under `.agent-work/deliverable-hygiene/<run-id>/` if temporary notes are needed.
4. Add `.agent-work/` to `.gitignore` when using scratch and the ignore is missing.
5. Make the requested change with the doctrine defaults: code-first rationale, behavioral tests, useful comments, hard deletion.
6. Validate with the narrowest relevant build, test, typecheck, or static check.
7. Delete successful scratch before final response.

## Recovery Loop Mode

Use recovery loop mode when the project already drifted or the user asks to restore hygiene.

Default cap: three passes.

Run folder:

```text
.agent-work/deliverable-hygiene/<run-id>/
  auditor-pass-N.md
  fixer-pass-N.md
  validator-pass-N.md
  status.md
```

These files are disposable. They exist so agents can be blunt and messy without contaminating the deliverable.

Use this `status.md` shape when a run stops blocked:

```markdown
# Deliverable Hygiene Run Status

Verdict: BLOCKED
Last pass: N
Decision needed: ...
Evidence: ...
Checks attempted: ...
Resume from: auditor | fixer | validator
Delete when: the blocking decision is resolved and validation passes
```

### Pass Step 1: Auditor

The auditor reads the repo and writes concrete findings only:

```markdown
# Auditor Pass N

## Findings

| ID | Category | Severity | Evidence | Action |
|---|---|---|---|---|
| DH-001 | Agent residue | P1 | path:line | Delete |

## Blockers

- Evidence that needs user confirmation before deletion.
```

Severity:

- P0: blocks understanding or correctness enough that cleanup cannot be trusted.
- P1: clear hygiene violation with meaningful maintenance cost.
- P2: useful cleanup if nearby, but not worth churn alone.

### Pass Step 2: Fixer

The fixer handles P0 and P1 findings first:

- Delete residue and dead compatibility paths when evidence is clear.
- Distill useful rationale into source, concise comments, ADRs, architecture docs, or `.project/` only when the human value is durable.
- Rewrite or remove test theater. If a weak test is the only coverage for important behavior, rewrite it as a behavior test before deleting it.
- Split or rename mental-load hotspots only inside the agreed cleanup scope.
- Record unfixed findings in the run folder, not in project docs.

The fixer must re-open files and verify the auditor's evidence. Auditor reports are leads, not truth.

### Pass Step 3: Validator

The validator is evidence-strict:

- Confirm fixed findings no longer exist.
- Search for leaked loop artifacts outside `.agent-work/`.
- Check that `.agent-work/` is ignored if it exists.
- Run relevant tests or checks.
- Fail only on concrete repository evidence tied to the doctrine.

Validator verdict:

- GREEN: no P0 or P1 violations remain in scope, checks pass or skipped checks are justified.
- BLOCKED: user confirmation or external information is required. Stop the loop immediately.
- CAPPED: three passes ran and concrete P0 or P1 findings remain.

### Loop Control

After validation:

- GREEN: delete `.agent-work/deliverable-hygiene/<run-id>/` and report the result.
- BLOCKED: keep only the minimal run-folder evidence needed to resume and explain what decision is needed. Delete the folder after that decision is resolved and validation passes.
- CAPPED: keep the run folder and summarize remaining evidence.
- Otherwise, begin the next pass with only remaining P0 and P1 findings.

## Subagent Use

When subagents are available and allowed, keep roles independent:

- Launch auditor and validator with fresh context where practical.
- Do not show the validator the fixer's self-assessment before it inspects the repo.
- Give each subagent the run folder path and the doctrine references.
- Keep raw subagent outputs in the run folder.

When subagents are not available, run auditor, fixer, and validator sequentially. Label the outputs the same way so the loop can be resumed later.

## Portable delegation

Use the local agent system's isolation primitive when one exists. Otherwise run the roles sequentially. In either case:

- Write temporary prompts, reports, diffs, and status files only inside `.agent-work/deliverable-hygiene/<run-id>/`.
- Use a worktree or forked workspace when edits are risky or parallel.
- Preserve role separation even when one agent performs each pass.
- Fall back to sequential auditor, fixer, and validator passes when no subagent primitive is available.

## Final Response

Report only durable facts:

- What categories were cleaned.
- What files changed.
- What checks ran.
- Whether the run folder was deleted or kept.
- What remains blocked, if anything.

Do not paste raw auditor or validator dumps unless the user asks.
