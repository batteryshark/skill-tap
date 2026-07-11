#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Survey Docker cleanup categories and optionally run one approved prune."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("survey", "images", "containers", "volumes", "builder"), default="survey", nargs="?")
    parser.add_argument("--apply", action="store_true", help="Execute the selected prune action")
    args = parser.parse_args()
    if not shutil.which("docker"):
        parser.error("docker was not found")
    commands = {
        "survey": ["docker", "system", "df", "-v"],
        "images": ["docker", "image", "prune", "-f"],
        "containers": ["docker", "container", "prune", "-f"],
        "volumes": ["docker", "volume", "prune", "-f"],
        "builder": ["docker", "builder", "prune", "-f"],
    }
    if args.action != "survey" and not args.apply:
        print(json.dumps({"action": args.action, "would_run": commands[args.action], "applied": False}, indent=2))
        return 0
    result = subprocess.run(commands[args.action], capture_output=True, text=True, check=False)
    print(json.dumps({"action": args.action, "command": commands[args.action], "returncode": result.returncode, "stdout": result.stdout, "stderr": result.stderr}, indent=2))
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
