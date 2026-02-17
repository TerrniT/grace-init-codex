---
name: grace-init-codex
description: Interactive GRACE project initializer for Codex. Expands .template files, resolves $PLACEHOLDER values, and creates CLAUDE.md + AGENTS.md and docs artifacts.
---

# grace-init-codex

Use this skill when you need to bootstrap a repository with GRACE protocol files.

## What this skill does

- Reads all `*.template` files from `assets/templates/`.
- Prompts for all `$PLACEHOLDER` values once and applies them consistently.
- Writes initialized files to the target repository root.
- Handles file conflicts with `backup`, `skip`, or `overwrite` behavior.
- Ensures `AGENTS.md` is created for Codex (mirrors generated `CLAUDE.md` when available).

## Usage

From the repository root:

```bash
python3 .agents/skills/grace-init-codex/scripts/grace_init.py
```

Optional flags:

```bash
python3 .agents/skills/grace-init-codex/scripts/grace_init.py \
  --templates-dir .agents/skills/grace-init-codex/assets/templates \
  --target-dir .
```
