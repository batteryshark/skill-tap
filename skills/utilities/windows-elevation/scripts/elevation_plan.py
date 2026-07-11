#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Emit a non-mutating Windows elevation capability and command plan."""

from __future__ import annotations

import argparse
import json
import platform
import shutil


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", nargs=argparse.REMAINDER, help="Command to quote in the plan; it is never executed")
    args = parser.parse_args()
    windows = platform.system() == "Windows"
    methods = {name: shutil.which(name) for name in ("sudo", "gsudo", "powershell", "pwsh", "schtasks")}
    print(json.dumps({"windows": windows, "available": methods, "requested_command": args.command, "executed": False, "guidance": "Use supported interactive administrator elevation; SYSTEM requires a separate reviewed plan."}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
