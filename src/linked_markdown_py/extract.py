import json
import re
import tomllib
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

import yaml

T = TypeVar("T")


@dataclass
class ExtractResult(Generic[T]):
    front_matter: str
    body: str
    attrs: T


_FRONT_MATTER_RE = re.compile(
    r"^---(\w*)\n(.*?)(?:\n?)---",
    re.DOTALL | re.MULTILINE,
)


def extract(content: str) -> ExtractResult[dict[str, Any]]:
    content = content.lstrip("\ufeff").replace("\r\n", "\n")

    match = _FRONT_MATTER_RE.match(content)
    if not match:
        raise ValueError("No valid front matter found")

    fmt = match.group(1).strip().lower() or "yaml"
    raw = match.group(2)
    body = content[match.end() :].lstrip("\n")

    if fmt == "json":
        attrs = json.loads(raw)
    elif fmt == "toml":
        attrs = tomllib.loads(raw)
    else:
        attrs = yaml.safe_load(raw)

    return ExtractResult(
        front_matter=raw,
        body=body,
        attrs=attrs or {},
    )
