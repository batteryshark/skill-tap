[CmdletBinding()]
param(
    [ValidateSet("win64", "win32")]
    [string]$Arch = "win64",

    [ValidateSet("auto", "gcc", "clang")]
    [string]$Compiler = "auto",

    [string]$Command,

    [string]$TempDir,

    [switch]$NoStaticRuntime,

    [switch]$Json,

    [switch]$IncludeMsysUsr,

    [switch]$Quiet
)

$ErrorActionPreference = "Stop"

function Get-ExistingDirs {
    param([string[]]$Dirs)

    $seen = @{}
    foreach ($dir in $Dirs) {
        if ([string]::IsNullOrWhiteSpace($dir)) {
            continue
        }

        $expanded = [Environment]::ExpandEnvironmentVariables($dir)
        if (Test-Path -LiteralPath $expanded -PathType Container) {
            $resolved = (Resolve-Path -LiteralPath $expanded).Path
            $key = $resolved.ToLowerInvariant()
            if (-not $seen.ContainsKey($key)) {
                $seen[$key] = $true
                $resolved
            }
        }
    }
}

function Find-Exe {
    param(
        [string[]]$Dirs,
        [string[]]$Names
    )

    foreach ($dir in $Dirs) {
        foreach ($name in $Names) {
            $candidate = Join-Path $dir $name
            if (Test-Path -LiteralPath $candidate -PathType Leaf) {
                return (Resolve-Path -LiteralPath $candidate).Path
            }
        }
    }

    return $null
}

function Get-VersionLine {
    param([string]$Exe)

    if (-not $Exe) {
        return $null
    }

    try {
        $line = & $Exe --version 2>$null | Select-Object -First 1
        return $line
    } catch {
        return $null
    }
}

function Get-DumpMachine {
    param([string]$Exe)

    if (-not $Exe) {
        return $null
    }

    try {
        $line = & $Exe -dumpmachine 2>$null | Select-Object -First 1
        return $line
    } catch {
        return $null
    }
}

function Resolve-WritableTempDir {
    param([string]$RequestedTempDir)

    $candidates = New-Object System.Collections.Generic.List[string]
    if (-not [string]::IsNullOrWhiteSpace($RequestedTempDir)) {
        $candidates.Add($RequestedTempDir)
    }
    if (-not [string]::IsNullOrWhiteSpace($env:WINBUILD_TEMP)) {
        $candidates.Add($env:WINBUILD_TEMP)
    }
    $candidates.Add((Join-Path (Get-Location).Path ".winbuild-tmp"))
    $candidates.Add("C:\tmp\codex-winbuild-tmp")

    foreach ($candidate in $candidates) {
        try {
            $expanded = [Environment]::ExpandEnvironmentVariables($candidate)
            $dir = New-Item -ItemType Directory -Force -Path $expanded
            $resolved = $dir.FullName
            $testFile = Join-Path $resolved ".write-test-$PID.tmp"
            Set-Content -LiteralPath $testFile -Value "ok" -NoNewline
            Remove-Item -LiteralPath $testFile -Force
            return $resolved
        } catch {
            continue
        }
    }

    throw "Could not find or create a writable compiler temp directory. Pass -TempDir with a writable path."
}

$msysRoot = if ($env:MSYS2_ROOT) { $env:MSYS2_ROOT } else { "C:\msys64" }

if ($Arch -eq "win64") {
    $gccDirs = Get-ExistingDirs @(
        $env:MINGW64_BIN,
        (Join-Path $msysRoot "mingw64\bin"),
        "C:\tools\mingw64\bin",
        "C:\tools\w64devkit\bin",
        "C:\mingw64\bin"
    )
    $clangDirs = Get-ExistingDirs @(
        $env:CLANG64_BIN,
        (Join-Path $msysRoot "clang64\bin"),
        "C:\llvm-mingw\bin",
        "C:\Program Files\LLVM\bin"
    )
    $expectedMachine = "x86_64-w64-mingw32"
    $clangTarget = "x86_64-w64-windows-gnu"
} else {
    $gccDirs = Get-ExistingDirs @(
        $env:MINGW32_BIN,
        (Join-Path $msysRoot "mingw32\bin"),
        "C:\tools\mingw32\bin",
        "C:\mingw32\bin"
    )
    $clangDirs = Get-ExistingDirs @(
        $env:CLANG32_BIN,
        "C:\llvm-mingw\bin",
        "C:\Program Files\LLVM\bin"
    )
    $expectedMachine = "i686-w64-mingw32"
    $clangTarget = "i686-w64-windows-gnu"
}

$selected = $null
$warnings = New-Object System.Collections.Generic.List[string]

if ($Compiler -eq "auto" -or $Compiler -eq "gcc") {
    $cc = Find-Exe $gccDirs @("gcc.exe")
    $cxx = Find-Exe $gccDirs @("g++.exe")
    if ($cc -and $cxx) {
        $bin = Split-Path -Parent $cc
        $selected = [ordered]@{
            arch = $Arch
            compiler = "gcc"
            bin = $bin
            cc = $cc
            cxx = $cxx
            make = Find-Exe @($bin) @("mingw32-make.exe", "make.exe")
            windres = Find-Exe @($bin) @("windres.exe")
            dlltool = Find-Exe @($bin) @("dlltool.exe")
            ar = Find-Exe @($bin) @("ar.exe")
            strip = Find-Exe @($bin) @("strip.exe")
            expected_machine = $expectedMachine
            dumpmachine = Get-DumpMachine $cc
            version = Get-VersionLine $cc
        }
    }
}

if (-not $selected -and ($Compiler -eq "auto" -or $Compiler -eq "clang")) {
    $cc = Find-Exe $clangDirs @("clang.exe")
    $cxx = Find-Exe $clangDirs @("clang++.exe")
    if ($cc -and $cxx) {
        $bin = Split-Path -Parent $cc
        $selected = [ordered]@{
            arch = $Arch
            compiler = "clang"
            bin = $bin
            cc = $cc
            cxx = $cxx
            make = Find-Exe @($bin) @("mingw32-make.exe", "make.exe")
            windres = Find-Exe @($bin) @("windres.exe", "llvm-windres.exe")
            dlltool = Find-Exe @($bin) @("dlltool.exe", "llvm-dlltool.exe")
            ar = Find-Exe @($bin) @("ar.exe", "llvm-ar.exe")
            strip = Find-Exe @($bin) @("strip.exe", "llvm-strip.exe")
            expected_machine = $clangTarget
            dumpmachine = $null
            version = Get-VersionLine $cc
        }

        if ($bin -like "C:\Program Files\LLVM*") {
            $warnings.Add("Standalone LLVM was selected. It may compile but fail to link unless a MinGW or MSVC sysroot is configured.")
        }
    }
}

if (-not $selected) {
    $searched = @($gccDirs + $clangDirs) | Where-Object { $_ } | Select-Object -Unique
    throw "No $Arch $Compiler toolchain found. Searched: $($searched -join '; ')"
}

$pathParts = New-Object System.Collections.Generic.List[string]
$pathParts.Add($selected.bin)
if ($IncludeMsysUsr) {
    $usrBin = Join-Path $msysRoot "usr\bin"
    if (Test-Path -LiteralPath $usrBin -PathType Container) {
        $pathParts.Add((Resolve-Path -LiteralPath $usrBin).Path)
    }
}

$oldPath = $env:Path
$env:Path = (($pathParts.ToArray() + ($oldPath -split ";" | Where-Object { $_ })) -join ";")
$env:CC = Split-Path -Leaf $selected.cc
$env:CXX = Split-Path -Leaf $selected.cxx
if ($selected.make) { $env:MAKE = Split-Path -Leaf $selected.make }
if ($selected.windres) { $env:WINDRES = Split-Path -Leaf $selected.windres }
if ($selected.ar) { $env:AR = Split-Path -Leaf $selected.ar }
if ($selected.strip) { $env:STRIP = Split-Path -Leaf $selected.strip }

$resolvedTempDir = Resolve-WritableTempDir $TempDir
$env:TEMP = $resolvedTempDir
$env:TMP = $resolvedTempDir

$staticRuntime = -not $NoStaticRuntime
if ($staticRuntime) {
    $env:WINBUILD_C_STATIC_FLAGS = "-static -static-libgcc"
    $env:WINBUILD_CXX_STATIC_FLAGS = "-static -static-libgcc -static-libstdc++"
    $env:WINBUILD_LDFLAGS = "-static"
    if ([string]::IsNullOrWhiteSpace($env:LDFLAGS)) { $env:LDFLAGS = $env:WINBUILD_LDFLAGS }
    if ([string]::IsNullOrWhiteSpace($env:CFLAGS)) { $env:CFLAGS = "-O2 -Wall -Wextra -D_WIN32_WINNT=0x0601 $($env:WINBUILD_C_STATIC_FLAGS)" }
    if ([string]::IsNullOrWhiteSpace($env:CXXFLAGS)) { $env:CXXFLAGS = "-std=c++17 -O2 -Wall -Wextra -D_WIN32_WINNT=0x0601 $($env:WINBUILD_CXX_STATIC_FLAGS)" }
}

$selected["path_prepend"] = $pathParts.ToArray()
$selected["temp_dir"] = $resolvedTempDir
$selected["static_runtime"] = $staticRuntime
$selected["static_flags"] = [ordered]@{
    c = if ($staticRuntime) { $env:WINBUILD_C_STATIC_FLAGS } else { $null }
    cxx = if ($staticRuntime) { $env:WINBUILD_CXX_STATIC_FLAGS } else { $null }
    ldflags = if ($staticRuntime) { $env:WINBUILD_LDFLAGS } else { $null }
}
$selected["env"] = [ordered]@{
    CC = $env:CC
    CXX = $env:CXX
    MAKE = $env:MAKE
    WINDRES = $env:WINDRES
    AR = $env:AR
    STRIP = $env:STRIP
    CFLAGS = $env:CFLAGS
    CXXFLAGS = $env:CXXFLAGS
    LDFLAGS = $env:LDFLAGS
    TEMP = $env:TEMP
    TMP = $env:TMP
}
$selected["warnings"] = $warnings.ToArray()

if ($Json) {
    $selected | ConvertTo-Json -Depth 5
} elseif (-not $Quiet) {
    Write-Host "Selected $($selected.compiler) for $($selected.arch)"
    Write-Host "PATH prepend: $($pathParts.ToArray() -join ';')"
    Write-Host "TEMP/TMP: $resolvedTempDir"
    if ($staticRuntime) {
        Write-Host "Static runtime: enabled"
        Write-Host "C static flags: $($env:WINBUILD_C_STATIC_FLAGS)"
        Write-Host "C++ static flags: $($env:WINBUILD_CXX_STATIC_FLAGS)"
    } else {
        Write-Host "Static runtime: disabled"
    }
    Write-Host "CC: $($selected.cc)"
    Write-Host "CXX: $($selected.cxx)"
    if ($selected.make) { Write-Host "MAKE: $($selected.make)" }
    if ($selected.windres) { Write-Host "WINDRES: $($selected.windres)" }
    if ($selected.dumpmachine) { Write-Host "dumpmachine: $($selected.dumpmachine)" }
    if ($selected.version) { Write-Host "version: $($selected.version)" }
    foreach ($warning in $warnings) {
        Write-Warning $warning
    }
}

if ($Command) {
    if (-not $Quiet) {
        Write-Host "Running: $Command"
    }
    Invoke-Expression $Command
    if ($global:LASTEXITCODE -ne $null -and $global:LASTEXITCODE -ne 0) {
        exit $global:LASTEXITCODE
    }
}
