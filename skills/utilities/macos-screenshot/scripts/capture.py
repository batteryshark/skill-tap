# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

from __future__ import annotations

import argparse
import json
import platform
import shutil
import subprocess
import sys
from pathlib import Path

COMMAND = shutil.which("screencapture") or "/usr/sbin/screencapture"


def check() -> int:
    payload = {
        "platform": platform.system(),
        "supported": platform.system() == "Darwin" and Path(COMMAND).exists(),
        "command": COMMAND,
        "permission_note": "Screen recording permission is enforced by macOS at capture time.",
    }
    print(json.dumps(payload, indent=2))
    return 0 if payload["supported"] else 1


def parse_region(value: str) -> str:
    parts = value.split(",")
    if len(parts) != 4:
        raise argparse.ArgumentTypeError("region must be x,y,width,height")
    try:
        numbers = [int(part) for part in parts]
    except ValueError as error:
        raise argparse.ArgumentTypeError("region values must be integers") from error
    if numbers[2] <= 0 or numbers[3] <= 0:
        raise argparse.ArgumentTypeError("region width and height must be positive")
    return ",".join(str(number) for number in numbers)


def capture(args: argparse.Namespace) -> int:
    if platform.system() != "Darwin" or not Path(COMMAND).exists():
        print("Error: macOS screencapture is unavailable.", file=sys.stderr)
        return 1
    modes = sum(bool(value) for value in (args.interactive, args.window_id, args.region, args.display))
    if modes > 1:
        print("Error: choose only one of --interactive, --window-id, --region, or --display.", file=sys.stderr)
        return 1
    output = args.output.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    command = [COMMAND, "-x", "-t", "png"]
    if args.interactive:
        command.append("-i")
    elif args.window_id:
        command.extend(["-l", str(args.window_id)])
    elif args.region:
        command.extend(["-R", args.region])
    elif args.display:
        command.extend(["-D", str(args.display)])
    command.append(str(output))
    result = subprocess.run(command, text=True, capture_output=True)
    if result.returncode != 0:
        print(result.stderr.strip() or "Screenshot capture failed.", file=sys.stderr)
        return result.returncode
    if not output.exists():
        print("Capture was cancelled; no file was created.", file=sys.stderr)
        return 2
    print(json.dumps({"output": str(output), "bytes": output.stat().st_size}, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture screenshots with the native macOS tool.")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("check")
    cap = sub.add_parser("capture")
    cap.add_argument("--output", type=Path, required=True)
    cap.add_argument("--interactive", action="store_true")
    cap.add_argument("--window-id", type=int)
    cap.add_argument("--region", type=parse_region)
    cap.add_argument("--display", type=int)
    args = parser.parse_args()
    return check() if args.command == "check" else capture(args)


if __name__ == "__main__":
    raise SystemExit(main())

