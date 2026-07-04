# Linked Markdown Python

Python implementation of Linked Markdown, packaged for PyPI.

## API

```python
from linked_markdown import parse, to_graph

doc = parse(markdown)
graph = to_graph(doc)
```

## Development

```sh
git submodule update --init --recursive
uv run pytest
```

The conformance suite is consumed from the `wazootech/linked-markdown` spec repository as a git submodule.
