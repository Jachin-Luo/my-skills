#!/usr/bin/env python3
"""Maintain and display a static catalog of user-installed AI skills."""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


SKILL_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CATALOG = SKILL_ROOT / "catalog" / "skills.json"

SKIP_PARTS = {
    ".git",
    "__pycache__",
    "node_modules",
}

SYSTEM_MARKERS = {
    ".system",
    "plugins",
    "cache",
    "openai-bundled",
    "openai-primary-runtime",
}


def expand_path(value: str) -> Path:
    return Path(os.path.expandvars(os.path.expanduser(value))).resolve()


def default_roots() -> list[Path]:
    home = Path.home()
    candidates = [
        SKILL_ROOT,
        home / ".codex" / "skills",
        home / ".agents" / "skills",
        home / ".hermes" / "skills",
    ]

    env_roots = []
    for key in ("CODEX_HOME", "AGENTS_HOME", "HERMES_HOME"):
        value = os.environ.get(key)
        if value:
            env_roots.append(Path(value) / "skills")

    roots: list[Path] = []
    for root in [*env_roots, *candidates]:
        try:
            resolved = root.resolve()
        except OSError:
            continue
        if resolved.exists() and resolved not in roots:
            roots.append(resolved)
    return roots


def looks_system_path(path: Path) -> bool:
    parts = {part.lower() for part in path.parts}
    return any(marker.lower() in parts for marker in SYSTEM_MARKERS)


def iter_skill_files(roots: Iterable[Path], include_system: bool) -> Iterable[Path]:
    seen: set[Path] = set()
    for root in roots:
        if not root.exists():
            continue
        if not include_system and looks_system_path(root):
            continue
        for current, dirnames, filenames in os.walk(root):
            current_path = Path(current)
            dirnames[:] = [
                dirname
                for dirname in dirnames
                if dirname not in SKIP_PARTS
                and (include_system or not looks_system_path(current_path / dirname))
            ]
            if "SKILL.md" not in filenames:
                continue
            skill_file = (current_path / "SKILL.md").resolve()
            if skill_file not in seen:
                seen.add(skill_file)
                yield skill_file


def parse_frontmatter(path: Path) -> dict[str, str]:
    try:
        text = path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        text = path.read_text(encoding="utf-8", errors="replace")

    if not text.startswith("---"):
        return {}

    lines = text.splitlines()
    frontmatter: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip().strip("'\"")
        if key in {"name", "description"}:
            frontmatter[key] = value
    return frontmatter


def collect_skills(roots: list[Path], include_system: bool) -> list[dict[str, object]]:
    discovered: list[dict[str, object]] = []
    names_seen: set[str] = set()

    for skill_file in iter_skill_files(roots, include_system):
        frontmatter = parse_frontmatter(skill_file)
        name = frontmatter.get("name") or skill_file.parent.name
        if name in names_seen:
            continue
        names_seen.add(name)
        discovered.append(
            {
                "name": name,
                "description": frontmatter.get("description", ""),
                "path": str(skill_file.parent),
                "path_obj": skill_file.parent,
                "source": source_label(skill_file),
            }
        )

    by_path = {skill["path_obj"]: skill for skill in discovered}
    for skill in discovered:
        parent = nearest_parent_skill(skill["path_obj"], by_path)
        skill["parent"] = parent["name"] if parent else ""
        skill["level"] = 1 if parent else 0
        del skill["path_obj"]

    return sorted(
        discovered,
        key=lambda item: (
            str(item["source"]).lower(),
            str(item["parent"] or item["name"]).lower(),
            int(item["level"]),
            str(item["name"]).lower(),
        ),
    )


def nearest_parent_skill(
    skill_dir: object, skills_by_path: dict[Path, dict[str, object]]
) -> dict[str, object] | None:
    if not isinstance(skill_dir, Path):
        return None
    for ancestor in skill_dir.parents:
        parent = skills_by_path.get(ancestor)
        if parent:
            return parent
    return None


def source_label(skill_file: Path) -> str:
    lower_parts = [part.lower() for part in skill_file.parts]
    if ".codex" in lower_parts:
        return "codex"
    if ".agents" in lower_parts:
        return "agents"
    if ".hermes" in lower_parts:
        return "hermes"
    return "workspace"


def load_catalog(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_catalog(
    path: Path, skills: list[dict[str, object]], roots: list[Path], include_system: bool
) -> None:
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "include_system": include_system,
        "roots": [str(root) for root in roots],
        "count": len(skills),
        "skills": skills,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def catalog_skills(catalog: dict[str, object]) -> list[dict[str, object]]:
    skills = catalog.get("skills", [])
    if not isinstance(skills, list):
        raise ValueError("Catalog field 'skills' must be a list.")
    return [skill for skill in skills if isinstance(skill, dict)]


def markdown(skills: list[dict[str, object]], catalog: dict[str, object] | None = None) -> str:
    has_parent = any(skill.get("parent") for skill in skills)
    if has_parent:
        headers = "| Parent | Skill | Purpose | Source | Path |"
        separator = "|---|---|---|---|---|"
    else:
        headers = "| Skill | Purpose | Source | Path |"
        separator = "|---|---|---|---|"

    lines = []
    if catalog:
        generated_at = catalog.get("generated_at", "unknown")
        lines.extend([f"Catalog generated at: {generated_at}", ""])

    lines.extend(
        [
            f"Found {len(skills)} skills.",
            "",
            headers,
            separator,
        ]
    )
    for skill in skills:
        purpose = str(skill.get("description", "")).replace("|", "\\|")
        path = str(skill.get("path", "")).replace("|", "\\|")
        source = skill.get("source", "")
        name = skill.get("name", "")
        if has_parent:
            parent = skill.get("parent") or "-"
            lines.append(f"| {parent} | {name} | {purpose} | {source} | `{path}` |")
        else:
            lines.append(f"| {name} | {purpose} | {source} | `{path}` |")
    return "\n".join(lines)


def tsv(skills: list[dict[str, object]]) -> str:
    rows = ["parent\tname\tdescription\tsource\tpath"]
    for skill in skills:
        rows.append(
            "\t".join(
                [
                    str(skill.get("parent", "")),
                    str(skill.get("name", "")),
                    str(skill.get("description", "")).replace("\t", " "),
                    str(skill.get("source", "")),
                    str(skill.get("path", "")),
                ]
            )
        )
    return "\n".join(rows)


def emit(skills: list[dict[str, object]], fmt: str, catalog: dict[str, object] | None = None) -> None:
    if fmt == "json":
        print(json.dumps(skills, ensure_ascii=False, indent=2))
    elif fmt == "tsv":
        print(tsv(skills))
    else:
        print(markdown(skills, catalog))


def main() -> int:
    parser = argparse.ArgumentParser(description="Show or update a static AI skill catalog.")
    parser.add_argument(
        "command",
        nargs="?",
        choices=("show", "init", "update", "scan"),
        default="show",
        help="show reads the static catalog; init/update rebuild it; scan only prints live scan results.",
    )
    parser.add_argument("--root", action="append", help="Skill root to scan. Can be repeated.")
    parser.add_argument("--catalog", default=str(DEFAULT_CATALOG), help="Static catalog JSON path.")
    parser.add_argument(
        "--include-system",
        action="store_true",
        help="Include .system, plugin cache, and bundled platform skills when scanning.",
    )
    parser.add_argument(
        "--format",
        choices=("markdown", "json", "tsv"),
        default="markdown",
        help="Output format.",
    )
    args = parser.parse_args()

    catalog_path = expand_path(args.catalog)

    if args.command == "show":
        if not catalog_path.exists():
            raise SystemExit(
                f"Catalog not found: {catalog_path}\n"
                "Run: python scripts/list_skills.py init"
            )
        catalog = load_catalog(catalog_path)
        emit(catalog_skills(catalog), args.format, catalog)
        return 0

    roots = [expand_path(root) for root in args.root] if args.root else default_roots()
    skills = collect_skills(roots, args.include_system)

    if args.command in {"init", "update"}:
        write_catalog(catalog_path, skills, roots, args.include_system)
        catalog = load_catalog(catalog_path)
        emit(catalog_skills(catalog), args.format, catalog)
        return 0

    emit(skills, args.format)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
