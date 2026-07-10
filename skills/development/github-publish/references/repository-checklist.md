# Repository checklist

## Identity and scope

- Confirm the project root and intended repository owner/name.
- Confirm visibility and license rather than selecting them from habit.
- Inspect existing remotes and history before initializing or creating anything.
- Verify Git author name and email are configured; do not mutate them silently.
- Separate requested changes from unrelated worktree changes.

## Public surface

- The first README sentence says what the project is and who uses it.
- Installation and quickstart commands run as written.
- The license matches the owner's sharing intent.
- Contribution, security, or conduct documents exist only when the project needs them.
- Descriptions and topics state current behavior rather than aspirations.

## Repository hygiene

- Generated output, dependencies, caches, credentials, and local-machine files are ignored.
- Lockfiles, migrations, fixtures, schemas, and generated sources are retained when they protect reproducibility or ship with the project.
- No stale paths, task notes, absolute user paths, environment files, or unreviewed large binaries are staged.
- Executable files have correct modes and line endings.

## Verification

- Run relevant tests, builds, linters, formatters, and repository validators.
- Review `git diff --cached --check` and the staged file list.
- After pushing, verify the remote branch, default branch, repository metadata, and CI result.
