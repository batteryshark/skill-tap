# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

from __future__ import annotations

import argparse
import re
import subprocess
import sys

NAME_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{0,63}$")
FIELD_RE = re.compile(r"^[0-9*/?,\-]+$")
BEGIN = "# BEGIN cron-job-manager:"
END = "# END cron-job-manager:"


def validate(name: str, schedule: str, command: str) -> None:
    if not NAME_RE.fullmatch(name):
        raise ValueError("name must be 1-64 safe identifier characters")
    fields = schedule.split()
    if len(fields) != 5 or any(not FIELD_RE.fullmatch(field) for field in fields):
        raise ValueError("schedule must contain five cron fields")
    if not command.strip() or "\n" in command or "\r" in command:
        raise ValueError("command must be one non-empty line")


def block(name: str, schedule: str, command: str) -> str:
    validate(name, schedule, command)
    return f"{BEGIN}{name}\n{schedule} {command}\n{END}{name}\n"


def current() -> str:
    result = subprocess.run(["crontab", "-l"], text=True, capture_output=True)
    if result.returncode == 0:
        return result.stdout
    if "no crontab" in result.stderr.lower():
        return ""
    raise RuntimeError(result.stderr.strip() or "unable to read crontab")


def without_named(text: str, name: str) -> tuple[str, bool]:
    lines = text.splitlines()
    output: list[str] = []
    removed = False
    inside = False
    for line in lines:
        if line == f"{BEGIN}{name}":
            if inside:
                raise ValueError("nested managed marker")
            inside = True
            removed = True
            continue
        if line == f"{END}{name}":
            if not inside:
                raise ValueError("unmatched managed end marker")
            inside = False
            continue
        if not inside:
            output.append(line)
    if inside:
        raise ValueError("unterminated managed marker")
    rendered = "\n".join(output).rstrip()
    return (rendered + "\n" if rendered else ""), removed


def write(text: str) -> None:
    subprocess.run(["crontab", "-"], input=text, text=True, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Safely manage named user crontab blocks.")
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("list")
    for action in ("render", "install"):
        item = sub.add_parser(action)
        item.add_argument("--name", required=True)
        item.add_argument("--schedule", required=True)
        item.add_argument("--command", required=True)
        if action == "install":
            item.add_argument("--confirm", action="store_true")
    remove = sub.add_parser("remove")
    remove.add_argument("--name", required=True)
    remove.add_argument("--confirm", action="store_true")
    args = parser.parse_args()
    try:
        if args.action == "list":
            print(current(), end="")
            return 0
        if args.action == "render":
            print(block(args.name, args.schedule, args.command), end="")
            return 0
        if args.action == "install":
            proposed = block(args.name, args.schedule, args.command)
            if not args.confirm:
                print(proposed, end="")
                print("Refusing mutation without --confirm.", file=sys.stderr)
                return 2
            cleaned, _ = without_named(current(), args.name)
            write(cleaned + proposed)
            print(f"Installed cron job: {args.name}")
            return 0
        if not NAME_RE.fullmatch(args.name):
            raise ValueError("invalid name")
        cleaned, removed = without_named(current(), args.name)
        if not removed:
            print(f"No managed cron job named {args.name}.")
            return 0
        if not args.confirm:
            print("Refusing mutation without --confirm.", file=sys.stderr)
            return 2
        write(cleaned)
        print(f"Removed cron job: {args.name}")
        return 0
    except (OSError, subprocess.CalledProcessError, RuntimeError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

