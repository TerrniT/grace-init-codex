#!/usr/bin/env python3
"""Interactive GRACE initializer for Codex projects."""

from __future__ import annotations

import argparse
import re
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

PLACEHOLDER_PATTERN = re.compile(r"\$([A-Z][A-Z0-9_]*)")


@dataclass(frozen=True)
class TemplateTask:
    source: Path
    relative_output: Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Initialize GRACE docs from templates.")
    parser.add_argument(
        "--templates-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "assets" / "templates",
        help="Directory with .template files",
    )
    parser.add_argument(
        "--target-dir",
        type=Path,
        default=Path.cwd(),
        help="Repository directory where files should be generated",
    )
    return parser.parse_args()


def discover_templates(templates_dir: Path) -> list[TemplateTask]:
    if not templates_dir.exists():
        raise FileNotFoundError(f"Templates directory does not exist: {templates_dir}")

    tasks: list[TemplateTask] = []
    for source in sorted(templates_dir.rglob("*.template")):
        rel = source.relative_to(templates_dir)
        output_rel = rel.with_suffix("")
        tasks.append(TemplateTask(source=source, relative_output=output_rel))

    if not tasks:
        raise RuntimeError(f"No template files found in {templates_dir}")
    return tasks


def collect_placeholders(tasks: list[TemplateTask]) -> list[str]:
    keys: set[str] = set()
    for task in tasks:
        content = task.source.read_text(encoding="utf-8")
        keys.update(PLACEHOLDER_PATTERN.findall(content))
    return sorted(keys)


def prompt_values(keys: list[str]) -> dict[str, str]:
    values: dict[str, str] = {}
    if not keys:
        return values

    print("Found placeholders. Enter values (empty input keeps placeholder text):")
    for key in keys:
        raw = input(f"  {key}: ").strip()
        values[key] = raw if raw else f"${key}"
    return values


def render(content: str, values: dict[str, str]) -> str:
    def replace(match: re.Match[str]) -> str:
        key = match.group(1)
        return values.get(key, match.group(0))

    return PLACEHOLDER_PATTERN.sub(replace, content)


def backup_file(path: Path) -> Path:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_path = path.with_suffix(path.suffix + f".bak.{stamp}")
    shutil.copy2(path, backup_path)
    return backup_path


def resolve_conflict(path: Path, global_choice: str | None) -> tuple[str, str | None]:
    if global_choice:
        return global_choice, global_choice

    while True:
        answer = input(
            f"File exists: {path}. Choose [b]ackup/[s]kip/[o]verwrite"
            " (or append ! for all remaining, e.g. o!): "
        ).strip().lower()
        if answer in {"b", "s", "o", "b!", "s!", "o!"}:
            choice = answer[0]
            sticky = choice if answer.endswith("!") else None
            return choice, sticky
        print("Invalid choice. Use b, s, o, b!, s!, or o!.")


def write_outputs(tasks: list[TemplateTask], target_dir: Path, values: dict[str, str]) -> None:
    global_choice: str | None = None

    for task in tasks:
        output = target_dir / task.relative_output
        output.parent.mkdir(parents=True, exist_ok=True)
        rendered = render(task.source.read_text(encoding="utf-8"), values)

        if output.exists():
            choice, sticky = resolve_conflict(output, global_choice)
            if sticky:
                global_choice = sticky

            if choice == "s":
                print(f"Skipped: {output}")
                continue
            if choice == "b":
                backup_path = backup_file(output)
                print(f"Backed up existing file to: {backup_path}")

        output.write_text(rendered, encoding="utf-8")
        print(f"Wrote: {output}")


def ensure_agents_md(target_dir: Path) -> None:
    claude = target_dir / "CLAUDE.md"
    agents = target_dir / "AGENTS.md"

    if claude.exists() and not agents.exists():
        agents.write_text(claude.read_text(encoding="utf-8"), encoding="utf-8")
        print("Generated AGENTS.md from CLAUDE.md")


def main() -> int:
    args = parse_args()
    templates_dir = args.templates_dir.resolve()
    target_dir = args.target_dir.resolve()

    print(f"Templates: {templates_dir}")
    print(f"Target:    {target_dir}")

    tasks = discover_templates(templates_dir)
    values = prompt_values(collect_placeholders(tasks))
    write_outputs(tasks, target_dir, values)
    ensure_agents_md(target_dir)

    print("GRACE initialization complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
