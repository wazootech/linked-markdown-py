# Agent guidelines

## What this repo is

This repository contains the Python implementation of Linked Markdown.

## How to work here

- Use `pyproject.toml` as the source of truth for package metadata and tooling.
- Prefer `uv` workflows when dependencies or lockfile behavior matter.
- Run focused pytest checks for behavior changes, and run Ruff formatting/linting
  when touching Python code.
- Keep public API changes documented in `README.md` or the appropriate docs.

## Code health

Family-wide rules live in the [wazootech workspace constitution](https://github.com/wazootech/workspace/blob/main/AGENTS.md#code-health-standards); this repo's specifics:

- Before pushing, run `uv run ruff check && uv run ruff format --check && uv run pytest` (CI runs the same).
- `.github/workflows/secret-scan.yml` runs gitleaks on every PR and push to `main`.
- Actions in `.github/workflows/` (CI and release) are pinned to commit SHAs; `renovate.json` keeps them current.
- `.github/CODEOWNERS` assigns `* @EthanThatOneKid`.
