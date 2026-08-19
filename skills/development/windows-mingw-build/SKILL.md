---
name: windows-mingw-build
description: Build, troubleshoot, or set up native Windows C and C++ compilation with MinGW-w64, MSYS2, GCC, G++, Clang, LLVM, mingw32-make, static runtime linking, resources, DLLs, or Makefiles. Use when producing 32-bit or 64-bit Windows artifacts, selecting a Windows GNU toolchain, diagnosing architecture or linker problems, avoiding CMake, or avoiding bundled MinGW runtime DLLs.
---

# Windows MinGW build

Build native Windows artifacts with an explicit architecture, a verified toolchain, and reviewable runtime dependencies.

## Workflow

1. Choose `win64` or `win32` before changing `PATH`. Prefer the matching MSYS2 directory:
   - `win64`: `C:\msys64\mingw64\bin`, target `x86_64-w64-mingw32`.
   - `win32`: `C:\msys64\mingw32\bin`, target `i686-w64-mingw32`.
2. Prefer an existing Makefile or direct compiler commands. Use CMake only when the project requires it or the user requests it.
3. Run `bin/windows-mingw-build -Arch win64` or `bin/windows-mingw-build -Arch win32` from MSYS2, Git Bash, WSL, or another POSIX shell with PowerShell available. In native PowerShell, run `scripts/with-win-toolchain.ps1` directly.
4. Verify `gcc -dumpmachine`, compiler version, make, resource tools, and a writable compiler temp directory before building.
5. Build with warnings enabled. For portable artifacts, statically link the MinGW runtime unless the target explicitly requires dynamic MinGW libraries.
6. Inspect the resulting executable or DLL with `objdump -p`; treat core Windows DLL imports as normal and investigate MinGW runtime DLL imports.

```powershell
& "<skill-path>\scripts\with-win-toolchain.ps1" -Arch win64 -Compiler gcc
& "<skill-path>\scripts\with-win-toolchain.ps1" -Arch win32 -Compiler gcc -Command "mingw32-make"
```

The helper prepends a discovered toolchain to the current child process, selects writable `TEMP` and `TMP` paths, exports compiler variables, and applies static-runtime defaults. Pass `-NoStaticRuntime` when dynamic MinGW runtime dependencies are intentional. Pass `-Json` to capture the selected toolchain as evidence.

## Defaults and checks

- Prefer MSYS2 MinGW GCC/G++ for ordinary Windows tools because one toolchain supplies headers, import libraries, `windres`, `dlltool`, `ar`, `strip`, and `mingw32-make`.
- Prefer the explicit 32-bit toolchain over adding `-m32` to a 64-bit compiler.
- Use standalone LLVM/Clang only after proving a compatible Windows GNU or MSVC sysroot exists.
- Set `_WIN32_WINNT` to the oldest API level the program may call, but do not treat the define as proof of runtime compatibility.
- Use `-static -static-libgcc` for portable C artifacts and add `-static-libstdc++` for C++.
- Rebuild or document the deployment requirement if imports include `libgcc_s_*.dll`, `libstdc++-6.dll`, or `libwinpthread-1.dll`.
- If GCC cannot create temporary files, point `TEMP` and `TMP` at a writable directory inside the workspace.

Read [`references/windows-cpp-recipes.md`](references/windows-cpp-recipes.md) for direct build commands, DLL exports, resources, old Windows targets, subsystems, inline assembly, POSIX Makefiles, and Clang sysroots.

Use [`agents/build-reviewer.md`](agents/build-reviewer.md) when an independent agent should inspect the build configuration and resulting imports without changing the project.
