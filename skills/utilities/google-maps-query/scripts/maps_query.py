# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

GEOCODE = "https://maps.googleapis.com/maps/api/geocode/json"
PLACES = "https://places.googleapis.com/v1"


def request_json(url: str, *, method: str = "GET", headers: dict[str, str] | None = None, body: dict | None = None) -> dict:
    data = json.dumps(body).encode() if body is not None else None
    merged = {"Accept": "application/json", **(headers or {})}
    if data is not None:
        merged["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=data, method=method, headers=merged)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", "replace")
        raise RuntimeError(f"HTTP {error.code}: {detail}") from error


def api_key() -> str:
    value = os.environ.get("GOOGLE_MAPS_API_KEY", "").strip()
    if not value:
        raise ValueError("GOOGLE_MAPS_API_KEY is not set")
    return value


def waypoint(value: str) -> dict:
    if value.startswith("place_id:"):
        return {"placeId": value.removeprefix("place_id:")}
    if value.startswith("address:"):
        return {"address": value.removeprefix("address:")}
    raise ValueError("route waypoint must start with place_id: or address:")


def run(args: argparse.Namespace) -> dict:
    key = api_key()
    if args.command == "geocode":
        query = urllib.parse.urlencode({"address": args.address, "key": key})
        return request_json(f"{GEOCODE}?{query}")
    if args.command == "reverse":
        if not -90 <= args.latitude <= 90 or not -180 <= args.longitude <= 180:
            raise ValueError("invalid latitude or longitude")
        query = urllib.parse.urlencode({"latlng": f"{args.latitude},{args.longitude}", "key": key})
        return request_json(f"{GEOCODE}?{query}")
    headers = {"X-Goog-Api-Key": key}
    if args.command == "search":
        headers["X-Goog-FieldMask"] = "places.id,places.displayName,places.formattedAddress,places.location,places.rating,places.googleMapsUri"
        return request_json(f"{PLACES}/places:searchText", method="POST", headers=headers, body={"textQuery": args.query, "maxResultCount": args.limit})
    if args.command == "place":
        headers["X-Goog-FieldMask"] = "id,displayName,formattedAddress,location,rating,websiteUri,nationalPhoneNumber,regularOpeningHours,googleMapsUri"
        return request_json(f"{PLACES}/places/{urllib.parse.quote(args.place_id, safe='')}", headers=headers)
    headers["X-Goog-FieldMask"] = "routes.distanceMeters,routes.duration,routes.description,routes.polyline.encodedPolyline"
    body = {
        "origin": waypoint(args.origin),
        "destination": waypoint(args.destination),
        "travelMode": args.mode,
        "computeAlternativeRoutes": False,
        "languageCode": "en-US",
        "units": "IMPERIAL",
    }
    return request_json("https://routes.googleapis.com/directions/v2:computeRoutes", method="POST", headers=headers, body=body)


def main() -> int:
    parser = argparse.ArgumentParser(description="Query Google Maps Platform APIs.")
    parser.add_argument("--execute", action="store_true", help="Acknowledge an external potentially billable API call.")
    sub = parser.add_subparsers(dest="command", required=True)
    geocode = sub.add_parser("geocode"); geocode.add_argument("address")
    reverse = sub.add_parser("reverse"); reverse.add_argument("latitude", type=float); reverse.add_argument("longitude", type=float)
    search = sub.add_parser("search"); search.add_argument("query"); search.add_argument("--limit", type=int, default=5, choices=range(1, 21))
    place = sub.add_parser("place"); place.add_argument("place_id")
    route = sub.add_parser("route"); route.add_argument("origin"); route.add_argument("destination"); route.add_argument("--mode", choices=("DRIVE", "BICYCLE", "WALK", "TRANSIT"), default="DRIVE")
    args = parser.parse_args()
    if not args.execute:
        print("Refusing external billable call without --execute.", file=sys.stderr)
        return 2
    try:
        print(json.dumps(run(args), indent=2, ensure_ascii=False))
        return 0
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
