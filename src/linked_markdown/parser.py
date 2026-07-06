import json
import re
import tomllib
from pathlib import Path
from typing import Any

import yaml

from .links import extract_links
from .types import LmpDocument

VALID_MARKERS = frozenset({"yaml", "json", "toml"})


class LmdError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def parse(content: str, base_iri: str | None = None, file_path: Path | None = None) -> LmpDocument:
    del base_iri, file_path
    result = extract(content)
    attrs = result["attrs"]
    body = result["body"]

    context = _normalize_context(attrs.get("@context"))
    doc_id = _read_string(attrs.get("@id") or attrs.get("id"))
    raw_types = attrs.get("@type", attrs.get("type"))
    types = [_expand_curie(item, context) for item in _normalize_string_array(raw_types)] if raw_types is not None else []

    return LmpDocument(
        id=doc_id,
        types=types,
        context=context,
        frontmatter=attrs,
        body=body,
        links=extract_links(body),
    )


def extract(content: str) -> dict[str, Any]:
    content = content.replace("\ufeff", "").replace("\r\n", "\n")

    _check_unknown_markers(content)

    has_opener = bool(re.match(r"^(---|---\w+\n|\+\+\+\n|= \w+ =\n)", content))
    if not has_opener:
        raise LmdError("LMD_NO_FRONTMATTER", "Expected frontmatter at the start of the document.")

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
                raise LmdError("LMD_INVALID_FRONTMATTER", "Expected closing frontmatter delimiter.")
            raw_fm = remaining[:end_match.start()]
            body = remaining[end_match.end():].lstrip("\n")
            return _build_extract_result(raw_fm, body, fmt)

    if content.startswith("---\n"):
        end = content.find("\n---", 3)
        if end == -1:
            raise LmdError("LMD_INVALID_FRONTMATTER", "Expected closing frontmatter delimiter.")
        raw_fm = content[4:end]
        body = content[end + 4:].lstrip("\n")
        fmt = "json" if raw_fm.strip().startswith(("{", "[")) else "yaml"
        return _build_extract_result(raw_fm, body, fmt)

    raise LmdError("LMD_INVALID_FRONTMATTER", "Unrecognized frontmatter delimiter pattern.")


def _check_unknown_markers(content: str) -> None:
    marker_match = re.match(r"^---(\w+)", content)
    if marker_match:
        marker = marker_match.group(1).lower()
        if marker and marker not in VALID_MARKERS:
            raise LmdError("LMD_INVALID_FRONTMATTER", f"Unknown front matter marker: ---{marker}")

    equals_match = re.match(r"^= (\w+) =", content)
    if equals_match:
        marker = equals_match.group(1).lower()
        if marker not in VALID_MARKERS:
            raise LmdError("LMD_INVALID_FRONTMATTER", f"Unknown front matter marker: = {marker} =")


def _build_extract_result(raw_fm: str, body: str, fmt: str) -> dict[str, Any]:
    try:
        if fmt == "json":
            attrs = json.loads(raw_fm) if raw_fm.strip() else {}
        elif fmt == "toml":
            attrs = tomllib.loads(raw_fm) if raw_fm.strip() else {}
        else:
            attrs = yaml.safe_load(raw_fm) if raw_fm.strip() else {}
    except (json.JSONDecodeError, tomllib.TOMLDecodeError, yaml.YAMLError) as e:
        raise LmdError("LMD_INVALID_FRONTMATTER", f"Invalid {fmt} frontmatter: {e}") from e

    if attrs is None:
        attrs = {}
    if not isinstance(attrs, dict):
        raise LmdError("LMD_INVALID_FRONTMATTER", "Frontmatter must parse to an object.")

    front_matter = raw_fm + "\n" if raw_fm else ""
    return {"attrs": attrs, "frontMatter": front_matter, "body": body}


def _normalize_context(value: Any) -> dict[str, str]:
    if not isinstance(value, dict):
        return {}
    return {str(key): prefix for key, prefix in value.items() if isinstance(prefix, str)}


def _normalize_string_array(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return value
    raise LmdError("LMD_INVALID_TYPE", "Expected @type or type to be a string or string array.")


def _read_string(value: Any) -> str | None:
    return value if isinstance(value, str) and value else None


def _expand_curie(value: str, context: dict[str, str]) -> str:
    if "://" in value:
        return value
    prefix, separator, suffix = value.partition(":")
    if not separator:
        return value
    return f"{context[prefix]}{suffix}" if prefix in context else value
