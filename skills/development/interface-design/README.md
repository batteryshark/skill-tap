# Interface design

Two skills that catch bad interface design, named for the Norman door — the
elegant pull handle on a door that opens with a push. Software ships that
door constantly: the feature nobody finds, the form that asks what the system
already knows, the delete control beside rename.

| Skill | When |
|---|---|
| [`norman`](norman/) | While building. Runs a five-question walkthrough on every surface you add or change: has it earned its place, can the user find it, what does it cost, do they know it worked, does it survive first use, hundredth use, and interruption. |
| [`norman-audit`](norman-audit/) | After the fact. Audits a diff or a whole workspace from source alone and returns ranked one-line findings with fixes, citing file and line. |

They share one vocabulary:

- **Eight failure tags** — `cut:` `orphan:` `scentless:` `excise:` `recall:`
  `mute:` `trap:` `amnesia:` — each defined by the research in the packages'
  `references/`.
- **Severity S1–S4** — higher is worse; S4 first.
- **The `norman:` marker** — `norman: <ceiling>, <upgrade trigger>` comments
  record deliberate UX corners; `norman/bin/norman` harvests them into a
  ledger, and `norman-audit/bin/norman-audit` collects mechanical evidence
  (form counts, sub-24px targets, undocumented flags, storage call sites).

GUI, CLI, and TUI are covered at parity: a missing `--help` example and an
unlabeled icon button are the same door.

Each package is self-contained per the tap contract — the `references/` files
are intentionally duplicated in both so either skill can be copied out alone.
