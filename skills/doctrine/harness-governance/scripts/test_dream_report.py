from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest


MODULE_PATH = Path(__file__).with_name("dream_report.py")
SPEC = importlib.util.spec_from_file_location("dream_report", MODULE_PATH)
assert SPEC and SPEC.loader
dream_report = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = dream_report
SPEC.loader.exec_module(dream_report)


class DreamReportTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp_dir.name)
        self.memory = self.repo / "memory"
        self.memory.mkdir()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def write(self, relative: str, content: str) -> Path:
        path = self.repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def state(self, last_absorbed: Path, dream_date: str = "2026-08-17") -> None:
        self.write(
            "memory/_dream-state.md",
            "# Dream State\n\n## Último dream\n"
            f"- Data: `{dream_date}`\n"
            f"- Última memória absorvida: `{last_absorbed}`\n",
        )

    def test_frontmatter_v1_is_aggregated_and_checkpoint_is_incremental(self) -> None:
        absorbed = self.write("memory/2026-08-16-absorvida.md", "# Já absorvida\n")
        self.state(absorbed)
        self.write(
            "memory/2026-08-18-nova.md",
            """+++
schema_version = 1
session_date = 2026-08-18
title = "Sessão nova"
model = "GPT"
runtime = "Windows"
skills_used = ["skills/runtime/windows-local.md", "skills/engineering/backend.md"]
skills_missed = ["skills/engineering/backend.md"]
skills_updated = ["skills/runtime/windows-local.md"]
facts_changed = ["A porta mudou"]
open_loops = ["Validar o relay"]
durable_candidates = ["Registrar retomada"]
supersedes = ["memory/fato-antigo.md"]
evidence = ["log 42"]
+++
# Corpo
""",
        )

        report = dream_report.build_report(self.repo)

        self.assertEqual(1, report["harvest"]["count"])
        self.assertEqual("2026-08-18", report["harvest"]["first_date"])
        self.assertEqual(2, len(report["skills"]["used"]))
        self.assertEqual(1, report["skills"]["missed"][0]["count"])
        self.assertEqual("A porta mudou", report["facts_changed"][0]["value"])
        self.assertEqual("Validar o relay", report["open_loops"][0]["value"])
        self.assertEqual("Registrar retomada", report["durable_candidates"][0]["value"])
        self.assertEqual("memory/fato-antigo.md", report["supersessions"][0]["value"])
        self.assertEqual("log 42", report["evidence"][0]["value"])
        self.assertEqual([], report["memories_without_metadata"])

    def test_legacy_fallback_extracts_skills_and_marks_missing_metadata(self) -> None:
        absorbed = self.write("memory/2026-08-16-absorvida.md", "# Já absorvida\n")
        self.state(absorbed)
        self.write(
            "memory/2026-08-19-legada.md",
            """# Sessão legada

## 2. Skills acionadas

Consultadas:
- `AGENTS.md` (obrigatória)
- `skills/runtime/windows-local.md`
- **skills/infra/coolify-vps.md** — atualizada

## O que foi feito
- `isto-nao-e-skill.py`
""",
        )

        report = dream_report.build_report(self.repo)
        used = {row["skill"] for row in report["skills"]["used"]}

        self.assertEqual(
            {"AGENTS.md", "skills/runtime/windows-local.md", "skills/infra/coolify-vps.md"},
            used,
        )
        self.assertEqual(["2026-08-19-legada.md"], report["memories_without_metadata"])

    def test_missing_checkpoint_file_falls_back_after_its_filename_date(self) -> None:
        missing = self.memory / "2026-08-16-ausente.md"
        self.state(missing)
        self.write("memory/2026-08-15-antiga.md", "# Antiga\n")
        self.write("memory/2026-08-17-nova.md", "# Nova\n")

        report = dream_report.build_report(self.repo)

        self.assertEqual(["2026-08-17-nova.md"], [item["path"] for item in report["harvest"]["memories"]])
        self.assertTrue(any("arquivo ausente" in warning for warning in report["warnings"]))

    def test_invalid_metadata_is_reported_without_inventing_entries(self) -> None:
        absorbed = self.write("memory/2026-08-16-absorvida.md", "# Já absorvida\n")
        self.state(absorbed)
        self.write(
            "memory/2026-08-18-invalida.md",
            """+++
schema_version = 2
session_date = "ontem"
skills_used = "backend"
+++
# Inválida
""",
        )

        report = dream_report.build_report(self.repo)

        self.assertEqual([], report["skills"]["used"])
        self.assertGreaterEqual(len(report["warnings"]), 3)
        self.assertTrue(any("schema_version" in warning for warning in report["warnings"]))
        self.assertEqual(["2026-08-18-invalida.md"], report["memories_without_metadata"])

    def test_markdown_and_optional_json_are_emitted(self) -> None:
        absorbed = self.write("memory/2026-08-16-absorvida.md", "# Já absorvida\n")
        self.state(absorbed)
        self.write("memory/2026-08-18-legada.md", "# Nova\n\n## Skills acionadas\n- `skill-a`\n")
        markdown_path = self.repo / "out" / "report.md"
        json_path = self.repo / "out" / "report.json"

        result = dream_report.main(
            [
                "--repo-root",
                str(self.repo),
                "--output",
                str(markdown_path),
                "--json",
                str(json_path),
            ]
        )

        self.assertEqual(0, result)
        self.assertIn("# Relatório de evidências para o Dream", markdown_path.read_text(encoding="utf-8"))
        payload = json.loads(json_path.read_text(encoding="utf-8"))
        self.assertEqual(1, payload["harvest"]["count"])


if __name__ == "__main__":
    unittest.main()
