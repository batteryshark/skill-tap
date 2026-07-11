---
name: system-recon
description: "Collect a bounded, read-only system inventory for troubleshooting while identifying privilege gaps and avoiding secrets or invasive enumeration."
---

# Collect a Safe System Inventory

1. Define the troubleshooting question and collect only evidence that can answer it.
2. Read [references/scope.md](references/scope.md), then run `bin/system-recon --profile basic` first. Add networking, storage, runtime, or development profiles only as needed.
3. Keep the run read-only. Do not enumerate browser data, keychains, tokens, private keys, shell history, document contents, or other users' data.
4. Mark checks that were unavailable because of permissions rather than escalating automatically.
5. Review the JSON for hostnames, usernames, addresses, serials, or paths before sharing it outside the machine.

Use [agents/recon-reviewer.md](agents/recon-reviewer.md) to distinguish missing evidence from absence of a condition.
