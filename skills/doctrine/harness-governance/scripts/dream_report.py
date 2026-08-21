"""Generate an evidence report for a Sharebook Dream cycle.

The report is deliberately observational: it reads the Dream checkpoint and
episodic memories, but never changes them or recommends/promotes durable
knowledge on its own.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
import json
from pathlib import Path
import re
import sys
import tomllib
from typing import Any, Iterable


FRONTMATTER_DELIMITER = "+++"
SUPPORTED_SCHEMA_VERSION = 1
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
KNOWN_FIELDS = {
    "schema_version",
    "session_date",
    "title",
    "model",
    "runtime",
    *LIST_FIELDS,
}


@dataclass
class MemoryRecord:
    path: Path
    relative_path: str
    session_date: str | None
    title: str
    has_metadata: bool
    metadata: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)

    def values(self, field_name: str) -> list[str]:
        value = self.metadata.get(field_name, [])
        return value if isinstance(value, list) else []


def _as_posix_relative(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def _date_from_filename(path: Path) -> str | None:
    match = re.match(r"(\d{4}-\d{2}-\d{2})(?:-|\.md$)", path.name)
    return match.group(1) if match else None


def _parse_frontmatter(text: str) -> tuple[dict[str, Any] | None, str, list[str]]:
    normalized = text.lstrip("\ufeff")
    lines = normalized.splitlines(keepends=True)
    if not lines or lines[0].strip() != FRONTMATTER_DELIMITER:
        return None, normalized, []

    closing_index = next(
        (index for index, line in enumerate(lines[1:], start=1) if line.strip() == FRONTMATTER_DELIMITER),
        None,
    )
    if closing_index is None:
        return None, normalized, ["frontmatter TOML aberto, mas sem delimitador de fechamento +++"]

    source = "".join(lines[1:closing_index])
    body = "".join(lines[closing_index + 1 :])
    try:
        parsed = tomllib.loads(source)
    except tomllib.TOMLDecodeError as exc:
        return None, body, [f"frontmatter TOML inválido: {exc}"]
    return parsed, body, []


def _normalize_list_field(
    raw: Any, field_name: str, relative_path: str, warnings: list[str]
) -> list[str]:
    if raw is None:
        return []
    if not isinstance(raw, list):
        warnings.append(f"{relative_path}: {field_name} deve ser uma lista TOML")
        return []

    values: list[str] = []
    for index, value in enumerate(raw):
        if isinstance(value, str) and value.strip():
            values.append(value.strip())
        else:
            warnings.append(
                f"{relative_path}: {field_name}[{index}] foi ignorado; esperado texto não vazio"
            )
    return values


def _first_heading(body: str, fallback: str) -> str:
    for line in body.splitlines():
        match = re.match(r"^#\s+(.+?)\s*$", line)
        if match:
            return match.group(1).strip()
    return fallback


def _clean_legacy_skill(line: str) -> str | None:
    text = re.sub(r"^\s*[-*+]\s+", "", line).strip()
    if not text:
        return None

    code_values = re.findall(r"`([^`]+)`", text)
    if code_values:
        return code_values[0].strip()

    link = re.search(r"\[([^]]+)]\(([^)]+)\)", text)
    if link:
        return link.group(1).strip()

    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(
        r"^(?:lido|lida|usado|usada|consultado|consultada|atualizado|atualizada|criado|criada)\s+",
        "",
        text,
        flags=re.IGNORECASE,
    )
    text = re.split(r"\s+[—–-]\s+|:\s+", text, maxsplit=1)[0].strip()
    return text or None


def extract_legacy_skills(body: str) -> list[str]:
    """Conservatively extract bullets under a legacy 'Skills acionadas' heading."""
    skills: list[str] = []
    inside_section = False
    for line in body.splitlines():
        heading = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if heading:
            title = heading.group(2).strip().casefold()
            inside_section = bool(re.search(r"\bskills?\s+acionad", title))
            continue
        if inside_section and re.match(r"^\s*[-*+]\s+", line):
            skill = _clean_legacy_skill(line)
            if skill:
                skills.append(skill)
    return sorted(set(skills), key=str.casefold)


def read_memory(path: Path, memory_root: Path) -> MemoryRecord:
    relative_path = _as_posix_relative(path, memory_root)
    text = path.read_text(encoding="utf-8-sig")
    raw_metadata, body, parse_warnings = _parse_frontmatter(text)
    warnings = [f"{relative_path}: {warning}" for warning in parse_warnings]
    metadata: dict[str, Any] = {}
    has_metadata = False

    if raw_metadata is not None:
        metadata_is_valid = True
        missing_fields = sorted(KNOWN_FIELDS - set(raw_metadata))
        if missing_fields:
            metadata_is_valid = False
            warnings.append(
                f"{relative_path}: campos TOML obrigatórios ausentes: {', '.join(missing_fields)}"
            )
        unknown_fields = sorted(set(raw_metadata) - KNOWN_FIELDS)
        if unknown_fields:
            metadata_is_valid = False
            warnings.append(
                f"{relative_path}: campos TOML desconhecidos: {', '.join(unknown_fields)}"
            )

        schema_version = raw_metadata.get("schema_version")
        if (
            isinstance(schema_version, bool)
            or not isinstance(schema_version, int)
            or schema_version != SUPPORTED_SCHEMA_VERSION
        ):
            metadata_is_valid = False
            warnings.append(
                f"{relative_path}: schema_version {schema_version!r} não é v{SUPPORTED_SCHEMA_VERSION}"
            )

        for field_name in LIST_FIELDS:
            normalized_values = _normalize_list_field(
                raw_metadata.get(field_name), field_name, relative_path, warnings
            )
            metadata[field_name] = normalized_values
            raw_values = raw_metadata.get(field_name)
            if not isinstance(raw_values, list) or len(normalized_values) != len(raw_values):
                metadata_is_valid = False

        for field_name in ("title", "model", "runtime"):
            value = raw_metadata.get(field_name)
            if not isinstance(value, str) or not value.strip():
                metadata_is_valid = False
                warnings.append(f"{relative_path}: {field_name} deve ser texto não vazio")
            else:
                metadata[field_name] = value.strip()

        raw_session_date = raw_metadata.get("session_date")
        if isinstance(raw_session_date, datetime) or not isinstance(raw_session_date, date):
            metadata_is_valid = False
            session_date = None
            warnings.append(
                f"{relative_path}: session_date deve ser data TOML local sem aspas (YYYY-MM-DD)"
            )
        else:
            session_date = raw_session_date.isoformat()

        has_metadata = metadata_is_valid
        if not metadata_is_valid:
            metadata = {field_name: [] for field_name in LIST_FIELDS}
            metadata["skills_used"] = extract_legacy_skills(body)
    else:
        session_date = None
        metadata["skills_used"] = extract_legacy_skills(body)
        for field_name in LIST_FIELDS[1:]:
            metadata[field_name] = []

    session_date = session_date or _date_from_filename(path)
    title = str(metadata.get("title") or _first_heading(body, path.stem))
    return MemoryRecord(
        path=path,
        relative_path=relative_path,
        session_date=session_date,
        title=title,
        has_metadata=has_metadata,
        metadata=metadata,
        warnings=warnings,
    )


def _checkpoint_info(state_path: Path) -> tuple[str | None, str | None]:
    text = state_path.read_text(encoding="utf-8-sig")
    path_match = re.search(r"Última memória absorvida:\s*`([^`]+)`", text, re.IGNORECASE)
    date_match = re.search(r"(?:^|\n)- Data:\s*`(\d{4}-\d{2}-\d{2})`", text, re.IGNORECASE)
    return (
        path_match.group(1).strip() if path_match else None,
        date_match.group(1) if date_match else None,
    )


def _resolve_checkpoint(raw_path: str | None, repo_root: Path, memory_root: Path) -> Path | None:
    if not raw_path:
        return None
    normalized = raw_path.replace("\\", "/")
    candidate = Path(raw_path)
    if candidate.is_absolute():
        return candidate.resolve()
    if normalized.startswith("memory/"):
        return (repo_root / normalized).resolve()
    return (memory_root / normalized).resolve()


def _record_sort_key(record: MemoryRecord) -> tuple[str, str]:
    return (record.session_date or "0000-00-00", record.relative_path.casefold())


def select_harvest(
    records: list[MemoryRecord],
    checkpoint: Path | None,
    checkpoint_date: str | None,
) -> tuple[list[MemoryRecord], list[str]]:
    ordered = sorted(records, key=_record_sort_key)
    warnings: list[str] = []

    if checkpoint is not None:
        for index, record in enumerate(ordered):
            if record.path.resolve() == checkpoint.resolve():
                return ordered[index + 1 :], warnings
        inferred = _date_from_filename(checkpoint)
        fallback_date = inferred or checkpoint_date
        if fallback_date:
            warnings.append(
                "checkpoint aponta para arquivo ausente; safra selecionada conservadoramente após "
                f"{fallback_date}"
            )
            return [record for record in ordered if (record.session_date or "") > fallback_date], warnings
        warnings.append("checkpoint aponta para arquivo ausente e sem data; toda a memória foi incluída")
        return ordered, warnings

    if checkpoint_date:
        warnings.append(
            "checkpoint não informa a última memória absorvida; safra selecionada após a data do Dream"
        )
        return [record for record in ordered if (record.session_date or "") > checkpoint_date], warnings

    warnings.append("checkpoint sem ponteiro e sem data; toda a memória foi incluída")
    return ordered, warnings


def _aggregate(records: Iterable[MemoryRecord], field_name: str) -> list[dict[str, Any]]:
    counts: Counter[str] = Counter()
    sources: dict[str, list[str]] = defaultdict(list)
    canonical: dict[str, str] = {}
    for record in records:
        seen_in_memory: set[str] = set()
        for value in record.values(field_name):
            key = value.casefold()
            if key in seen_in_memory:
                continue
            seen_in_memory.add(key)
            canonical.setdefault(key, value)
            counts[key] += 1
            sources[key].append(record.relative_path)
    return [
        {"skill": canonical[key], "count": counts[key], "memories": sources[key]}
        for key in sorted(counts, key=lambda item: (-counts[item], canonical[item].casefold()))
    ]


def _collect_entries(records: Iterable[MemoryRecord], field_name: str) -> list[dict[str, str]]:
    return [
        {"memory": record.relative_path, "value": value}
        for record in records
        for value in record.values(field_name)
    ]


def build_report(repo_root: Path) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    memory_root = repo_root / "memory"
    state_path = memory_root / "_dream-state.md"
    if not state_path.is_file():
        raise FileNotFoundError(f"checkpoint do Dream não encontrado: {state_path}")

    raw_checkpoint, checkpoint_date = _checkpoint_info(state_path)
    checkpoint = _resolve_checkpoint(raw_checkpoint, repo_root, memory_root)
    paths = sorted(
        (path for path in memory_root.rglob("*.md") if path.resolve() != state_path.resolve()),
        key=lambda path: path.as_posix().casefold(),
    )
    records = [read_memory(path, memory_root) for path in paths]
    harvest, selection_warnings = select_harvest(records, checkpoint, checkpoint_date)

    warnings = selection_warnings + [warning for record in harvest for warning in record.warnings]
    missing_metadata = [record.relative_path for record in harvest if not record.has_metadata]
    dated = [record.session_date for record in harvest if record.session_date]
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "checkpoint": {
            "state": _as_posix_relative(state_path, repo_root),
            "last_absorbed": raw_checkpoint,
            "dream_date": checkpoint_date,
        },
        "harvest": {
            "count": len(harvest),
            "first_date": min(dated) if dated else None,
            "last_date": max(dated) if dated else None,
            "memories": [
                {
                    "path": record.relative_path,
                    "session_date": record.session_date,
                    "title": record.title,
                    "has_metadata": record.has_metadata,
                }
                for record in harvest
            ],
        },
        "skills": {
            "used": _aggregate(harvest, "skills_used"),
            "missed": _aggregate(harvest, "skills_missed"),
            "updated": _aggregate(harvest, "skills_updated"),
        },
        "facts_changed": _collect_entries(harvest, "facts_changed"),
        "open_loops": _collect_entries(harvest, "open_loops"),
        "durable_candidates": _collect_entries(harvest, "durable_candidates"),
        "supersessions": _collect_entries(harvest, "supersedes"),
        "evidence": _collect_entries(harvest, "evidence"),
        "memories_without_metadata": missing_metadata,
        "warnings": warnings,
    }


def _markdown_table(rows: list[dict[str, Any]]) -> list[str]:
    if not rows:
        return ["_Nenhum registro._"]
    result = ["| Skill | Contagem | Memórias |", "|---|---:|---|"]
    for row in rows:
        memories = ", ".join(f"`{item}`" for item in row["memories"])
        result.append(f"| `{row['skill']}` | {row['count']} | {memories} |")
    return result


def _entry_section(entries: list[dict[str, str]]) -> list[str]:
    if not entries:
        return ["_Nenhum registro._"]
    return [f"- {entry['value']} — `{entry['memory']}`" for entry in entries]


def render_markdown(report: dict[str, Any]) -> str:
    harvest = report["harvest"]
    lines = [
        "# Relatório de evidências para o Dream",
        "",
        "> Relatório observacional. Não decide promoções e não altera memórias.",
        "",
        "## Safra",
        "",
        f"- Checkpoint: `{report['checkpoint']['last_absorbed'] or 'não informado'}`",
        f"- Intervalo: `{harvest['first_date'] or 'n/a'}` a `{harvest['last_date'] or 'n/a'}`",
        f"- Memórias não absorvidas: **{harvest['count']}**",
        "",
    ]
    lines.extend(
        f"- `{memory['path']}` — {memory['title']}" for memory in harvest["memories"]
    )

    labels = (("used", "Skills usadas"), ("missed", "Skills não acionadas"), ("updated", "Skills atualizadas"))
    for key, label in labels:
        lines.extend(["", f"## {label}", "", *_markdown_table(report["skills"][key])])

    sections = (
        ("facts_changed", "Fatos alterados"),
        ("open_loops", "Open loops"),
        ("durable_candidates", "Candidatos duráveis"),
        ("supersessions", "Supersessions"),
        ("evidence", "Evidências declaradas"),
    )
    for key, label in sections:
        lines.extend(["", f"## {label}", "", *_entry_section(report[key])])

    lines.extend(["", "## Memórias sem metadados v1", ""])
    if report["memories_without_metadata"]:
        lines.extend(f"- `{path}`" for path in report["memories_without_metadata"])
    else:
        lines.append("_Nenhuma._")

    lines.extend(["", "## Avisos", ""])
    if report["warnings"]:
        lines.extend(f"- {warning}" for warning in report["warnings"])
    else:
        lines.append("_Nenhum._")
    return "\n".join(lines) + "\n"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    default_root = Path(__file__).resolve().parents[4]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=default_root)
    parser.add_argument("--output", type=Path, help="grava o relatório Markdown; padrão: stdout")
    parser.add_argument("--json", type=Path, dest="json_output", help="grava também os dados em JSON")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        report = build_report(args.repo_root)
        markdown = render_markdown(report)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(markdown, encoding="utf-8")
        else:
            sys.stdout.write(markdown)
        if args.json_output:
            args.json_output.parent.mkdir(parents=True, exist_ok=True)
            args.json_output.write_text(
                json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
    except (FileNotFoundError, OSError) as exc:
        print(f"erro: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
