from __future__ import annotations

import datetime as dt
from pathlib import Path
import tempfile
import unittest

from episodic_memory_metadata import (
    MetadataValidationError,
    parse_memory_file,
    parse_memory_text,
)


VALID_FRONTMATTER = """+++\n\
schema_version = 1\n\
session_date = 2026-08-20\n\
title = \"Upgrade do harness\"\n\
model = \"gpt-5\"\n\
runtime = \"windows-local\"\n\
skills_used = [\"skills/runtime/windows-local.md\"]\n\
skills_missed = []\n\
skills_updated = []\n\
facts_changed = [\"Metadados v1 foram definidos.\"]\n\
open_loops = []\n\
durable_candidates = [\"Medir ativação de skills.\"]\n\
supersedes = []\n\
evidence = [\"skills/doctrine/harness-governance/references/episodic-memory-metadata-v1.md\"]\n\
+++\n"""


class ParseMemoryTextTests(unittest.TestCase):
    def test_legacy_memory_remains_valid_and_distinguishable(self) -> None:
        prose = "# Sessão antiga\r\n\r\nProsa intacta.\r\n"

        parsed = parse_memory_text(prose)

        self.assertTrue(parsed.is_legacy)
        self.assertEqual(parsed.format, "legacy")
        self.assertIsNone(parsed.metadata)
        self.assertEqual(parsed.body, prose)

    def test_valid_v1_metadata_is_parsed_and_prose_is_preserved(self) -> None:
        prose = "\r\n# Memória\r\n\r\nA prosa permanece exatamente assim.\r\n"

        parsed = parse_memory_text(VALID_FRONTMATTER + prose)

        self.assertFalse(parsed.is_legacy)
        self.assertEqual(parsed.format, "v1")
        self.assertEqual(parsed.body, prose)
        self.assertEqual(parsed.metadata["schema_version"], 1)
        self.assertEqual(parsed.metadata["session_date"], dt.date(2026, 8, 20))

    def test_missing_required_field_is_rejected(self) -> None:
        text = VALID_FRONTMATTER.replace("open_loops = []\n", "")

        with self.assertRaisesRegex(MetadataValidationError, "open_loops"):
            parse_memory_text(text)

    def test_wrong_list_type_is_rejected(self) -> None:
        text = VALID_FRONTMATTER.replace(
            'skills_used = ["skills/runtime/windows-local.md"]',
            'skills_used = "skills/runtime/windows-local.md"',
        )

        with self.assertRaisesRegex(MetadataValidationError, "array of strings"):
            parse_memory_text(text)

    def test_unknown_field_is_rejected(self) -> None:
        text = VALID_FRONTMATTER.replace(
            "evidence = [", 'evidance = []\nevidence = ['
        )

        with self.assertRaisesRegex(MetadataValidationError, "unknown fields: evidance"):
            parse_memory_text(text)

    def test_quoted_session_date_is_rejected(self) -> None:
        text = VALID_FRONTMATTER.replace(
            "session_date = 2026-08-20", 'session_date = "2026-08-20"'
        )

        with self.assertRaisesRegex(MetadataValidationError, "local date"):
            parse_memory_text(text)

    def test_unsupported_schema_is_rejected(self) -> None:
        text = VALID_FRONTMATTER.replace("schema_version = 1", "schema_version = 2")

        with self.assertRaisesRegex(MetadataValidationError, "unsupported value"):
            parse_memory_text(text)

    def test_opening_delimiter_requires_closing_delimiter(self) -> None:
        with self.assertRaisesRegex(MetadataValidationError, "closing"):
            parse_memory_text("+++\nschema_version = 1\n")

    def test_utf8_bom_file_is_supported(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory, "memory.md")
            path.write_text(VALID_FRONTMATTER + "# Corpo\n", encoding="utf-8-sig")

            parsed = parse_memory_file(path)

        self.assertEqual(parsed.format, "v1")
        self.assertEqual(parsed.body, "# Corpo\n")


if __name__ == "__main__":
    unittest.main()
