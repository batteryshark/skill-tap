#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Build an agent handoff brief from a Claude Code JSONL transcript.

The JSONL export mixes human prompts, assistant text, tool calls, and tool
results. This script keeps the human and assistant narrative, extracts edits
and validation commands, and emits a Markdown brief that is concise enough to
use in a new agent session.
"""

from __future__ import annotations

import argparse
import collections
import dataclasses
import json
import os
import re
import sys
from pathlib import Path
from typing import Any


ANSI_RE = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")
SYSTEM_REMINDER_RE = re.compile(r"<system-reminder>.*?</system-reminder>\s*", re.DOTALL)
LOCAL_COMMAND_CAVEAT_RE = re.compile(r"<local-command-caveat>.*?</local-command-caveat>\s*", re.DOTALL)
LOCAL_COMMAND_TAG_RE = re.compile(r"<command-name>|<local-command-stdout>|<command-message>|<command-args>")
TOKEN_URL_RE = re.compile(r"(?i)([?&]token=)[^)\s&]+")
ORG_ID_RE = re.compile(r"(?i)(organization id\s*:\s*)[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
SECRET_ASSIGN_RE = re.compile(
    r"(?i)\b(api[_ -]?key|access[_ -]?token|refresh[_ -]?token|session[_ -]?token|"
    r"authorization|password|secret)\b\s*[:=]\s*([\"']?)[^\s,;\"']+\2"
)

EDIT_TOOLS = {"Edit", "MultiEdit", "Write", "NotebookEdit"}
COMMAND_TOOLS = {"Bash", "PowerShell"}
SEARCH_READ_TOOLS = {"Read", "Grep", "Glob", "LS"}
TASK_TOOLS = {"TaskCreate", "TaskUpdate"}

NOTE_KEYWORDS = (
    "handoff",
    "current state",
    "verified",
    "definitively",
    "fixed",
    "root cause",
    "resolved",
    "works",
    "working",
    "crash",
    "error",
    "next",
    "remaining",
    "todo",
    "need",
    "should",
    "important",
    "nuance",
)


@dataclasses.dataclass
class PromptEvent:
    line: int
    timestamp: str
    text: str


@dataclasses.dataclass
class AssistantNote:
    line: int
    timestamp: str
    text: str


@dataclasses.dataclass
class ToolEvent:
    line: int
    timestamp: str
    name: str
    tool_id: str
    input_summary: str
    cwd: str
    user_context: str
    assistant_context: str
    result_summary: str = ""


@dataclasses.dataclass
class FileChangeEvent:
    line: int
    timestamp: str
    op: str
    tool: str
    summary: str
    user_context: str
    assistant_context: str


def configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


def clean_text(text: Any) -> str:
    if text is None:
        return ""
    value = str(text)
    value = ANSI_RE.sub("", value)
    value = SYSTEM_REMINDER_RE.sub("", value)
    value = LOCAL_COMMAND_CAVEAT_RE.sub("", value)
    value = value.replace("\r\n", "\n").replace("\r", "\n")
    return value.strip()


def redact_text(text: str, enabled: bool) -> str:
    if not enabled:
        return text
    text = TOKEN_URL_RE.sub(r"\1<redacted>", text)
    text = ORG_ID_RE.sub(r"\1<redacted>", text)
    text = EMAIL_RE.sub("<email>", text)
    text = SECRET_ASSIGN_RE.sub(lambda m: f"{m.group(1)}=<redacted>", text)
    return text


def one_line(text: Any, limit: int = 300, redact: bool = True) -> str:
    value = redact_text(clean_text(text), redact)
    value = re.sub(r"\s+", " ", value).strip()
    if len(value) <= limit:
        return value
    return value[: max(0, limit - 18)].rstrip() + " ... [truncated]"


def block_text(text: Any, limit: int = 1200, redact: bool = True) -> str:
    value = redact_text(clean_text(text), redact)
    if len(value) <= limit:
        return value
    return value[: max(0, limit - 42)].rstrip() + f"\n\n[truncated {len(value) - limit} chars]"


def json_preview(value: Any, limit: int = 500, redact: bool = True) -> str:
    try:
        rendered = json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)
    except TypeError:
        rendered = str(value)
    return one_line(rendered, limit=limit, redact=redact)


def relpath_text(value: Any, root: str) -> str:
    if not value:
        return ""
    text = str(value).strip().strip('"')
    root_text = str(root).strip().strip('"')
    text_path = Path(text).expanduser()
    root_path = Path(root_text).expanduser()
    if text_path.is_absolute() and root_path.is_absolute():
        try:
            return str(text_path.resolve(strict=False).relative_to(root_path.resolve(strict=False))).replace("\\", "/")
        except ValueError:
            pass
    text_norm = text.replace("/", "\\")
    root_norm = root_text.replace("/", "\\").rstrip("\\")
    if root_norm and text_norm.lower().startswith(root_norm.lower() + "\\"):
        return text_norm[len(root_norm) + 1 :].replace("\\", "/")
    return text.replace("\\", "/")


def as_timestamp(value: Any) -> str:
    if not value:
        return ""
    text = str(value)
    if "T" in text:
        return text.replace("T", " ").replace("Z", " UTC")
    return text


def first_line(value: Any, limit: int = 90, redact: bool = True) -> str:
    text = clean_text(value)
    if not text:
        return ""
    return one_line(text.splitlines()[0], limit=limit, redact=redact)


def content_text(content: Any, include_tool_results: bool, redact: bool) -> str:
    if isinstance(content, str):
        return redact_text(clean_text(content), redact)
    if not isinstance(content, list):
        return ""
    pieces: list[str] = []
    for item in content:
        if not isinstance(item, dict):
            continue
        item_type = item.get("type")
        if item_type == "text":
            pieces.append(redact_text(clean_text(item.get("text", "")), redact))
        elif item_type == "tool_result" and include_tool_results:
            pieces.append(redact_text(clean_text(item.get("content", "")), redact))
    return "\n\n".join(piece for piece in pieces if piece)


def is_local_command_text(text: str) -> bool:
    return bool(LOCAL_COMMAND_TAG_RE.search(text)) or text.startswith("<local-command")


def should_keep_assistant_note(text: str) -> bool:
    lower = text.lower()
    return len(text) >= 120 or any(keyword in lower for keyword in NOTE_KEYWORDS)


def is_noisy_assistant_text(text: str) -> bool:
    lower = text.lower().strip()
    return lower.startswith("api error:") or "please double press esc" in lower


def tool_input_summary(name: str, input_value: Any, root: str, redact: bool) -> str:
    if not isinstance(input_value, dict):
        return json_preview(input_value, redact=redact)

    if name in COMMAND_TOOLS:
        return one_line(input_value.get("command") or input_value.get("script") or input_value, 900, redact=redact)

    if name in EDIT_TOOLS:
        file_path = relpath_text(input_value.get("file_path") or input_value.get("path") or input_value.get("notebook_path"), root)
        if name == "Write":
            content = input_value.get("content", "")
            line_count = len(clean_text(content).splitlines()) if content else 0
            return f"{file_path}: write {line_count} lines"
        if name == "MultiEdit":
            edits = input_value.get("edits") or []
            return f"{file_path}: {len(edits)} edits"
        old = first_line(input_value.get("old_string", ""), redact=redact)
        new = first_line(input_value.get("new_string", ""), redact=redact)
        if old or new:
            return f"{file_path}: replace `{old}` -> `{new}`"
        return file_path or json_preview(input_value, redact=redact)

    if name in SEARCH_READ_TOOLS:
        bits = []
        for key in ("file_path", "path", "pattern", "glob", "query"):
            if input_value.get(key):
                value = input_value[key]
                if key in {"file_path", "path"}:
                    value = relpath_text(value, root)
                bits.append(f"{key}={value}")
        return one_line(", ".join(bits) or input_value, 500, redact=redact)

    if name in TASK_TOOLS:
        return json_preview(input_value, limit=900, redact=redact)

    return json_preview(input_value, limit=650, redact=redact)


def summarize_result(result_value: Any, fallback_content: Any, root: str, redact: bool) -> str:
    if isinstance(result_value, dict):
        parts: list[str] = []
        for key in ("type", "filePath", "numLines", "startLine", "totalLines", "durationMs", "interrupted", "exitCode", "returnCode"):
            if key not in result_value:
                continue
            value = result_value[key]
            if key == "filePath":
                value = relpath_text(value, root)
            parts.append(f"{key}={value}")
        for key in ("stdout", "stderr", "result", "content", "message"):
            value = result_value.get(key)
            if value:
                if key == "content" and result_value.get("filePath") and isinstance(value, str):
                    parts.append(f"content={len(value.splitlines())} lines/{len(value)} chars")
                else:
                    parts.append(f"{key}: {one_line(value, limit=500, redact=redact)}")
        if parts:
            return "; ".join(parts)
        return json_preview(result_value, limit=700, redact=redact)
    if result_value:
        return one_line(result_value, limit=800, redact=redact)
    return one_line(fallback_content, limit=800, redact=redact)


def file_paths_from_edit(name: str, input_value: Any) -> list[str]:
    if not isinstance(input_value, dict):
        return []
    keys = ("file_path", "path", "notebook_path")
    paths = [str(input_value[key]) for key in keys if input_value.get(key)]
    if name == "MultiEdit" and input_value.get("file_path"):
        return [str(input_value["file_path"])]
    return paths


def result_file_path(result_value: Any) -> str:
    if isinstance(result_value, dict):
        return str(result_value.get("filePath") or result_value.get("path") or "")
    return ""


def record_change(
    changed_files: dict[str, list[FileChangeEvent]],
    path_value: str,
    root: str,
    line: int,
    timestamp: str,
    op: str,
    tool: str,
    summary: str,
    user_context: str,
    assistant_context: str,
) -> None:
    if not path_value:
        return
    path = relpath_text(path_value, root)
    changed_files[path].append(
        FileChangeEvent(
            line=line,
            timestamp=timestamp,
            op=op or tool,
            tool=tool,
            summary=summary,
            user_context=user_context,
            assistant_context=assistant_context,
        )
    )


def parse_jsonl(path: Path, root: str, include_tool_results: bool, redact: bool) -> dict[str, Any]:
    counts: collections.Counter[str] = collections.Counter()
    tool_counts: collections.Counter[str] = collections.Counter()
    model_counts: collections.Counter[str] = collections.Counter()
    cwds: collections.Counter[str] = collections.Counter()
    versions: collections.Counter[str] = collections.Counter()
    parse_errors: list[str] = []
    timestamps: list[str] = []

    human_prompts: list[PromptEvent] = []
    local_commands: list[PromptEvent] = []
    assistant_notes: list[AssistantNote] = []
    all_assistant_texts: list[AssistantNote] = []
    tool_events: list[ToolEvent] = []
    command_events: list[ToolEvent] = []
    task_events: list[ToolEvent] = []
    mcp_events: list[ToolEvent] = []
    changed_files: dict[str, list[FileChangeEvent]] = collections.defaultdict(list)
    tool_by_id: dict[str, ToolEvent] = {}

    current_user_context = ""
    last_assistant_context = ""
    seen_assistant_texts: set[tuple[str, str]] = set()
    session_ids: collections.Counter[str] = collections.Counter()

    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                parse_errors.append(f"line {line_number}: {exc}")
                continue

            record_type = str(record.get("type") or "")
            counts[record_type] += 1

            timestamp = str(record.get("timestamp") or "")
            if timestamp:
                timestamps.append(timestamp)
            if record.get("cwd"):
                cwds[relpath_text(record["cwd"], root)] += 1
            if record.get("version"):
                versions[str(record["version"])] += 1
            if record.get("sessionId"):
                session_ids[str(record["sessionId"])] += 1

            message = record.get("message") or {}
            if isinstance(message, dict) and message.get("model"):
                model_counts[str(message["model"])] += 1

            content = message.get("content") if isinstance(message, dict) else None

            if record_type == "user":
                if isinstance(content, str):
                    text = content_text(content, include_tool_results=False, redact=redact)
                    if not text:
                        continue
                    event = PromptEvent(line_number, timestamp, text)
                    if is_local_command_text(text):
                        local_commands.append(event)
                    else:
                        human_prompts.append(event)
                        current_user_context = one_line(text, limit=650, redact=redact)
                    continue

                if isinstance(content, list):
                    fallback_content = ""
                    for item in content:
                        if not isinstance(item, dict) or item.get("type") != "tool_result":
                            continue
                        tool_use_id = str(item.get("tool_use_id") or "")
                        result_value = record.get("toolUseResult")
                        summary = summarize_result(result_value, item.get("content", ""), root, redact=redact)
                        event = tool_by_id.get(tool_use_id)
                        if event:
                            event.result_summary = summary
                            file_path = result_file_path(result_value)
                            if file_path:
                                op = ""
                                if isinstance(result_value, dict):
                                    op = str(result_value.get("type") or "")
                                record_change(
                                    changed_files,
                                    file_path,
                                    root,
                                    line_number,
                                    timestamp,
                                    op,
                                    event.name,
                                    summary,
                                    event.user_context,
                                    event.assistant_context,
                                )
                        elif include_tool_results:
                            fallback_content = one_line(item.get("content", ""), limit=800, redact=redact)
                    if include_tool_results and fallback_content:
                        local_commands.append(PromptEvent(line_number, timestamp, fallback_content))
                continue

            if record_type != "assistant" or not isinstance(content, list):
                continue

            for item in content:
                if not isinstance(item, dict):
                    continue
                item_type = item.get("type")
                if item_type == "text":
                    text = content_text([item], include_tool_results=False, redact=redact)
                    if not text:
                        continue
                    if is_noisy_assistant_text(text):
                        continue
                    dedupe_key = (str(message.get("id") or record.get("uuid") or line_number), text)
                    if dedupe_key in seen_assistant_texts:
                        continue
                    seen_assistant_texts.add(dedupe_key)
                    note = AssistantNote(line_number, timestamp, text)
                    all_assistant_texts.append(note)
                    last_assistant_context = one_line(text, limit=650, redact=redact)
                    if should_keep_assistant_note(text):
                        assistant_notes.append(note)
                elif item_type == "tool_use":
                    name = str(item.get("name") or "")
                    tool_id = str(item.get("id") or "")
                    input_value = item.get("input")
                    tool_counts[name] += 1
                    cwd = relpath_text(record.get("cwd") or "", root)
                    event = ToolEvent(
                        line=line_number,
                        timestamp=timestamp,
                        name=name,
                        tool_id=tool_id,
                        input_summary=tool_input_summary(name, input_value, root, redact=redact),
                        cwd=cwd,
                        user_context=current_user_context,
                        assistant_context=last_assistant_context,
                    )
                    tool_events.append(event)
                    if tool_id:
                        tool_by_id[tool_id] = event
                    if name in COMMAND_TOOLS:
                        command_events.append(event)
                    if name in TASK_TOOLS:
                        task_events.append(event)
                    if name.startswith("mcp__"):
                        mcp_events.append(event)
                    if name in EDIT_TOOLS:
                        for file_path in file_paths_from_edit(name, input_value):
                            record_change(
                                changed_files,
                                file_path,
                                root,
                                line_number,
                                timestamp,
                                name,
                                name,
                                event.input_summary,
                                event.user_context,
                                event.assistant_context,
                            )

    return {
        "path": path,
        "root": root,
        "counts": counts,
        "tool_counts": tool_counts,
        "model_counts": model_counts,
        "cwds": cwds,
        "versions": versions,
        "parse_errors": parse_errors,
        "timestamps": timestamps,
        "session_ids": session_ids,
        "human_prompts": human_prompts,
        "local_commands": local_commands,
        "assistant_notes": assistant_notes,
        "all_assistant_texts": all_assistant_texts,
        "tool_events": tool_events,
        "command_events": command_events,
        "task_events": task_events,
        "mcp_events": mcp_events,
        "changed_files": changed_files,
    }


def append_counter(lines: list[str], title: str, counter: collections.Counter[str], limit: int = 20) -> None:
    lines.append(f"## {title}")
    if not counter:
        lines.append("- None found.")
        lines.append("")
        return
    for key, count in counter.most_common(limit):
        label = key if key else "<blank>"
        lines.append(f"- `{label}`: {count}")
    lines.append("")


def append_prompt_list(lines: list[str], title: str, events: list[PromptEvent], max_items: int, text_limit: int, redact: bool) -> None:
    lines.append(f"## {title}")
    if not events:
        lines.append("- None found.")
        lines.append("")
        return
    for event in events[:max_items]:
        lines.append(f"- {as_timestamp(event.timestamp)} L{event.line}: {one_line(event.text, limit=text_limit, redact=redact)}")
    if len(events) > max_items:
        lines.append(f"- ... {len(events) - max_items} more omitted by --max-prompts")
    lines.append("")


def append_assistant_notes(lines: list[str], notes: list[AssistantNote], max_items: int, text_limit: int, redact: bool) -> None:
    lines.append("## High-Signal Assistant Notes")
    if not notes:
        lines.append("- None found.")
        lines.append("")
        return

    if len(notes) > max_items:
        head_count = max(1, max_items // 4)
        tail_count = max_items - head_count
        selected = notes[:head_count] + notes[-tail_count:]
        omitted_after_line = notes[head_count - 1].line
        skipped_middle = len(notes) - len(selected)
    else:
        selected = notes[:]
        omitted_after_line = -1
        skipped_middle = 0

    omitted_written = False
    for note in selected:
        if skipped_middle > 0 and not omitted_written and note.line > omitted_after_line:
            lines.append(f"- ... {skipped_middle} middle notes omitted by --max-notes")
            omitted_written = True
        lines.append(f"- {as_timestamp(note.timestamp)} L{note.line}: {one_line(note.text, limit=text_limit, redact=redact)}")
    lines.append("")


def append_changed_files(lines: list[str], changed_files: dict[str, list[FileChangeEvent]], max_events_per_file: int, redact: bool) -> None:
    lines.append("## Changed Files")
    if not changed_files:
        lines.append("- None found.")
        lines.append("")
        return

    def sort_key(item: tuple[str, list[FileChangeEvent]]) -> tuple[str, str]:
        path, events = item
        last = events[-1].timestamp if events else ""
        return (last, path)

    for path, events in sorted(changed_files.items(), key=sort_key):
        ops = collections.Counter(event.op or event.tool for event in events)
        op_text = ", ".join(f"{op}:{count}" for op, count in ops.most_common())
        first_ts = as_timestamp(events[0].timestamp)
        last_ts = as_timestamp(events[-1].timestamp)
        lines.append(f"- `{path}` - {len(events)} event(s), {op_text}; {first_ts} -> {last_ts}")

        contexts: list[str] = []
        for event in events:
            for context in (event.user_context, event.assistant_context):
                if context and context not in contexts:
                    contexts.append(context)
        for context in contexts[:2]:
            lines.append(f"  - Why/context: {one_line(context, limit=260, redact=redact)}")

        shown_events = events[-max_events_per_file:]
        if len(events) > len(shown_events):
            lines.append(f"  - ... {len(events) - len(shown_events)} earlier event(s) omitted")
        for event in shown_events:
            lines.append(
                f"  - {as_timestamp(event.timestamp)} L{event.line} `{event.tool}`: "
                f"{one_line(event.summary, limit=360, redact=redact)}"
            )
    lines.append("")


def append_commands(lines: list[str], commands: list[ToolEvent], max_items: int, text_limit: int, redact: bool) -> None:
    lines.append("## Commands And Validation")
    if not commands:
        lines.append("- None found.")
        lines.append("")
        return
    for event in commands[:max_items]:
        lines.append(f"- {as_timestamp(event.timestamp)} L{event.line} `{event.name}`: {one_line(event.input_summary, limit=text_limit, redact=redact)}")
        if event.result_summary:
            lines.append(f"  - Result: {one_line(event.result_summary, limit=text_limit, redact=redact)}")
    if len(commands) > max_items:
        lines.append(f"- ... {len(commands) - max_items} more omitted by --max-commands")
    lines.append("")


def append_mcp(lines: list[str], mcp_events: list[ToolEvent], max_items: int, text_limit: int, redact: bool) -> None:
    lines.append("## Reverse-Engineering Tool Evidence")
    if not mcp_events:
        lines.append("- None found.")
        lines.append("")
        return
    counts = collections.Counter(event.name for event in mcp_events)
    lines.append("- Tool calls: " + ", ".join(f"`{name}` x{count}" for name, count in counts.most_common(12)))
    for event in mcp_events[:max_items]:
        lines.append(f"- {as_timestamp(event.timestamp)} L{event.line} `{event.name}`: {one_line(event.input_summary, limit=text_limit, redact=redact)}")
        if event.result_summary:
            lines.append(f"  - Result: {one_line(event.result_summary, limit=text_limit, redact=redact)}")
    if len(mcp_events) > max_items:
        lines.append(f"- ... {len(mcp_events) - max_items} more omitted by --max-mcp")
    lines.append("")


def append_current_state(lines: list[str], session: dict[str, Any], max_items: int, text_limit: int, redact: bool) -> None:
    lines.append("## Current State And Next Signals")
    candidates: list[tuple[int, str, str, str]] = []
    for prompt in session["human_prompts"][-20:]:
        text = prompt.text
        if any(keyword in text.lower() for keyword in NOTE_KEYWORDS):
            candidates.append((prompt.line, prompt.timestamp, "User", text))
    for note in session["all_assistant_texts"][-35:]:
        text = note.text
        if any(keyword in text.lower() for keyword in NOTE_KEYWORDS):
            candidates.append((note.line, note.timestamp, "Assistant", text))

    if not candidates:
        lines.append("- None found.")
        lines.append("")
        return

    candidates.sort(key=lambda item: item[0])
    selected = candidates[-max_items:]
    for line_number, timestamp, source, text in selected:
        lines.append(f"- {as_timestamp(timestamp)} L{line_number} {source}: {one_line(text, limit=text_limit, redact=redact)}")
    lines.append("")


def append_tasks(lines: list[str], tasks: list[ToolEvent], max_items: int, text_limit: int, redact: bool) -> None:
    lines.append("## Task List Events")
    if not tasks:
        lines.append("- None found.")
        lines.append("")
        return
    for event in tasks[:max_items]:
        lines.append(f"- {as_timestamp(event.timestamp)} L{event.line} `{event.name}`: {one_line(event.input_summary, limit=text_limit, redact=redact)}")
    if len(tasks) > max_items:
        lines.append(f"- ... {len(tasks) - max_items} more omitted by --max-tasks")
    lines.append("")


def render_markdown(session: dict[str, Any], args: argparse.Namespace) -> str:
    lines: list[str] = []
    timestamps = session["timestamps"]
    counts: collections.Counter[str] = session["counts"]

    lines.append("# Agent Session Handoff Brief")
    lines.append("")
    lines.append(f"- Source: `{relpath_text(session['path'], session['root'])}`")
    if session["session_ids"]:
        session_id = session["session_ids"].most_common(1)[0][0]
        visible_session_id = "<redacted>" if args.redact_session_ids else session_id
        lines.append(f"- Session ID: `{visible_session_id}`")
    if timestamps:
        lines.append(f"- Time range: {as_timestamp(timestamps[0])} -> {as_timestamp(timestamps[-1])}")
    lines.append(f"- JSONL records parsed: {sum(counts.values())}")
    lines.append(f"- Redaction: {'on' if args.redact else 'off'}")
    lines.append("")

    append_current_state(
        lines,
        session,
        max_items=args.max_state,
        text_limit=args.text_limit,
        redact=args.redact,
    )
    append_prompt_list(
        lines,
        "Human Objectives And Pivots",
        session["human_prompts"],
        max_items=args.max_prompts,
        text_limit=args.text_limit,
        redact=args.redact,
    )
    append_changed_files(
        lines,
        session["changed_files"],
        max_events_per_file=args.max_events_per_file,
        redact=args.redact,
    )
    append_assistant_notes(
        lines,
        session["assistant_notes"],
        max_items=args.max_notes,
        text_limit=args.text_limit,
        redact=args.redact,
    )
    append_commands(
        lines,
        session["command_events"],
        max_items=args.max_commands,
        text_limit=args.text_limit,
        redact=args.redact,
    )
    append_mcp(
        lines,
        session["mcp_events"],
        max_items=args.max_mcp,
        text_limit=args.text_limit,
        redact=args.redact,
    )
    append_tasks(
        lines,
        session["task_events"],
        max_items=args.max_tasks,
        text_limit=args.text_limit,
        redact=args.redact,
    )

    lines.append("## Appendix: Session Shape")
    lines.append("")
    append_counter(lines, "Record Counts", session["counts"], limit=20)
    append_counter(lines, "Tool Counts", session["tool_counts"], limit=30)
    append_counter(lines, "Models", session["model_counts"], limit=10)
    append_counter(lines, "Working Directories", session["cwds"], limit=12)

    if session["parse_errors"]:
        lines.append("## Parse Errors")
        for error in session["parse_errors"]:
            lines.append(f"- {error}")
        lines.append("")

    lines.append("## Re-run")
    command = ["claude-session-handoff", relpath_text(session["path"], session["root"])]
    if args.output:
        command.extend(["-o", relpath_text(args.output, session["root"])])
    if not args.redact:
        command.append("--no-redact")
    lines.append("```powershell")
    lines.append(" ".join(command))
    lines.append("```")
    lines.append("")
    return "\n".join(lines)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Parse a Claude Code JSONL transcript into an agent handoff brief.")
    parser.add_argument("jsonl", type=Path, help="Path to the Claude JSONL transcript.")
    parser.add_argument("-o", "--output", type=Path, help="Write Markdown to this path instead of stdout.")
    parser.add_argument("--root", default=os.getcwd(), help="Project root used to shorten absolute paths. Defaults to cwd.")
    parser.add_argument("--include-tool-results", action="store_true", help="Include otherwise skipped raw tool-result text.")
    parser.add_argument("--no-redact", dest="redact", action="store_false", help="Disable light redaction of tokens, emails, and org IDs.")
    parser.add_argument("--redact-session-ids", action="store_true", help="Also redact the session ID in the brief header.")
    parser.add_argument("--max-prompts", type=int, default=50, help="Maximum human prompts to show.")
    parser.add_argument("--max-notes", type=int, default=32, help="Maximum assistant notes to show.")
    parser.add_argument("--max-commands", type=int, default=45, help="Maximum Bash/PowerShell commands to show.")
    parser.add_argument("--max-mcp", type=int, default=25, help="Maximum MCP calls to show.")
    parser.add_argument("--max-tasks", type=int, default=24, help="Maximum task-list events to show.")
    parser.add_argument("--max-state", type=int, default=14, help="Maximum current-state/next-signal entries to show.")
    parser.add_argument("--max-events-per-file", type=int, default=4, help="Maximum recent change events shown per file.")
    parser.add_argument("--text-limit", type=int, default=420, help="Maximum characters per rendered list item.")
    parser.set_defaults(redact=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    configure_stdio()
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    jsonl_path = args.jsonl
    if not jsonl_path.exists():
        parser.error(f"JSONL path does not exist: {jsonl_path}")

    root = str(Path(args.root).resolve())
    session = parse_jsonl(jsonl_path, root=root, include_tool_results=args.include_tool_results, redact=args.redact)
    markdown = render_markdown(session, args)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(markdown, encoding="utf-8")
        print(f"Wrote {args.output}")
    else:
        print(markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
