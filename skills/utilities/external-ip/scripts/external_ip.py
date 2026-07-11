#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Resolve public IP observations from multiple HTTPS endpoints."""

from __future__ import annotations

import argparse
import ipaddress
import json
import urllib.error
import urllib.request

ENDPOINTS = ("https://api.ipify.org", "https://ifconfig.me/ip", "https://icanhazip.com")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout", type=float, default=5.0)
    args = parser.parse_args()
    observations = []
    for url in ENDPOINTS:
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "external-ip-skill/1"})
            with urllib.request.urlopen(request, timeout=args.timeout) as response:
                value = response.read(256).decode("ascii").strip()
            address = ipaddress.ip_address(value)
            observations.append({"service": url, "address": str(address), "family": address.version})
        except (OSError, ValueError, UnicodeError, urllib.error.URLError) as error:
            observations.append({"service": url, "error": str(error)})
    valid = [item for item in observations if "address" in item]
    print(json.dumps({"observations": observations, "consensus": len({item["address"] for item in valid}) == 1 if valid else False}, indent=2))
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
