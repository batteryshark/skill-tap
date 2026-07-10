---
name: github-publish
description: Publish a local project to GitHub or update an existing GitHub repository with deliberate visibility, scoped commits, appropriate ignore rules, useful metadata, and verified CI. Use when creating a repository, connecting a local checkout to GitHub, preparing the first push, publishing local changes, or repairing incomplete repository setup.
---

# GitHub publish

Publish the intended project without leaking local state, staging unrelated work, or guessing repository policy.

## Prerequisites

Require local `git` and GitHub CLI `gh`. Run `gh` and networked Git commands with host access when the sandbox cannot reach the system keychain, DNS, or GitHub. Never diagnose credentials as invalid from a sandbox-only failure; recheck `gh auth status` with host access.

Before creating a remote, establish the owner, repository name, and visibility from the request. Visibility changes are consequential; do not infer public, private, or internal when the choice is not already clear.

## Workflow

1. Run `bin/github-publish <project>` for a read-only local preflight.
2. Inspect `git status`, existing history, branches, remotes, configured identity, ignore rules, README, license, generated output, suspected secret-bearing files, and large artifacts.
3. Read [`references/repository-checklist.md`](references/repository-checklist.md). Fix only repository setup that belongs to the requested publication.
4. Build `.gitignore` from actual project evidence. Use [`references/ignore-guidance.md`](references/ignore-guidance.md); keep lockfiles, fixtures, editor settings, and generated sources when they are intentionally part of the project.
5. Run the project's relevant checks and execute documented quickstart commands when practical.
6. Stage only intended files. Review the staged diff and run `git diff --cached --check` before committing.
7. For a new remote, use the current `gh repo create --help` flags and the confirmed visibility. For an existing remote, verify its owner, target branch, and divergence before pushing.
8. Push with tracking when needed, apply a concise description and a small set of accurate topics, then verify the remote branch and CI result.

## Safety

- Do not overwrite an existing remote, force-push, rewrite history, or change visibility without explicit authorization.
- Do not silently change Git identity or add attribution trailers.
- Do not stage the entire worktree when unrelated changes are present.
- Do not print suspected secret values while scanning or reporting.
- Treat repository creation, pushes, releases, issue creation, and metadata changes as external writes within the user's requested scope.

## Report

State repository URL, visibility, branch, commit, checks, CI result, metadata changes, and anything still requiring owner input.

Use [`agents/reviewer.md`](agents/reviewer.md) for an independent publication preflight.
