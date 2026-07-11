from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = ROOT / "skills"
DEVELOPMENT = SKILLS_ROOT / "development"
PRODUCTIVITY = SKILLS_ROOT / "productivity"
UTILITIES = SKILLS_ROOT / "utilities"


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
            skill_packages = sorted(
                skill_file.parent for skill_file in SKILLS_ROOT.rglob("SKILL.md")
            )
            for skill in skill_packages:
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
        script = DEVELOPMENT / "architecture-for-comprehension" / "scripts" / "map_repository.py"
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

    def test_code_quality_inventory_separates_tests(self) -> None:
        script = DEVELOPMENT / "code-quality-review" / "scripts" / "code_inventory.py"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "src").mkdir()
            (root / "tests").mkdir()
            (root / "src" / "app.py").write_text("def run():\n    return 1\n", encoding="utf-8")
            (root / "tests" / "test_app.py").write_text("def test_run():\n    assert True\n", encoding="utf-8")
            result = run_script(script, str(root), "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["source_files"], 2)
        self.assertEqual(report["test_files"], 1)
        self.assertEqual(report["languages"], {"Python": 2})

    def test_codebase_archeology_finds_exact_duplicates(self) -> None:
        script = DEVELOPMENT / "codebase-archeology" / "scripts" / "inventory.py"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "Cargo.toml").write_text("[package]\nname='fixture'\n", encoding="utf-8")
            (root / "one.txt").write_text("same artifact\n", encoding="utf-8")
            (root / "two.txt").write_text("same artifact\n", encoding="utf-8")
            result = run_script(script, str(root), "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["manifests"], ["Cargo.toml"])
        self.assertEqual(report["duplicate_groups"][0]["paths"], ["one.txt", "two.txt"])

    def test_codebase_writeup_profiles_domains_without_url_values(self) -> None:
        script = DEVELOPMENT / "codebase-writeup" / "scripts" / "repo_profile.py"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "package.json").write_text('{"name":"fixture"}\n', encoding="utf-8")
            (root / "index.ts").write_text(
                'const endpoint = "https://api.example.test/path?token=sensitive-value";\n',
                encoding="utf-8",
            )
            result = run_script(script, str(root), "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("sensitive-value", result.stdout)
        report = json.loads(result.stdout)
        self.assertEqual(report["external_domains"], {"api.example.test": 1})
        self.assertEqual(report["entrypoint_candidates"], ["index.ts"])

    def test_engineering_diagram_scaffold_writes_selected_view(self) -> None:
        script = DEVELOPMENT / "engineering-diagrams" / "scripts" / "scaffold_diagram.py"
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "request-flow.md"
            result = run_script(
                script,
                "sequence",
                "--title",
                "Request flow",
                "--output",
                str(output),
            )
            content = output.read_text(encoding="utf-8")
            second = run_script(
                script,
                "sequence",
                "--title",
                "Request flow",
                "--output",
                str(output),
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("# Request flow", content)
        self.assertIn("sequenceDiagram", content)
        self.assertEqual(second.returncode, 2)
        self.assertIn("refusing to overwrite", second.stderr)

    def test_github_publish_preflight_reports_secret_bearing_files(self) -> None:
        script = DEVELOPMENT / "github-publish" / "scripts" / "preflight.py"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text("# Fixture\n", encoding="utf-8")
            (root / "LICENSE").write_text("fixture\n", encoding="utf-8")
            (root / ".gitignore").write_text(".env\n", encoding="utf-8")
            (root / ".env").write_text("TOKEN=do-not-print\n", encoding="utf-8")
            result = run_script(script, str(root), "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("do-not-print", result.stdout)
        report = json.loads(result.stdout)
        self.assertTrue(report["readme"])
        self.assertTrue(report["license"])
        self.assertTrue(report["gitignore"])
        self.assertEqual(report["secret_bearing_files"], [".env"])

    def test_hygiene_scanner_reports_candidates_and_can_fail(self) -> None:
        script = DEVELOPMENT / "deliverable-hygiene" / "scripts" / "scan_hygiene.py"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "handoff-notes.md"
            path.write_text("TODO: remove the temporary report\n", encoding="utf-8")
            result = run_script(script, str(path), "--fail-on-findings")
        self.assertEqual(result.returncode, 1)
        self.assertIn("scratch-name", result.stdout)
        self.assertIn("debt-marker", result.stdout)

    def test_intellidiff_smart_comparison_and_duplicate_detection(self) -> None:
        script = UTILITIES / "intellidiff" / "scripts" / "intellidiff.py"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            left = root / "left.txt"
            right = root / "right.txt"
            copy = root / "copy.txt"
            left.write_bytes(b"Alpha  \r\n\r\nBeta\r\n")
            right.write_bytes(b"Alpha\nBeta\n")
            copy.write_bytes(right.read_bytes())
            compared = run_script(
                script,
                "file",
                str(left),
                str(right),
                "--smart",
                "--ignore-newlines",
                "--ignore-whitespace",
                "--ignore-blank",
                "--json",
            )
            duplicates = run_script(script, "duplicates", str(root), "--json")
        self.assertEqual(compared.returncode, 0, compared.stderr)
        self.assertEqual(json.loads(compared.stdout)["result"], "identical-normalized")
        groups = json.loads(duplicates.stdout)["duplicate_groups"]
        self.assertEqual(groups[0]["paths"], ["copy.txt", "right.txt"])

    def test_project_tracker_scaffolds_compact_state(self) -> None:
        script = PRODUCTIVITY / "project-tracker" / "scripts" / "project_tracker.py"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            initialized = run_script(script, "init", str(root), "--title", "Fixture")
            session = run_script(
                script,
                "session",
                str(root),
                "--title",
                "First pass",
                "--timestamp",
                "2026-07-10-1200",
            )
            status = run_script(script, "status", str(root), "--json")
            tracker_text = (root / ".project" / "tracker.md").read_text(encoding="utf-8")
        self.assertEqual(initialized.returncode, 0, initialized.stderr)
        self.assertEqual(session.returncode, 0, session.stderr)
        self.assertIn("# Project Tracker: Fixture", tracker_text)
        report = json.loads(status.stdout)
        self.assertTrue(report["tracker_exists"])
        self.assertEqual(report["sessions"], 1)

    def test_decision_record_scaffold_preserves_lifecycle_fields(self) -> None:
        script = PRODUCTIVITY / "decision-records" / "scripts" / "scaffold_record.py"
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "queue.md"
            result = run_script(
                script,
                "--title",
                "Choose the job queue",
                "--status",
                "accepted",
                "--date",
                "2026-07-10",
                "--output",
                str(output),
            )
            content = output.read_text(encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("# Decision: Choose the job queue", content)
        self.assertIn("- Status: accepted", content)
        self.assertIn("## Reconsider when", content)

    def test_project_retrospective_collects_only_supported_sources(self) -> None:
        script = (
            PRODUCTIVITY
            / "project-retrospective"
            / "scripts"
            / "collect_sources.py"
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "notes.md").write_text("# Notes\n", encoding="utf-8")
            (root / "program.py").write_text("print('not a retro source')\n", encoding="utf-8")
            result = run_script(script, str(root), "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["files_found"], 1)
        self.assertTrue(report["files"][0]["path"].endswith("notes.md"))

    def test_publish_scanner_redacts_suspected_secret_values(self) -> None:
        script = DEVELOPMENT / "publish-ready" / "scripts" / "recon.py"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "config.py").write_text('api_key = "supersecretvalue"\n', encoding="utf-8")
            result = run_script(script, str(root))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("supersecretvalue", result.stdout)
        self.assertIn("suspected secret value (redacted)", result.stdout)

    def test_work_product_scanner_rejects_missing_paths(self) -> None:
        script = DEVELOPMENT / "work-product-audit" / "scripts" / "audit_text.py"
        result = run_script(script, "/path/that/does/not/exist")
        self.assertEqual(result.returncode, 2)
        self.assertIn("path does not exist", result.stderr)

    def test_work_product_scanner_fail_mode(self) -> None:
        script = DEVELOPMENT / "work-product-audit" / "scripts" / "audit_text.py"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "README.md"
            path.write_text("The point is that this unlocks everything.\n", encoding="utf-8")
            result = run_script(script, str(path), "--fail-on-findings")
        self.assertEqual(result.returncode, 1)
        self.assertIn("meta-thesis", result.stdout)
        self.assertIn("ai-signpost", result.stdout)


if __name__ == "__main__":
    unittest.main()
