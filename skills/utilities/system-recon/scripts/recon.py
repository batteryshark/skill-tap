#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Collect a bounded read-only system inventory without secret values."""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=("basic", "development", "network"), default="basic")
    args = parser.parse_args()
    data = {"os": platform.system(), "release": platform.release(), "version": platform.version(), "machine": platform.machine(), "python": platform.python_version(), "cpu_count": os.cpu_count(), "disk": shutil.disk_usage("/")._asdict()}
    if args.profile == "development":
        data["commands"] = {name: shutil.which(name) for name in ("git", "python3", "node", "go", "cargo", "docker", "uv")}
    elif args.profile == "network":
        command = ["ipconfig", "getifaddr", "en0"] if platform.system() == "Darwin" else (["ip", "-brief", "address"] if shutil.which("ip") else [])
        if command:
            run = subprocess.run(command, capture_output=True, text=True, timeout=5, check=False)
            data["network_summary"] = run.stdout.strip()
            data["network_status"] = run.returncode
        else:
            data["network_summary"] = "unavailable"
    print(json.dumps(data, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
