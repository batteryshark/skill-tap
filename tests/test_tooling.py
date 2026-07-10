from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills" / "development"


def run_script(script: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *args],
        capture_output=True,
        text=True,
        check=False,
    )


class ToolingTests(unittest.TestCase):
    def test_every_entry_point_has_working_help(self) -> None:
        with tempfile.TemporaryDirectory() as cache:
            env = os.environ.copy()
            env["UV_CACHE_DIR"] = cache
            for skill in sorted(path for path in SKILLS.iterdir() if path.is_dir()):
                command = skill / "bin" / skill.name
                with self.subTest(command=command):
                    result = subprocess.run(
                        [str(command), "--help"],
                        capture_output=True,
                        text=True,
                        check=False,
                        env=env,
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertIn("usage:", result.stdout.lower())

    def test_architecture_map_emits_machine_readable_inventory(self) -> None:
        script = SKILLS / "architecture-for-comprehension" / "scripts" / "map_repository.py"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "pyproject.toml").write_text("[project]\nname='fixture'\n", encoding="utf-8")
            (root / "main.py").write_text("print('ok')\n", encoding="utf-8")
            result = run_script(script, str(root), "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["file_count"], 2)
        self.assertEqual(report["manifests"], ["pyproject.toml"])
        self.assertEqual(report["entrypoint_candidates"], ["main.py"])

    def test_hygiene_scanner_reports_candidates_and_can_fail(self) -> None:
        script = SKILLS / "deliverable-hygiene" / "scripts" / "scan_hygiene.py"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "handoff-notes.md"
            path.write_text("TODO: remove the temporary report\n", encoding="utf-8")
            result = run_script(script, str(path), "--fail-on-findings")
        self.assertEqual(result.returncode, 1)
        self.assertIn("scratch-name", result.stdout)
        self.assertIn("debt-marker", result.stdout)

    def test_publish_scanner_redacts_suspected_secret_values(self) -> None:
        script = SKILLS / "publish-ready" / "scripts" / "recon.py"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "config.py").write_text('api_key = "supersecretvalue"\n', encoding="utf-8")
            result = run_script(script, str(root))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("supersecretvalue", result.stdout)
        self.assertIn("suspected secret value (redacted)", result.stdout)

    def test_work_product_scanner_rejects_missing_paths(self) -> None:
        script = SKILLS / "work-product-audit" / "scripts" / "audit_text.py"
        result = run_script(script, "/path/that/does/not/exist")
        self.assertEqual(result.returncode, 2)
        self.assertIn("path does not exist", result.stderr)

    def test_work_product_scanner_fail_mode(self) -> None:
        script = SKILLS / "work-product-audit" / "scripts" / "audit_text.py"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "README.md"
            path.write_text("The point is that this unlocks everything.\n", encoding="utf-8")
            result = run_script(script, str(path), "--fail-on-findings")
        self.assertEqual(result.returncode, 1)
        self.assertIn("meta-thesis", result.stdout)
        self.assertIn("ai-signpost", result.stdout)


if __name__ == "__main__":
    unittest.main()
