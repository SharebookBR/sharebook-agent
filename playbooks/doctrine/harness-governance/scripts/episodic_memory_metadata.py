"""Parse and validate optional TOML metadata in episodic memories.

The metadata block is optional for backwards compatibility. A Markdown file
without an opening ``+++`` delimiter is classified as ``legacy`` and remains
valid. If the delimiter is present, the complete v1 contract is enforced.
"""

from __future__ import annotations

import argparse
import datetime as dt
from dataclasses import dataclass
from pathlib import Path
import sys
import tomllib
from typing import Any, Literal, Mapping, Sequence


SCHEMA_VERSION = 1

TEXT_FIELDS = ("title", "model", "runtime")
LIST_FIELDS = (
    "skills_used",
    "skills_missed",
    "skills_updated",
    "facts_changed",
    "open_loops",
    "durable_candidates",
    "supersedes",
    "evidence",
)
REQUIRED_FIELDS = (
    "schema_version",
    "session_date",
    *TEXT_FIELDS,
    *LIST_FIELDS,
)


class MetadataValidationError(ValueError):
    """Raised when a memory declares metadata that violates the v1 contract."""


@dataclass(frozen=True)
class ParsedMemory:
    """A parsed memory with its Markdown prose preserved byte-for-byte as text."""

    format: Literal["legacy", "v1"]
    body: str
    metadata: Mapping[str, Any] | None

    @property
    def is_legacy(self) -> bool:
        return self.format == "legacy"


def _is_delimiter(line: str, *, first_line: bool = False) -> bool:
    value = line.rstrip("\r\n")
    if first_line:
        value = value.removeprefix("\ufeff")
    return value == "+++"


def _validate_non_empty_text(field: str, value: Any) -> None:
    if not isinstance(value, str) or not value.strip():
        raise MetadataValidationError(f"{field}: expected a non-empty string")


def _validate_string_list(field: str, value: Any) -> None:
    if not isinstance(value, list):
        raise MetadataValidationError(f"{field}: expected an array of strings")
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            raise MetadataValidationError(
                f"{field}[{index}]: expected a non-empty string"
            )


def validate_v1(metadata: Mapping[str, Any]) -> None:
    """Validate parsed TOML metadata against the episodic-memory v1 contract."""

    missing = [field for field in REQUIRED_FIELDS if field not in metadata]
    if missing:
        raise MetadataValidationError(
            "missing required fields: " + ", ".join(missing)
        )

    unknown = sorted(set(metadata) - set(REQUIRED_FIELDS))
    if unknown:
        raise MetadataValidationError("unknown fields: " + ", ".join(unknown))

    version = metadata["schema_version"]
    if isinstance(version, bool) or not isinstance(version, int):
        raise MetadataValidationError("schema_version: expected integer 1")
    if version != SCHEMA_VERSION:
        raise MetadataValidationError(
            f"schema_version: unsupported value {version!r}; expected 1"
        )

    session_date = metadata["session_date"]
    if isinstance(session_date, dt.datetime) or not isinstance(session_date, dt.date):
        raise MetadataValidationError(
            "session_date: expected an unquoted TOML local date (YYYY-MM-DD)"
        )

    for field in TEXT_FIELDS:
        _validate_non_empty_text(field, metadata[field])
    for field in LIST_FIELDS:
        _validate_string_list(field, metadata[field])


def parse_memory_text(text: str) -> ParsedMemory:
    """Parse one memory, preserving legacy files and Markdown prose.

    No frontmatter means ``legacy``. An opening delimiter commits the document
    to the v1 schema: malformed TOML, a missing closing delimiter, or invalid
    fields raise :class:`MetadataValidationError`.
    """

    lines = text.splitlines(keepends=True)
    if not lines or not _is_delimiter(lines[0], first_line=True):
        return ParsedMemory(format="legacy", body=text, metadata=None)

    closing_index = next(
        (index for index, line in enumerate(lines[1:], start=1) if _is_delimiter(line)),
        None,
    )
    if closing_index is None:
        raise MetadataValidationError("frontmatter: missing closing +++ delimiter")

    toml_text = "".join(lines[1:closing_index])
    try:
        metadata = tomllib.loads(toml_text)
    except tomllib.TOMLDecodeError as exc:
        raise MetadataValidationError(f"frontmatter: invalid TOML: {exc}") from exc

    validate_v1(metadata)
    return ParsedMemory(
        format="v1",
        body="".join(lines[closing_index + 1 :]),
        metadata=metadata,
    )


def parse_memory_file(path: str | Path) -> ParsedMemory:
    """Read a UTF-8 Markdown file and parse its optional metadata."""

    memory_path = Path(path)
    try:
        text = memory_path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError as exc:
        raise MetadataValidationError(f"file is not valid UTF-8: {exc}") from exc
    return parse_memory_text(text)


def validate_paths(paths: Sequence[str | Path]) -> int:
    """Validate paths for CLI use and return a process exit code."""

    invalid = 0
    for raw_path in paths:
        path = Path(raw_path)
        try:
            parsed = parse_memory_file(path)
        except (OSError, MetadataValidationError) as exc:
            invalid += 1
            print(f"INVALID\t{path}\t{exc}")
            continue
        print(f"{parsed.format.upper()}\t{path}")
    return 1 if invalid else 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate optional v1 TOML metadata in episodic memories."
    )
    parser.add_argument("paths", nargs="+", help="Markdown memory files")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    return validate_paths(args.paths)


if __name__ == "__main__":
    sys.exit(main())
