#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Scaffold a small library-first FastMCP 3 project."""

from __future__ import annotations

import argparse
import re
import stat
from pathlib import Path

NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def write(path: Path, value: str, executable: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")
    if executable:
        path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("name")
    parser.add_argument("--target-dir", default=".")
    args = parser.parse_args()
    if not NAME.fullmatch(args.name):
        parser.error("name must use lowercase kebab-case")
    root = Path(args.target_dir).expanduser().resolve() / args.name
    if root.exists():
        parser.error(f"target already exists: {root}")
    package = args.name.replace("-", "_")
    write(root / "pyproject.toml", f'''[project]
name = "{args.name}"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = ["fastmcp>=3,<4"]

[project.optional-dependencies]
dev = ["pytest>=8", "pytest-asyncio>=0.24"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
''')
    write(root / "fastmcp.json", '''{
  "$schema": "https://gofastmcp.com/public/schemas/fastmcp.json/latest.json",
  "source": "server.py:mcp"
}
''')
    write(root / package / "__init__.py", "")
    write(root / package / "core.py", '''def greet(name: str) -> str:
    """Return a deterministic greeting."""
    cleaned = name.strip()
    if not cleaned:
        raise ValueError("name must not be empty")
    return f"Hello, {cleaned}!"
''')
    write(root / "server.py", f'''from fastmcp import FastMCP

from {package}.core import greet

mcp = FastMCP("{args.name}")
mcp.tool(greet)

if __name__ == "__main__":
    mcp.run()
''')
    write(root / "tests" / "test_server.py", f'''from fastmcp import Client

from {package}.core import greet
from server import mcp


def test_core():
    assert greet("Ada") == "Hello, Ada!"


async def test_protocol():
    async with Client(mcp) as client:
        result = await client.call_tool("greet", {{"name": "Ada"}})
        assert "Hello, Ada!" in str(result)
''')
    write(root / ".gitignore", ".venv/\n__pycache__/\n.pytest_cache/\n")
    print(root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
