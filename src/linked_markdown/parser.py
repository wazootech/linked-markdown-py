from pathlib import Path
from typing import Any

import yaml

from .links import extract_links
from .types import LmpDocument


class LmdError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def parse(content: str, base_iri: str | None = None, file_path: Path | None = None) -> LmpDocument:
    del base_iri, file_path
    normalized = content.replace("\r\n", "\n")
    frontmatter, body = _extract_frontmatter(normalized)
    context = _normalize_context(frontmatter.get("@context"))
    doc_id = _read_string(frontmatter.get("@id") or frontmatter.get("id"))

    if not doc_id:
        raise LmdError("LMD_MISSING_ID", "Expected id or @id in frontmatter.")

    raw_types = frontmatter.get("@type", frontmatter.get("type"))
    if raw_types is None:
        raise LmdError("LMD_MISSING_TYPE", "Expected @type or type in frontmatter.")

    types = [_expand_curie(item, context) for item in _normalize_string_array(raw_types)]

    return LmpDocument(
        id=doc_id,
        types=types,
        context=context,
        frontmatter=frontmatter,
        body=body,
        links=extract_links(body),
    )


def _extract_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    if not content.startswith("---\n"):
        raise LmdError("LMD_MISSING_FRONTMATTER", "Expected frontmatter delimited by --- at the start of the document.")

    end = content.find("\n---", 4)
    if end == -1:
        raise LmdError("LMD_MISSING_FRONTMATTER", "Expected closing frontmatter delimiter.")

    raw_frontmatter = content[4:end]
    body = content[end + 4 :]
    body = body.lstrip("\n")

    parsed = yaml.safe_load(raw_frontmatter) or {}
    if not isinstance(parsed, dict):
        raise LmdError("LMD_INVALID_FRONTMATTER", "Frontmatter must parse to an object.")

    return parsed, body


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
