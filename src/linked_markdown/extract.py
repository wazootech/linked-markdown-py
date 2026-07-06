import json
import re
import tomllib
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

import yaml

from .errors import LinkedMarkdownError, LMD_INVALID_FRONTMATTER, LMD_NO_FRONTMATTER

T = TypeVar("T")


@dataclass
class ExtractResult(Generic[T]):
    front_matter: str
    body: str
    attrs: T


# Opener regex: ordered by specificity (longest match first)
_OPENER_RE = re.compile(
    r"^(?:"
    r"= yaml =|= json =|= toml =|"  # equals delimiters
    r"---yaml|---json|---toml|"     # explicit markers
    r"---|\+\+\+"                    # unmarked dash and plus
    r")",
    re.MULTILINE,
)


def _split_front_matter(
    content: str,
) -> tuple[str, str, str] | None:
    """Returns (format, raw_frontmatter, body) or None if no delimiter found.

    Format is one of: 'yaml', 'json', 'toml'.
    """
    match = _OPENER_RE.match(content)
    if not match:
        return None

    opener = match.group(0)
    rest = content[match.end() :]
    format_: str
    closer: str

    # Determine format and closer based on opener
    if opener == "---yaml":
        format_ = "yaml"
        closer = "---"
    elif opener == "---json":
        format_ = "json"
        closer = "---"
    elif opener == "---toml":
        format_ = "toml"
        closer = "---"
    elif opener == "---":
        format_ = "yaml"  # unmarked defaults to YAML (which accepts JSON)
        closer = "---"
    elif opener == "+++":
        format_ = "toml"
        closer = "+++"
    elif opener == "= yaml =":
        format_ = "yaml"
        closer = "= yaml ="
    elif opener == "= json =":
        format_ = "json"
        closer = "= json ="
    elif opener == "= toml =":
        format_ = "toml"
        closer = "= toml ="
    else:
        return None

    # Find the closer in the remaining content
    closer_idx = rest.find(f"\n{closer}")
    if closer_idx == -1:
        if rest.startswith(closer):
            raw = ""
            body = rest[len(closer) :]
            return format_, raw, body.lstrip("\n")
        return None

    raw = rest[:closer_idx + 1].lstrip("\n")
    body = rest[closer_idx + len(closer) + 1 :]
    return format_, raw, body.lstrip("\n")


def extract(content: str) -> ExtractResult[dict[str, Any]]:
    content = content.lstrip("\ufeff").replace("\r\n", "\n")

    # Check for unknown ---<word> marker
    marker_match = re.match(r"^---(\w+)", content)
    if marker_match and marker_match.group(1).lower() not in {"yaml", "json", "toml", ""}:
        raise LinkedMarkdownError(
            LMD_INVALID_FRONTMATTER,
            f"Unknown front matter marker: {marker_match.group(1)}",
        )

    # Check for unknown = <word> = marker
    equals_match = re.match(r"^= (\w+) =", content)
    if equals_match and equals_match.group(1).lower() not in {"yaml", "json", "toml"}:
        raise LinkedMarkdownError(
            LMD_INVALID_FRONTMATTER,
            f"Unknown front matter marker: {equals_match.group(1)}",
        )

    # Check if any known opener exists at all
    if not _OPENER_RE.match(content):
        raise LinkedMarkdownError(LMD_NO_FRONTMATTER)

    split = _split_front_matter(content)
    if split is None:
        # Opener exists but no closer found
        raise LinkedMarkdownError(LMD_INVALID_FRONTMATTER)

    fmt, raw, body = split

    try:
        if fmt == "json":
            attrs = json.loads(raw)
        elif fmt == "toml":
            attrs = tomllib.loads(raw)
        else:
            attrs = yaml.safe_load(raw)
    except (json.JSONDecodeError, tomllib.TOMLDecodeError, yaml.YAMLError) as e:
        raise LinkedMarkdownError(LMD_INVALID_FRONTMATTER, cause=e) from e

    if attrs is None:
        attrs = {}
    elif not isinstance(attrs, dict):
        raise LinkedMarkdownError(LMD_INVALID_FRONTMATTER)

    return ExtractResult(
        front_matter=raw,
        body=body,
        attrs=attrs,
    )
