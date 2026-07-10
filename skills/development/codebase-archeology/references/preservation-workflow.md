# Preservation workflow

## Preserve before improving

Record original checksums, dates when meaningful, archive structure, toolchain files, and known provenance before altering a historical artifact. Use a copy, branch, or worktree for risky changes.

## Establish a canonical shape

- Choose the project root and canonical variant from evidence.
- Keep original source, real fixtures, schemas, build inputs, and useful history.
- Separate vendored dependencies, generated output, caches, and reproducible binaries.
- Replace machine-specific paths with documented configuration only after proving the replacement.

## Recover the build

Start from documented or historically plausible toolchains. Record versions and environment assumptions. Prefer the least invasive path that reproduces behavior. A container, virtual machine, emulator, compatibility layer, port, and rewrite solve different preservation problems; state which one is being attempted.

## Modernize deliberately

Modernization may improve maintainability but can erase behavior or evidence. Add characterization tests, preserve wire and file formats, and keep the original artifact when comparison remains valuable.

## Curate the repository

Create durable README or build notes only after facts are established. Keep temporary inventories and triage reports out of the final repository. Initialize or commit version control only when requested, after reviewing the exact preservation surface.
