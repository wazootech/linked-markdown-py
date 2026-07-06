# Linked Markdown Python

Python implementation of Linked Markdown, packaged for PyPI.

**Status:** All 26 conformance tests passing.

## API

```python
from linked_markdown.extract import extract
from linked_markdown.errors import (
    LinkedMarkdownError,
    LMD_NO_FRONTMATTER,
    LMD_INVALID_FRONTMATTER,
)

result = extract(markdown)
# => ExtractResult(front_matter="...", body="...", attrs={...})
```

### `extract(content: str) -> ExtractResult[dict]`

Parses frontmatter from a Linked Markdown document. Supports YAML (`---`, `---yaml`, `= yaml =`), JSON (`---`, `---json`, `= json =`), and TOML (`---toml`, `+++`, `= toml =`) formats.

- Strips UTF-8 BOM and normalizes CRLF to LF before parsing.
- Returns `front_matter` with a trailing newline for non-empty frontmatter.
- `front_matter` is `""` for empty frontmatter (`---\n---`).
- `body` has leading newlines stripped.

### `LinkedMarkdownError`

Thrown for all error conditions. Has a `.code` property:

| Code | When |
|------|------|
| `LMD_NO_FRONTMATTER` | No frontmatter delimiters found |
| `LMD_INVALID_FRONTMATTER` | Unknown marker, unparseable content, non-object attrs, or no closing delimiter |

```python
try:
    extract(markdown)
except LinkedMarkdownError as e:
    if e.code == LMD_NO_FRONTMATTER:
        ...
```

## Development

```sh
git submodule update --init --recursive
uv sync
uv run pytest
```
