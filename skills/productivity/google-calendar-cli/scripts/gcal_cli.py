# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "google-api-python-client>=2.187.0",
#   "google-auth>=2.45.0",
#   "google-auth-httplib2>=0.2.1",
#   "google-auth-oauthlib>=1.2.2",
# ]
# ///

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPE = ["https://www.googleapis.com/auth/calendar"]
CONFIG = Path.home() / ".config" / "google-calendar-cli"
CREDENTIALS = Path(os.environ.get("GCAL_CREDENTIALS", CONFIG / "credentials.json")).expanduser()
TOKEN = Path(os.environ.get("GCAL_TOKEN_FILE", CONFIG / "token.json")).expanduser()


def save_private(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    try:
        path.chmod(0o600)
    except OSError:
        pass


def credentials(interactive: bool = False) -> Credentials:
    creds = Credentials.from_authorized_user_file(TOKEN, SCOPE) if TOKEN.exists() else None
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        save_private(TOKEN, creds.to_json())
    if not creds or not creds.valid:
        if not interactive:
            raise ValueError("not authenticated; run auth")
        if not CREDENTIALS.exists():
            raise ValueError(f"OAuth desktop credentials not found: {CREDENTIALS}")
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS, SCOPE)
        creds = flow.run_local_server(port=0)
        save_private(TOKEN, creds.to_json())
    return creds


def service(interactive: bool = False):
    return build("calendar", "v3", credentials=credentials(interactive), cache_discovery=False)


def canonical(payload: dict) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def digest(payload: dict) -> str:
    return hashlib.sha256(canonical(payload)).hexdigest()


def write_plan(path: Path, payload: dict) -> None:
    document = {"confirmation_sha256": digest(payload), "plan": payload}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(document, indent=2, ensure_ascii=False))


def event_body(args: argparse.Namespace) -> dict:
    start_value = datetime.fromisoformat(args.start.replace("Z", "+00:00"))
    end_value = datetime.fromisoformat(args.end.replace("Z", "+00:00"))
    if start_value.tzinfo is None or end_value.tzinfo is None:
        raise ValueError("start and end must include a UTC offset or Z")
    if end_value <= start_value:
        raise ValueError("end must be after start")
    body = {
        "summary": args.summary,
        "start": {"dateTime": args.start},
        "end": {"dateTime": args.end},
    }
    if args.time_zone:
        body["start"]["timeZone"] = args.time_zone
        body["end"]["timeZone"] = args.time_zone
    if args.description:
        body["description"] = args.description
    if args.location:
        body["location"] = args.location
    if args.attendee:
        body["attendees"] = [{"email": value} for value in args.attendee]
    return body


def apply(path: Path, confirmation: str) -> dict:
    document = json.loads(path.read_text(encoding="utf-8"))
    payload = document.get("plan")
    expected = document.get("confirmation_sha256")
    if not isinstance(payload, dict) or expected != digest(payload):
        raise ValueError("plan content does not match its embedded hash")
    if confirmation != expected:
        raise ValueError("confirmation hash does not match the plan")
    api = service()
    operation = payload.get("operation")
    if operation == "create":
        result = api.events().insert(
            calendarId=payload["calendar_id"],
            body=payload["event"],
            sendUpdates=payload["send_updates"],
        ).execute()
        return {"operation": "create", "event_id": result.get("id"), "html_link": result.get("htmlLink"), "status": result.get("status")}
    if operation == "delete":
        api.events().delete(
            calendarId=payload["calendar_id"],
            eventId=payload["event_id"],
            sendUpdates=payload["send_updates"],
        ).execute()
        return {"operation": "delete", "event_id": payload["event_id"], "deleted": True}
    raise ValueError("unsupported plan operation")


def main() -> int:
    parser = argparse.ArgumentParser(description="Google Calendar CLI with hash-bound mutation plans.")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("auth")
    sub.add_parser("calendars")
    events = sub.add_parser("events")
    events.add_argument("--calendar", default="primary")
    events.add_argument("--start", required=True)
    events.add_argument("--end", required=True)
    events.add_argument("--limit", type=int, default=50)
    busy = sub.add_parser("freebusy")
    busy.add_argument("--calendar", action="append", required=True)
    busy.add_argument("--start", required=True)
    busy.add_argument("--end", required=True)
    create = sub.add_parser("plan-create")
    create.add_argument("--plan", type=Path, required=True)
    create.add_argument("--calendar", default="primary")
    create.add_argument("--summary", required=True)
    create.add_argument("--start", required=True)
    create.add_argument("--end", required=True)
    create.add_argument("--time-zone")
    create.add_argument("--description")
    create.add_argument("--location")
    create.add_argument("--attendee", action="append")
    create.add_argument("--notify-attendees", action="store_true")
    delete = sub.add_parser("plan-delete")
    delete.add_argument("--plan", type=Path, required=True)
    delete.add_argument("--calendar", default="primary")
    delete.add_argument("--event-id", required=True)
    delete.add_argument("--notify-attendees", action="store_true")
    execute = sub.add_parser("apply-plan")
    execute.add_argument("plan", type=Path)
    execute.add_argument("--confirm", required=True)
    args = parser.parse_args()
    try:
        if args.command == "auth":
            credentials(interactive=True)
            print(json.dumps({"authenticated": True, "token_file": str(TOKEN)}, indent=2))
        elif args.command == "calendars":
            result = service().calendarList().list(maxResults=250).execute()
            print(json.dumps(result.get("items", []), indent=2, ensure_ascii=False))
        elif args.command == "events":
            result = service().events().list(calendarId=args.calendar, timeMin=args.start, timeMax=args.end, singleEvents=True, orderBy="startTime", maxResults=args.limit).execute()
            print(json.dumps(result.get("items", []), indent=2, ensure_ascii=False))
        elif args.command == "freebusy":
            body = {"timeMin": args.start, "timeMax": args.end, "items": [{"id": item} for item in args.calendar]}
            print(json.dumps(service().freebusy().query(body=body).execute(), indent=2, ensure_ascii=False))
        elif args.command == "plan-create":
            payload = {"operation": "create", "calendar_id": args.calendar, "event": event_body(args), "send_updates": "all" if args.notify_attendees else "none"}
            write_plan(args.plan, payload)
        elif args.command == "plan-delete":
            payload = {"operation": "delete", "calendar_id": args.calendar, "event_id": args.event_id, "send_updates": "all" if args.notify_attendees else "none"}
            write_plan(args.plan, payload)
        else:
            print(json.dumps(apply(args.plan, args.confirm), indent=2, ensure_ascii=False))
        return 0
    except Exception as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
