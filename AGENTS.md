# Agent guidelines

## What this repo is

This repository contains the Python implementation of Linked Markdown.

## How to work here

- Use `pyproject.toml` as the source of truth for package metadata and tooling.
- Prefer `uv` workflows when dependencies or lockfile behavior matter.
- Run focused pytest checks for behavior changes, and run Ruff formatting/linting
  when touching Python code.
- Keep public API changes documented in `README.md` or the appropriate docs.
