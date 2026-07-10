# IntelliDiff reference

## File comparison

Exact mode is the default. It reports SHA-256 digests and compares bytes when digests match. Exit code `0` means identical and `1` means different.

Smart mode decodes UTF-8 and can apply explicit normalization:

- `--ignore-newlines`: normalize CRLF and CR to LF.
- `--ignore-whitespace`: strip leading and trailing whitespace on each line.
- `--ignore-blank`: remove blank lines.
- `--ignore-case`: compare case-folded text.
- `--normalize-unicode`: apply Unicode NFKC normalization.

Smart equality means the normalized text matches. It does not mean the original bytes match. Invalid UTF-8 is an error; use exact mode for binary or unknown encodings.

## Directory comparison

`folders` compares relative paths, then SHA-256 content for paths present on both sides. It reports:

- identical files at the same relative path
- changed files at the same relative path
- left-only files
- right-only files

`duplicates` groups files with the same nonzero size and SHA-256 digest. Empty files are omitted from duplicate groups to avoid noise.

Both commands skip hidden paths, `.git`, dependency trees, caches, and common build output by default. `--include-hidden` includes dotfiles and hidden directories but still excludes `.git` and known cache/build directories.

## Other commands

`hash` reports SHA-256, byte size, and whether a null-byte heuristic classifies the file as binary.

`lines` prints a one-based range with optional context. It is for targeted inspection, not content comparison.

All commands accept `--json` except `lines`. Comparison commands use exit code `1` for a valid “different” result and `2` for invalid input or execution errors.
