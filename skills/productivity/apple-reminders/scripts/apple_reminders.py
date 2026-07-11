#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Apple Reminders CLI — manage macOS Reminders via EventKit.

Requires macOS with Xcode Command Line Tools (for first-time Swift compilation).
The Swift binary is auto-built on first use if not already compiled.

Usage:
    python3 apple_reminders.py <command> [options]

Commands:
    list-lists                     List all reminder lists
    list-reminders                 List reminders (with optional filters)
    create-reminder                Create a new reminder
    update-reminder <reminder-id>  Update an existing reminder
    delete-reminder <reminder-id>  Delete a reminder
    create-list                    Create a new reminder list
    update-list                    Rename a reminder list
    delete-list                    Delete a reminder list
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).parent.resolve()
SWIFT_DIR = SCRIPT_DIR / "swift"
BIN_DIR = SCRIPT_DIR / "bin"
BINARY_PATH = BIN_DIR / "EventKitCLI"
SOURCE_FILE = SWIFT_DIR / "EventKitCLI.swift"
INFO_PLIST = SWIFT_DIR / "Info.plist"


def build_binary():
    """Compile the Swift binary if it doesn't exist."""
    if BINARY_PATH.exists():
        return

    if sys.platform != "darwin":
        print("Error: This tool requires macOS.", file=sys.stderr)
        sys.exit(1)

    try:
        subprocess.run(["which", "swiftc"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print(
            "Error: Swift compiler (swiftc) not found.\n"
            "Install Xcode Command Line Tools: xcode-select --install",
            file=sys.stderr,
        )
        sys.exit(1)

    if not SOURCE_FILE.exists():
        print(f"Error: Swift source not found at {SOURCE_FILE}", file=sys.stderr)
        sys.exit(1)

    if not INFO_PLIST.exists():
        print(f"Error: Info.plist not found at {INFO_PLIST}", file=sys.stderr)
        sys.exit(1)

    BIN_DIR.mkdir(parents=True, exist_ok=True)

    print("Building EventKitCLI binary (first-time setup)...", file=sys.stderr)

    cmd = [
        "swiftc",
        "-o", str(BINARY_PATH),
        str(SOURCE_FILE),
        "-framework", "EventKit",
        "-framework", "Foundation",
        "-Xlinker", "-sectcreate",
        "-Xlinker", "__TEXT",
        "-Xlinker", "__info_plist",
        "-Xlinker", str(INFO_PLIST),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Build failed:\n{result.stderr}", file=sys.stderr)
        sys.exit(1)

    BINARY_PATH.chmod(0o755)
    print("Build complete.", file=sys.stderr)


def bootstrap_reminders_permission():
    """Ensure Reminders permission is granted by triggering a prompt via AppleScript."""
    try:
        # Check silently first to avoid spamming the console on every run
        result = subprocess.run([
            'osascript', '-e',
            'tell application "Reminders" to get the name of every list'
        ], capture_output=True, text=True, check=True, timeout=10)
        return True

    except subprocess.CalledProcessError as e:
        if "Not authorized" in str(e.stderr):
            print("❌ Reminders permission denied!", file=sys.stderr)
            print("💡 Please grant permission when prompted, or go to:", file=sys.stderr)
            print("   System Settings → Privacy & Security → Automation", file=sys.stderr)
            print("   Enable Reminders for your terminal/app", file=sys.stderr)
        else:
            print(f"⚠️  Permission check failed: {e.stderr}", file=sys.stderr)
        return False
    except subprocess.TimeoutExpired:
        print("⚠️  Permission check timed out - continuing anyway", file=sys.stderr)
        return True

def run_cli(args: list[str]) -> dict:
    """Execute the Swift CLI binary and return parsed JSON."""
    build_binary()
    bootstrap_reminders_permission()

    try:
        proc = subprocess.run(
            [str(BINARY_PATH)] + args,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except subprocess.TimeoutExpired:
        print("Error: Command timed out after 30 seconds.", file=sys.stderr)
        sys.exit(1)

    if proc.stdout:
        try:
            data = json.loads(proc.stdout)
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON from EventKitCLI:\n{proc.stdout}", file=sys.stderr)
            sys.exit(1)
    elif proc.stderr:
        print(f"Error: {proc.stderr.strip()}", file=sys.stderr)
        sys.exit(1)
    else:
        print("Error: No output from EventKitCLI.", file=sys.stderr)
        sys.exit(1)

    if data.get("status") == "error":
        print(f"Error: {data.get('message', 'Unknown error')}", file=sys.stderr)
        sys.exit(1)

    return data.get("result", data)


def format_markdown(data, command):
    """Format the JSON data into a readable Markdown string."""
    if not data and data != []:
        return "No data returned."

    if command == "list-lists":
        if not data:
            return "No reminder lists found."
        lines = ["# Reminder Lists\n"]
        for lst in data:
            lines.append(f"- **{lst.get('title', 'Unknown')}** (ID: `{lst.get('id')}`)")
        return "\n".join(lines)

    elif command == "list-reminders":
        reminders = data.get("reminders", [])
        if not reminders:
            return "No reminders found."

        lines = ["# Reminders\n"]
        from collections import defaultdict
        grouped = defaultdict(list)
        for rem in reminders:
            grouped[rem.get("list", "Unknown")].append(rem)

        for list_name, list_rems in grouped.items():
            lines.append(f"## {list_name}")
            for rem in list_rems:
                status = "[x]" if rem.get("isCompleted") else "[ ]"
                lines.append(f"- {status} **{rem.get('title', 'Untitled')}** (ID: `{rem.get('id')}`)")
                if rem.get("dueDate"):
                    lines.append(f"  - Due: {rem.get('dueDate')}")
                if rem.get("url"):
                    lines.append(f"  - URL: {rem.get('url')}")
                if rem.get("notes"):
                    notes = rem.get("notes").replace("\n", "\n    ")
                    lines.append(f"  - Notes: {notes}")
            lines.append("")
        return "\n".join(lines).strip()

    elif command in ("create-reminder", "update-reminder"):
        lines = [f"# Reminder: {data.get('title', 'Untitled')}"]
        lines.append(f"- **ID:** `{data.get('id')}`")
        status = "Completed" if data.get("isCompleted") else "Pending"
        lines.append(f"- **Status:** {status}")
        lines.append(f"- **List:** {data.get('list')}")
        if data.get("dueDate"):
            lines.append(f"- **Due:** {data.get('dueDate')}")
        if data.get("url"):
            lines.append(f"- **URL:** {data.get('url')}")
        if data.get("notes"):
            notes = data.get("notes").replace("\n", "\n  ")
            lines.append(f"- **Notes:** {notes}")
        return "\n".join(lines)

    elif command == "delete-reminder":
        return f"✅ Deleted reminder ID: `{data.get('id')}`"

    elif command in ("create-list", "update-list"):
        return f"✅ List '{data.get('title')}' saved with ID: `{data.get('id')}`"

    elif command == "delete-list":
        return f"✅ Deleted list '{data.get('title')}'"

    else:
        return json.dumps(data, indent=2, ensure_ascii=False)


def output(data, args, command):
    """Print output in either Markdown (default) or JSON."""
    if getattr(args, "json", False) or getattr(args, "pretty", False):
        indent = 2 if getattr(args, "pretty", False) else None
        print(json.dumps(data, indent=indent, ensure_ascii=False))
    else:
        print(format_markdown(data, command))


# --- Reminder Commands ---

def cmd_list_lists(args):
    result = run_cli(["--action", "read-lists"])
    output(result, args, "list-lists")


def cmd_list_reminders(args):
    cli_args = ["--action", "read"]
    if args.show_completed:
        cli_args.extend(["--showCompleted", "true"])
    if args.list:
        cli_args.extend(["--filterList", args.list])
    if args.search:
        cli_args.extend(["--search", args.search])
    if args.due_within:
        cli_args.extend(["--dueWithin", args.due_within])

    result = run_cli(cli_args)
    output(result, args, "list-reminders")


def cmd_create_reminder(args):
    cli_args = ["--action", "create", "--title", args.title]
    if args.list:
        cli_args.extend(["--targetList", args.list])
    if args.notes:
        cli_args.extend(["--note", args.notes])
    if args.url:
        cli_args.extend(["--url", args.url])
    if args.due_date:
        cli_args.extend(["--dueDate", args.due_date])

    result = run_cli(cli_args)
    output(result, args, "create-reminder")


def cmd_update_reminder(args):
    cli_args = ["--action", "update", "--id", args.reminder_id]
    if args.title:
        cli_args.extend(["--title", args.title])
    if args.list:
        cli_args.extend(["--targetList", args.list])
    if args.notes:
        cli_args.extend(["--note", args.notes])
    if args.url:
        cli_args.extend(["--url", args.url])
    if args.completed is not None:
        cli_args.extend(["--isCompleted", str(args.completed).lower()])
    if args.due_date:
        cli_args.extend(["--dueDate", args.due_date])

    result = run_cli(cli_args)
    output(result, args, "update-reminder")


def cmd_delete_reminder(args):
    result = run_cli(["--action", "delete", "--id", args.reminder_id])
    output(result, args, "delete-reminder")


def cmd_create_list(args):
    result = run_cli(["--action", "create-list", "--name", args.name])
    output(result, args, "create-list")


def cmd_update_list(args):
    result = run_cli(["--action", "update-list", "--name", args.name, "--newName", args.new_name])
    output(result, args, "update-list")


def cmd_delete_list(args):
    result = run_cli(["--action", "delete-list", "--name", args.name])
    output(result, args, "delete-list")


# --- Rebuild Command ---

def cmd_rebuild(args):
    """Force rebuild the Swift binary."""
    if BINARY_PATH.exists():
        BINARY_PATH.unlink()
    build_binary()
    print("Rebuild complete.", file=sys.stderr)


def main():
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--json", action="store_true", help="Output raw JSON")
    common.add_argument("--pretty", action="store_true", help="Pretty-print JSON output (implies --json)")

    parser = argparse.ArgumentParser(
        description="Apple Reminders CLI — manage macOS Reminders via EventKit.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- Reminder Lists ---

    sub = subparsers.add_parser("list-lists", parents=[common], help="List all reminder lists")
    sub.set_defaults(func=cmd_list_lists)

    sub = subparsers.add_parser("create-list", parents=[common], help="Create a new reminder list")
    sub.add_argument("--name", required=True, help="List name")
    sub.set_defaults(func=cmd_create_list)

    sub = subparsers.add_parser("update-list", parents=[common], help="Rename a reminder list")
    sub.add_argument("--name", required=True, help="Current list name")
    sub.add_argument("--new-name", required=True, help="New list name")
    sub.set_defaults(func=cmd_update_list)

    sub = subparsers.add_parser("delete-list", parents=[common], help="Delete a reminder list")
    sub.add_argument("--name", required=True, help="List name to delete")
    sub.set_defaults(func=cmd_delete_list)

    # --- Reminders ---

    sub = subparsers.add_parser("list-reminders", parents=[common], help="List reminders")
    sub.add_argument("--show-completed", action="store_true", help="Include completed reminders")
    sub.add_argument("--list", help="Filter: reminder list name")
    sub.add_argument("--search", help="Filter: search title/notes")
    sub.add_argument("--due-within", choices=["overdue", "today", "tomorrow", "this-week", "no-date"],
                     help="Filter: due date range")
    sub.set_defaults(func=cmd_list_reminders)

    sub = subparsers.add_parser("create-reminder", parents=[common], help="Create a new reminder")
    sub.add_argument("--title", required=True, help="Reminder title")
    sub.add_argument("--list", help="Target reminder list (default: system default)")
    sub.add_argument("--notes", help="Reminder notes")
    sub.add_argument("--url", help="Associated URL")
    sub.add_argument("--due-date", help="Due date (YYYY-MM-DD or ISO 8601)")
    sub.set_defaults(func=cmd_create_reminder)

    sub = subparsers.add_parser("update-reminder", parents=[common], help="Update an existing reminder")
    sub.add_argument("reminder_id", help="Reminder ID")
    sub.add_argument("--title", help="New title")
    sub.add_argument("--list", help="Move to different list")
    sub.add_argument("--notes", help="New notes")
    sub.add_argument("--url", help="New URL")
    completed_group = sub.add_mutually_exclusive_group()
    completed_group.add_argument("--completed", dest="completed", action="store_true", default=None, help="Mark completed")
    completed_group.add_argument("--not-completed", dest="completed", action="store_false", help="Mark not completed")
    sub.add_argument("--due-date", help="New due date")
    sub.set_defaults(func=cmd_update_reminder)

    sub = subparsers.add_parser("delete-reminder", parents=[common], help="Delete a reminder")
    sub.add_argument("reminder_id", help="Reminder ID")
    sub.set_defaults(func=cmd_delete_reminder)

    # --- Utility ---

    sub = subparsers.add_parser("rebuild", parents=[common], help="Force rebuild the Swift binary")
    sub.set_defaults(func=cmd_rebuild)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
