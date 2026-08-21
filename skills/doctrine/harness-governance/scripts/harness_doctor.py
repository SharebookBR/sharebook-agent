#!/usr/bin/env python3
"""Deterministic structural audit for the Sharebook knowledge harness."""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Sequence
from urllib.parse import unquote

from episodic_memory_metadata import MetadataValidationError, parse_memory_text


IGNORED_DIRECTORIES = {
    ".git",
    ".idea",
    ".pytest_cache",
    ".venv",
    ".vscode",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
    "temp",
    "var",
}

REFERENCE_LINK_RE = re.compile(r"^\s{0,3}\[[^\]\n]+\]:\s*(<[^>\n]+>|\S+)")
URI_SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
WINDOWS_DRIVE_RE = re.compile(r"^[A-Za-z]:[\\/]")
MEMORY_NAME_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})(?:-[^/\\]+)?\.md$")


@dataclass(frozen=True)
class Finding:
    code: str
    path: str
    message: str
    line: int | None = None
    target: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {key: value for key, value in asdict(self).items() if value is not None}


class HarnessDoctor:
    """Run read-only, deterministic checks over one sharebook-agent root."""

    def __init__(self, root: Path, *, today: dt.date | None = None) -> None:
        self.root = root.resolve()
        self.today = today or dt.date.today()

    def run(self) -> list[Finding]:
        findings: list[Finding] = []
        findings.extend(self.audit_markdown_links())
        findings.extend(self.audit_skill_index_coverage())
        findings.extend(self.audit_skill_artifacts())
        findings.extend(self.audit_dream_state())
        findings.extend(self.audit_memory_frontmatter())
        return sorted(
            set(findings),
            key=lambda finding: (
                finding.code,
                finding.path,
                finding.line or 0,
                finding.target or "",
                finding.message,
            ),
        )

    def audit_markdown_links(self) -> list[Finding]:
        findings: list[Finding] = []
        for markdown_file in self._files_named("*.md"):
            text = self._read_text(markdown_file)
            for line_number, raw_target in extract_relative_markdown_links(text):
                target = normalize_link_target(raw_target)
                if target is None:
                    continue
                resolved = (markdown_file.parent / Path(target.replace("/", os.sep))).resolve()
                if not resolved.exists():
                    findings.append(
                        Finding(
                            code="broken_markdown_link",
                            path=self._display_path(markdown_file),
                            line=line_number,
                            target=raw_target,
                            message=f"Link relativo não resolve: {raw_target}",
                        )
                    )
        return findings

    def audit_skill_index_coverage(self) -> list[Finding]:
        skills_root = self.root / "skills"
        if not skills_root.is_dir():
            return [
                Finding(
                    code="missing_skills_directory",
                    path="skills",
                    message="Diretório canônico de skills não existe.",
                )
            ]

        findings: list[Finding] = []
        for family in sorted(path for path in skills_root.iterdir() if path.is_dir()):
            if family.name in IGNORED_DIRECTORIES:
                continue
            family_index = family / "INDEX.md"
            index_text = self._read_text(family_index) if family_index.is_file() else ""
            for skill_file in sorted(family.rglob("SKILL.md")):
                if self._is_ignored(skill_file):
                    continue
                if not family_index.is_file():
                    findings.append(
                        Finding(
                            code="missing_family_index",
                            path=self._display_path(family),
                            message=f"Família sem INDEX.md para legitimar {self._display_path(skill_file)}.",
                        )
                    )
                elif not path_is_mentioned(skill_file, family_index, index_text, self.root):
                    findings.append(
                        Finding(
                            code="unindexed_skill",
                            path=self._display_path(skill_file),
                            message=f"Skill ausente de {self._display_path(family_index)}.",
                        )
                    )
        return findings

    def audit_skill_artifacts(self) -> list[Finding]:
        skills_root = self.root / "skills"
        if not skills_root.is_dir():
            return []

        findings: list[Finding] = []
        skill_directories = {
            path.parent.resolve()
            for path in skills_root.rglob("SKILL.md")
            if not self._is_ignored(path)
        }

        # Immediate family children are either standalone Markdown skills or skill folders.
        for family in sorted(path for path in skills_root.iterdir() if path.is_dir()):
            if family.name in IGNORED_DIRECTORIES:
                continue
            for child in sorted(path for path in family.iterdir() if path.is_dir()):
                if child.name in IGNORED_DIRECTORIES:
                    continue
                if child.resolve() not in skill_directories:
                    findings.append(
                        Finding(
                            code="skill_directory_without_skill",
                            path=self._display_path(child),
                            message="Pasta de skill sem SKILL.md.",
                        )
                    )

        for skill_directory in sorted(skill_directories):
            skill_file = skill_directory / "SKILL.md"
            skill_text = self._read_text(skill_file).replace("\\", "/").casefold()
            nested_skill_directories = {
                candidate.parent.resolve()
                for candidate in skill_directory.rglob("SKILL.md")
                if candidate.parent.resolve() != skill_directory
            }

            for current_root, directory_names, file_names in os.walk(skill_directory):
                current = Path(current_root)
                directory_names[:] = sorted(
                    name
                    for name in directory_names
                    if name not in IGNORED_DIRECTORIES
                    and (current / name).resolve() not in nested_skill_directories
                )

                for directory_name in directory_names:
                    directory = current / directory_name
                    relative = directory.relative_to(skill_directory).as_posix()
                    if not artifact_is_mentioned(relative, skill_text, is_directory=True):
                        findings.append(
                            Finding(
                                code="orphan_skill_directory",
                                path=self._display_path(directory),
                                message=f"Pasta não mencionada em {self._display_path(skill_file)}.",
                            )
                        )

                for file_name in sorted(file_names):
                    artifact = current / file_name
                    if artifact == skill_file or self._is_ignored(artifact):
                        continue
                    relative = artifact.relative_to(skill_directory).as_posix()
                    if not artifact_is_mentioned(relative, skill_text, is_directory=False):
                        findings.append(
                            Finding(
                                code="orphan_skill_artifact",
                                path=self._display_path(artifact),
                                message=f"Artefato não mencionado em {self._display_path(skill_file)}.",
                            )
                        )
        return findings

    def audit_dream_state(self) -> list[Finding]:
        state_file = self.root / "memory" / "_dream-state.md"
        if not state_file.is_file():
            return [
                Finding(
                    code="missing_dream_state",
                    path="memory/_dream-state.md",
                    message="Checkpoint oficial do Dream não existe.",
                )
            ]

        findings: list[Finding] = []
        text = self._read_text(state_file)
        if not re.search(r"(?im)^#\s+Dream State\s*$", text):
            findings.append(
                Finding(
                    code="invalid_dream_state",
                    path=self._display_path(state_file),
                    message="Título '# Dream State' ausente.",
                )
            )
        if not re.search(r"(?im)^##\s+[ÚU]ltimo dream\s*$", text):
            findings.append(
                Finding(
                    code="invalid_dream_state",
                    path=self._display_path(state_file),
                    message="Seção '## Último dream' ausente.",
                )
            )

        date_match = re.search(r"(?im)^-\s*Data:\s*`?(\d{4}-\d{2}-\d{2})`?\s*$", text)
        dream_date: dt.date | None = None
        if date_match is None:
            findings.append(
                Finding(
                    code="invalid_dream_state",
                    path=self._display_path(state_file),
                    message="Campo Data ausente ou fora do formato YYYY-MM-DD.",
                )
            )
        else:
            try:
                dream_date = dt.date.fromisoformat(date_match.group(1))
                if dream_date > self.today:
                    findings.append(
                        Finding(
                            code="incoherent_dream_state",
                            path=self._display_path(state_file),
                            message=f"Data do Dream está no futuro: {dream_date.isoformat()}.",
                        )
                    )
            except ValueError:
                findings.append(
                    Finding(
                        code="invalid_dream_state",
                        path=self._display_path(state_file),
                        message=f"Data inválida: {date_match.group(1)}.",
                    )
                )

        memory_match = re.search(
            r"(?im)^-\s*[ÚU]ltima memória absorvida:\s*`?([^`\r\n]+?)`?\s*$", text
        )
        if memory_match is None:
            findings.append(
                Finding(
                    code="invalid_dream_state",
                    path=self._display_path(state_file),
                    message="Campo 'Última memória absorvida' ausente.",
                )
            )
            return findings

        memory_reference = memory_match.group(1).strip()
        memory_name = Path(memory_reference.replace("\\", "/")).name
        referenced_memory = self.root / "memory" / memory_name
        if not referenced_memory.is_file():
            findings.append(
                Finding(
                    code="incoherent_dream_state",
                    path=self._display_path(state_file),
                    target=memory_reference,
                    message="Última memória absorvida não existe em memory/.",
                )
            )
        name_match = MEMORY_NAME_RE.match(memory_name)
        if name_match is None:
            findings.append(
                Finding(
                    code="incoherent_dream_state",
                    path=self._display_path(state_file),
                    target=memory_reference,
                    message="Última memória absorvida não segue o nome YYYY-MM-DD[-tema].md.",
                )
            )
        elif dream_date is not None:
            try:
                memory_date = dt.date.fromisoformat(name_match.group(1))
                if memory_date > dream_date:
                    findings.append(
                        Finding(
                            code="incoherent_dream_state",
                            path=self._display_path(state_file),
                            target=memory_reference,
                            message="Última memória absorvida é posterior à data do Dream.",
                        )
                    )
            except ValueError:
                pass
        return findings

    def audit_memory_frontmatter(self) -> list[Finding]:
        memory_root = self.root / "memory"
        if not memory_root.is_dir():
            return []

        findings: list[Finding] = []
        for memory_file in sorted(memory_root.rglob("*.md")):
            if memory_file.name == "_dream-state.md" or self._is_ignored(memory_file):
                continue
            text = self._read_text(memory_file)
            if not text.startswith("+++"):
                continue
            try:
                parsed = parse_memory_text(text)
            except MetadataValidationError as error:
                findings.append(
                    Finding(
                        code="invalid_memory_frontmatter",
                        path=self._display_path(memory_file),
                        line=1,
                        message=str(error),
                    )
                )
                continue
            metadata = parsed.metadata or {}
            session_date = metadata.get("session_date")
            filename_match = MEMORY_NAME_RE.match(memory_file.name)
            if isinstance(session_date, dt.date) and filename_match:
                if session_date.isoformat() != filename_match.group(1):
                    findings.append(
                        Finding(
                            code="incoherent_memory_frontmatter",
                            path=self._display_path(memory_file),
                            message="session_date diverge da data no nome do arquivo.",
                        )
                    )
        return findings

    def _files_named(self, pattern: str) -> Iterable[Path]:
        for path in sorted(self.root.rglob(pattern)):
            if path.is_file() and not self._is_ignored(path):
                yield path

    def _is_ignored(self, path: Path) -> bool:
        try:
            relative = path.resolve().relative_to(self.root)
        except ValueError:
            return True
        return any(part in IGNORED_DIRECTORIES for part in relative.parts)

    def _display_path(self, path: Path) -> str:
        try:
            return path.resolve().relative_to(self.root).as_posix()
        except ValueError:
            return str(path)

    @staticmethod
    def _read_text(path: Path) -> str:
        return path.read_text(encoding="utf-8-sig")


def extract_relative_markdown_links(text: str) -> Iterable[tuple[int, str]]:
    """Yield Markdown link targets outside fenced and inline code."""
    in_fence = False
    fence_marker = ""
    for line_number, line in enumerate(text.splitlines(), start=1):
        fence_match = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if fence_match:
            marker = fence_match.group(1)
            if not in_fence:
                in_fence = True
                fence_marker = marker[0]
            elif marker[0] == fence_marker:
                in_fence = False
            continue
        if in_fence:
            continue

        visible_line = re.sub(r"`+[^`\n]*`+", "", line)
        reference_match = REFERENCE_LINK_RE.match(visible_line)
        if reference_match:
            yield line_number, reference_match.group(1)
        for target in extract_inline_link_targets(visible_line):
            yield line_number, target


def extract_inline_link_targets(line: str) -> Iterable[str]:
    """Extract inline targets while respecting balanced parentheses."""
    cursor = 0
    while True:
        opener = line.find("](", cursor)
        if opener < 0:
            return
        index = opener + 2
        while index < len(line) and line[index].isspace():
            index += 1
        start = index
        if index < len(line) and line[index] == "<":
            closing_angle = line.find(">", index + 1)
            if closing_angle >= 0:
                yield line[start : closing_angle + 1]
                cursor = closing_angle + 1
                continue

        depth = 0
        escaped = False
        while index < len(line):
            character = line[index]
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == "(":
                depth += 1
            elif character == ")":
                if depth == 0:
                    yield line[start:index]
                    cursor = index + 1
                    break
                depth -= 1
            index += 1
        else:
            cursor = opener + 2


def normalize_link_target(raw_target: str) -> str | None:
    target = html.unescape(raw_target.strip())
    if target.startswith("<") and ">" in target:
        target = target[1 : target.index(">")]
    else:
        target = re.split(r"\s+(?=[\"'(])", target, maxsplit=1)[0]
    target = target.strip().replace("\\ ", " ")
    if not target or target.startswith("#") or target.startswith(("//", "/", "\\")):
        return None
    if URI_SCHEME_RE.match(target) and not WINDOWS_DRIVE_RE.match(target):
        return None
    if WINDOWS_DRIVE_RE.match(target):
        return None
    target = target.split("#", 1)[0].split("?", 1)[0]
    target = unquote(target).strip()
    return target or None


def path_is_mentioned(path: Path, document: Path, text: str, root: Path) -> bool:
    normalized_text = text.replace("\\", "/").casefold()
    candidates = {
        path.relative_to(document.parent).as_posix(),
        path.relative_to(root).as_posix(),
    }
    candidates.update(f"./{candidate}" for candidate in tuple(candidates))
    return any(candidate.casefold() in normalized_text for candidate in candidates)


def artifact_is_mentioned(relative_path: str, skill_text: str, *, is_directory: bool) -> bool:
    normalized = relative_path.replace("\\", "/").strip("/").casefold()
    if not normalized:
        return True
    candidates = {normalized, f"./{normalized}"}
    if is_directory:
        candidates.update({f"{normalized}/", f"./{normalized}/"})
    else:
        candidates.add(Path(normalized).name.casefold())
    return any(candidate in skill_text for candidate in candidates)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Audita a saúde estrutural do harness Sharebook.")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[4],
        help="Raiz do sharebook-agent (padrão: detectada pelo caminho do script).",
    )
    parser.add_argument("--json", action="store_true", help="Emite resultado estruturado em JSON.")
    return parser


def render_human(root: Path, findings: Sequence[Finding]) -> str:
    if not findings:
        return f"Harness Doctor: limpo ({root})"
    lines = [f"Harness Doctor: {len(findings)} achado(s) ({root})"]
    for finding in findings:
        location = finding.path
        if finding.line is not None:
            location += f":{finding.line}"
        lines.append(f"- [{finding.code}] {location} — {finding.message}")
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = args.root.resolve()
    findings = HarnessDoctor(root).run()
    if args.json:
        payload = {
            "schema_version": 1,
            "root": str(root),
            "clean": not findings,
            "finding_count": len(findings),
            "findings": [finding.to_dict() for finding in findings],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(render_human(root, findings))
    return 0 if not findings else 1


if __name__ == "__main__":
    sys.exit(main())
