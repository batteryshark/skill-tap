# Windows C/C++ Recipes

## Architecture Checks

Use the compiler's machine target before building:

```powershell
gcc -dumpmachine
```

Expected values:

```text
x86_64-w64-mingw32  # 64-bit Windows
i686-w64-mingw32    # 32-bit Windows
```

Inspect a built executable or object when architecture matters:

```powershell
objdump -f tool.exe
objdump -p tool.exe | Select-String "DLL Name|subsystem|MajorSubsystemVersion|ImageBase"
```

Portable MinGW-built tools should not import these runtime DLLs:

```text
libgcc_s_*.dll
libstdc++-6.dll
libwinpthread-1.dll
```

## Old Windows Targets

Use API level defines to prevent accidental calls to newer APIs:

```powershell
gcc -D_WIN32_WINNT=0x0501 -DNTDDI_VERSION=0x05010000 -O2 -o xp-ish.exe main.c
gcc -D_WIN32_WINNT=0x0601 -DNTDDI_VERSION=0x06010000 -O2 -o win7.exe main.c
gcc -D_WIN32_WINNT=0x0A00 -DNTDDI_VERSION=0x0A000000 -O2 -o win10.exe main.c
```

This only controls headers and conditional declarations. It does not guarantee runtime compatibility. Verify imports and test on the target OS. For older targets, avoid UCRT toolchains unless the runtime deployment plan is explicit.

## DLL Exports

Use a `.def` file when exact export names or ordinals matter:

```def
LIBRARY patch
EXPORTS
    InitPatch @1
    ShutdownPatch @2
```

Build:

```powershell
gcc -shared -O2 -Wall -Wextra -static -static-libgcc -o patch.dll patch.c patch.def
objdump -p patch.dll | Select-String "Export|ordinal|Name"
objdump -p patch.dll | Select-String "DLL Name"
```

For stdcall name decoration problems in 32-bit builds, consider:

```text
-Wl,--enable-stdcall-fixup
-Wl,--kill-at
```

Only use those flags when they match the loader or host application's export expectations.

## Static Runtime Flags

For small tools copied between machines, default to static MinGW runtime linking:

```text
C:   -static -static-libgcc
C++: -static -static-libgcc -static-libstdc++
```

Use `-static` specifically to avoid carrying MinGW runtime DLLs beside the executable or patch DLL. Core Windows DLLs remain imports and are expected.

Verify after every portable build:

```powershell
objdump -p tool.exe | Select-String "DLL Name"
```

Rebuild if the import list includes `libgcc_s_*.dll`, `libstdc++-6.dll`, or `libwinpthread-1.dll`.

## Subsystems

Console program:

```powershell
gcc -O2 -static -static-libgcc -o tool.exe tool.c
```

GUI program without console:

```powershell
gcc -O2 -mwindows -static -static-libgcc -o app.exe app.c
```

Unicode entry point:

```powershell
gcc -O2 -municode -static -static-libgcc -o app.exe app.c
```

## Resources

Compile `.rc` resources with the toolchain's `windres`:

```powershell
windres version.rc -O coff -o version.res
gcc -O2 -static -static-libgcc -o app.exe main.c version.res
```

## Inline Assembly And Patch Payloads

For small patch payloads, first build an object file and inspect it before linking:

```powershell
gcc -m32 -ffreestanding -fno-asynchronous-unwind-tables -fno-ident -Os -c payload.c -o payload.o
objdump -d payload.o
```

Prefer the explicit `C:\msys64\mingw32\bin` 32-bit toolchain over relying on `-m32`; use `-m32` only after confirming the active compiler supports it.

## POSIX Makefiles

Try native MinGW make first:

```powershell
mingw32-make
```

If the Makefile depends on POSIX shell syntax, use MSYS2 bash deliberately:

```powershell
& "C:\msys64\usr\bin\bash.exe" -lc "cd /c/path/to/project && make"
```

Do not mix MSYS path conversion into native builds unless the Makefile requires it.

## Clang With GNU Target

If using a Clang binary that has a MinGW sysroot available:

```powershell
clang --target=x86_64-w64-windows-gnu -O2 -Wall -o tool.exe tool.c
clang++ --target=i686-w64-windows-gnu -std=c++17 -O2 -o tool32.exe main.cpp
```

If headers or startup objects are missing, switch to MSYS2 MinGW GCC instead of trying random flags.
