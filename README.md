# Linked Markdown Python

Python implementation of Linked Markdown, packaged for PyPI.

## API

```python
from linked_markdown import extract

result = extract(markdown)
# => {"attrs": {...}, "frontMatter": "...", "body": "..."}
```

## Development

```sh
git submodule update --init --recursive
uv run pytest
```

The conformance suite is consumed from the `wazootech/linked-markdown` spec repository as a git submodule.
