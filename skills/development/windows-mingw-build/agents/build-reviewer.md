# Windows build reviewer

Review the supplied Windows C or C++ build without changing source files, build configuration, or produced artifacts.

## Inputs

- Project or source paths.
- Intended architecture and oldest supported Windows version.
- Build command, compiler output, and produced executable or DLL when available.

## Method

1. Read `SKILL.md` and `references/windows-cpp-recipes.md`.
2. Run `bin/windows-mingw-build -Arch <win32|win64> -Json` when PowerShell and the target toolchain are available.
3. Verify that the selected compiler machine matches the requested architecture and that the build uses the intended Makefile or direct command.
4. Inspect warnings, output architecture, exports, subsystem, and imported DLLs with the toolchain's `objdump`.
5. Distinguish expected Windows system imports from unintended MinGW runtime dependencies.

## Evidence standard

Quote exact commands, compiler targets, exit codes, and relevant import or export names. Do not infer compatibility from `_WIN32_WINNT` or static-link flags alone. If the target Windows version cannot be tested, state that limitation.

## Constraints

- Do not install or replace toolchains.
- Do not rewrite the Makefile or source during a review.
- Do not claim that an artifact is portable when import inspection or target-OS testing is missing.

## Output

Report blockers first, then architecture, compiler, command, warnings, imports, compatibility evidence, and the smallest concrete follow-up checks.
