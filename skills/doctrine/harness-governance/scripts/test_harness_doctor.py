from __future__ import annotations

import datetime as dt
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from harness_doctor import HarnessDoctor, main, normalize_link_target


VALID_METADATA = """+++
schema_version = 1
session_date = 2026-08-20
title = "Sessão de teste"
model = "codex"
runtime = "windows-local"
skills_used = ["runtime/windows-local"]
skills_missed = []
skills_updated = []
facts_changed = []
open_loops = []
durable_candidates = []
supersedes = []
evidence = ["teste local"]
+++
"""


class HarnessFixture:
    def __init__(self, root: Path) -> None:
        self.root = root

    def write(self, relative: str, content: str = "") -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def make_clean(self) -> None:
        self.write("README.md", "[documento](docs/existing.md) [site](https://example.com) [seção](#top)\n")
        self.write("docs/existing.md", "# Documento\n")
        self.write("skills/family/INDEX.md", "- `./sample/SKILL.md`\n")
        self.write(
            "skills/family/sample/SKILL.md",
            "# Sample\n\n- `scripts/tool.py`\n- `references/guide.md`\n",
        )
        self.write("skills/family/sample/scripts/tool.py", "")
        self.write("skills/family/sample/references/guide.md", "# Guia\n")
        self.write("memory/2026-08-19-before-dream.md", "# Legada\n")
        self.write("memory/2026-08-20-session.md", VALID_METADATA + "\n# Memória\n")
        self.write(
            "memory/_dream-state.md",
            """# Dream State

## Último dream
- Data: `2026-08-20`
- Última memória absorvida: `memory/2026-08-19-before-dream.md`
""",
        )


class HarnessDoctorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.fixture = HarnessFixture(self.root)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def codes(self) -> list[str]:
        doctor = HarnessDoctor(self.root, today=dt.date(2026, 8, 20))
        return [finding.code for finding in doctor.run()]

    def test_clean_harness_has_no_findings(self) -> None:
        self.fixture.make_clean()
        self.assertEqual([], HarnessDoctor(self.root, today=dt.date(2026, 8, 20)).run())

    def test_broken_relative_markdown_link_is_reported_but_urls_and_anchors_are_not(self) -> None:
        self.fixture.make_clean()
        self.fixture.write(
            "links.md",
            """[quebrado](missing/file.md)
[web](https://example.com/missing)
[email](mailto:test@example.com)
[âncora](#local)
`[exemplo](also-missing.md)`
```
[exemplo](fenced-missing.md)
```
""",
        )
        findings = HarnessDoctor(self.root, today=dt.date(2026, 8, 20)).run()
        broken = [finding for finding in findings if finding.code == "broken_markdown_link"]
        self.assertEqual(1, len(broken))
        self.assertEqual("missing/file.md", broken[0].target)

    def test_reference_style_link_and_encoded_space_are_resolved(self) -> None:
        self.fixture.make_clean()
        self.fixture.write("docs/file name.md", "ok")
        self.fixture.write("docs/file (final).md", "ok")
        self.fixture.write(
            "reference.md",
            "[doc]: <docs/file%20name.md>\n[final](docs/file%20(final).md)\n",
        )
        self.assertNotIn("broken_markdown_link", self.codes())

    def test_unindexed_skill_and_skill_directory_without_skill_are_reported(self) -> None:
        self.fixture.make_clean()
        self.fixture.write("skills/family/unindexed/SKILL.md", "# Unindexed\n")
        self.fixture.write("skills/family/loose/readme.txt", "órfão")
        findings = HarnessDoctor(self.root, today=dt.date(2026, 8, 20)).run()
        self.assertIn("unindexed_skill", [finding.code for finding in findings])
        self.assertIn("skill_directory_without_skill", [finding.code for finding in findings])

    def test_unmentioned_skill_artifact_and_directory_are_reported(self) -> None:
        self.fixture.make_clean()
        self.fixture.write("skills/family/sample/assets/cover.png", "")
        findings = HarnessDoctor(self.root, today=dt.date(2026, 8, 20)).run()
        self.assertIn("orphan_skill_directory", [finding.code for finding in findings])
        self.assertIn("orphan_skill_artifact", [finding.code for finding in findings])

    def test_missing_and_incoherent_dream_state_are_reported(self) -> None:
        self.fixture.make_clean()
        self.fixture.write(
            "memory/_dream-state.md",
            """# Dream State
## Último dream
- Data: `2026-08-18`
- Última memória absorvida: `memory/2026-08-19-before-dream.md`
""",
        )
        findings = HarnessDoctor(self.root, today=dt.date(2026, 8, 20)).run()
        dream_findings = [finding for finding in findings if "dream_state" in finding.code]
        self.assertEqual(1, len(dream_findings))
        self.assertIn("posterior", dream_findings[0].message)

    def test_legacy_memory_is_allowed_and_invalid_toml_metadata_is_reported(self) -> None:
        self.fixture.make_clean()
        self.fixture.write(
            "memory/2026-08-20-invalid.md",
            VALID_METADATA.replace("skills_used = [\"runtime/windows-local\"]", "skills_used = \"runtime/windows-local\""),
        )
        findings = HarnessDoctor(self.root, today=dt.date(2026, 8, 20)).run()
        metadata_findings = [
            finding for finding in findings if finding.code == "invalid_memory_frontmatter"
        ]
        self.assertEqual(1, len(metadata_findings))
        self.assertIn("skills_used", metadata_findings[0].message)

    def test_frontmatter_date_must_match_filename(self) -> None:
        self.fixture.make_clean()
        self.fixture.write(
            "memory/2026-08-19-wrong-date.md",
            VALID_METADATA + "\n# Memória\n",
        )
        self.assertIn("incoherent_memory_frontmatter", self.codes())

    def test_frontmatter_in_archived_memory_is_validated(self) -> None:
        self.fixture.make_clean()
        self.fixture.write(
            "memory/2026-07/2026-07-31-invalid.md",
            VALID_METADATA.replace("session_date = 2026-08-20", 'session_date = "2026-07-31"'),
        )

        findings = HarnessDoctor(self.root, today=dt.date(2026, 8, 20)).run()

        self.assertTrue(
            any(
                finding.code == "invalid_memory_frontmatter"
                and finding.path == "memory/2026-07/2026-07-31-invalid.md"
                for finding in findings
            )
        )

    def test_frontmatter_v1_rejects_unknown_fields(self) -> None:
        self.fixture.make_clean()
        self.fixture.write(
            "memory/2026-08-20-unknown.md",
            VALID_METADATA.replace("evidence =", "unexpected = []\nevidence ="),
        )
        findings = HarnessDoctor(self.root, today=dt.date(2026, 8, 20)).run()
        metadata_findings = [
            finding for finding in findings if finding.code == "invalid_memory_frontmatter"
        ]
        self.assertEqual(1, len(metadata_findings))
        self.assertIn("unknown fields", metadata_findings[0].message)

    def test_json_cli_is_machine_readable_and_returns_one_on_findings(self) -> None:
        self.fixture.make_clean()
        self.fixture.write("README.md", "[quebrado](missing.md)\n")
        output = io.StringIO()
        with redirect_stdout(output):
            exit_code = main(["--root", str(self.root), "--json"])
        payload = json.loads(output.getvalue())
        self.assertEqual(1, exit_code)
        self.assertFalse(payload["clean"])
        self.assertEqual(payload["finding_count"], len(payload["findings"]))

    def test_target_normalization_ignores_non_relative_targets(self) -> None:
        self.assertIsNone(normalize_link_target("https://example.com/a"))
        self.assertIsNone(normalize_link_target("#section"))
        self.assertIsNone(normalize_link_target("C:\\absolute\\file.md"))
        self.assertEqual("docs/a b.md", normalize_link_target("<docs/a%20b.md>"))


if __name__ == "__main__":
    unittest.main()
