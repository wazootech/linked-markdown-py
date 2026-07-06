import json
import re
import tomllib
from typing import Any

import yaml

VALID_MARKERS = frozenset({"yaml", "json", "toml"})


class LinkedMarkdownError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def extract(content: str) -> dict[str, Any]:
    content = content.replace("\ufeff", "").replace("\r\n", "\n")

    _check_unknown_markers(content)

    has_opener = bool(re.match(r"^(---|\+\+\+(?:\n|$)|= \w+ =(?:\n|$))", content))
    if not has_opener:
        raise LinkedMarkdownError("LMD_NO_FRONTMATTER", "Expected frontmatter at the start of the document.")

    patterns: list[tuple[str, str, str]] = [
        (r"^---yaml\n", r"\n---", "yaml"),
        (r"^---json\n", r"\n---", "json"),
        (r"^---toml\n", r"\n---", "toml"),
        (r"^\+\+\+\n", r"\n\+\+\+", "toml"),
        (r"^= yaml =\n", r"\n= yaml =", "yaml"),
        (r"^= json =\n", r"\n= json =", "json"),
        (r"^= toml =\n", r"\n= toml =", "toml"),
    ]

    for opener_pat, closer_pat, fmt in patterns:
        opener_match = re.match(opener_pat, content)
        if opener_match:
            opener_len = len(opener_match.group(0))
            remaining = content[opener_len:]
            end_match = re.search(closer_pat, remaining)
            if end_match is None:
                raise LinkedMarkdownError("LMD_INVALID_FRONTMATTER", "Expected closing frontmatter delimiter.")
            raw_fm = remaining[:end_match.start()]
            body = remaining[end_match.end():].lstrip("\n")
            return _build_extract_result(raw_fm, body, fmt)

    if content.startswith("---\n"):
        end = content.find("\n---", 3)
        if end == -1:
            raise LinkedMarkdownError("LMD_INVALID_FRONTMATTER", "Expected closing frontmatter delimiter.")
        raw_fm = content[4:end]
        body = content[end + 4:].lstrip("\n")
        fmt = "json" if raw_fm.strip().startswith(("{", "[")) else "yaml"
        return _build_extract_result(raw_fm, body, fmt)

    raise LinkedMarkdownError("LMD_INVALID_FRONTMATTER", "Unrecognized frontmatter delimiter pattern.")


def _check_unknown_markers(content: str) -> None:
    marker_match = re.match(r"^---(\w+)", content)
    if marker_match:
        marker = marker_match.group(1).lower()
        if marker and marker not in VALID_MARKERS:
            raise LinkedMarkdownError("LMD_INVALID_FRONTMATTER", f"Unknown front matter marker: ---{marker}")

    equals_match = re.match(r"^= (\w+) =", content)
    if equals_match:
        marker = equals_match.group(1).lower()
        if marker not in VALID_MARKERS:
            raise LinkedMarkdownError("LMD_INVALID_FRONTMATTER", f"Unknown front matter marker: = {marker} =")


def _build_extract_result(raw_fm: str, body: str, fmt: str) -> dict[str, Any]:
    try:
        if fmt == "json":
            attrs = json.loads(raw_fm) if raw_fm.strip() else {}
        elif fmt == "toml":
            attrs = tomllib.loads(raw_fm) if raw_fm.strip() else {}
        else:
            attrs = yaml.safe_load(raw_fm) if raw_fm.strip() else {}
    except (json.JSONDecodeError, tomllib.TOMLDecodeError, yaml.YAMLError) as e:
        raise LinkedMarkdownError("LMD_INVALID_FRONTMATTER", f"Invalid {fmt} frontmatter: {e}") from e

    if attrs is None:
        attrs = {}
    if not isinstance(attrs, dict):
        raise LinkedMarkdownError("LMD_INVALID_FRONTMATTER", "Frontmatter must parse to an object.")

    front_matter = raw_fm + "\n" if raw_fm else ""
    return {"attrs": attrs, "frontMatter": front_matter, "body": body}
