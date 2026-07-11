#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Emit read-only PowerShell for auditing selected Windows AI policy areas."""

from __future__ import annotations

import argparse
import json
import platform


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("audit", "powershell"), default="audit", nargs="?")
    args = parser.parse_args()
    paths = [r"HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsAI", r"HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsCopilot", r"HKCU:\SOFTWARE\Policies\Microsoft\Windows\WindowsCopilot", r"HKLM:\SOFTWARE\Policies\Microsoft\Edge"]
    script = "$paths = @(" + ",".join("'" + item + "'" for item in paths) + "); foreach ($path in $paths) { Write-Output \"## $path\"; Get-ItemProperty -Path $path -ErrorAction SilentlyContinue | Format-List }"
    if args.action == "powershell":
        print(script)
    else:
        print(json.dumps({"windows": platform.system() == "Windows", "policy_paths": paths, "read_only_powershell": script, "note": "Verify every value against official documentation for the target build."}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
