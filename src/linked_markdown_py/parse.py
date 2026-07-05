from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Optional

from .exceptions import MissingIdError, MissingTypeError
from .extract import extract


@dataclass
class ParseOptions:
    id: Optional[str] = None
    type: Optional[str | list[str]] = None
    context: Optional[str | dict[str, Any]] = None
    body_predicate: Optional[str] = None


def _deep_merge(
    base: dict[str, Any],
    override: dict[str, Any],
) -> dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, Mapping):
            merged[key] = _deep_merge(merged[key], dict(value))
        else:
            merged[key] = value
    return merged


def parse(content: str, options: Optional[ParseOptions] = None) -> dict[str, Any]:
    result = extract(content)
    attrs = result.attrs

    at_id = attrs.pop("@id", None)
    legacy_id = attrs.pop("id", None)
    at_type = attrs.pop("@type", None)
    legacy_type = attrs.pop("type", None)
    at_context = attrs.pop("@context", None)
    legacy_context = attrs.pop("context", None)

    if options is not None:
        resolved_id = options.id or at_id or legacy_id
        resolved_type = options.type or at_type or legacy_type

        raw_context = at_context or legacy_context
        if isinstance(raw_context, dict) and isinstance(options.context, dict):
            resolved_context = _deep_merge(raw_context, options.context)
        else:
            resolved_context = options.context or raw_context
    else:
        resolved_id = at_id or legacy_id
        resolved_type = at_type or legacy_type
        resolved_context = at_context or legacy_context

    if not resolved_id:
        raise MissingIdError()
    if not resolved_type:
        raise MissingTypeError()

    parsed: dict[str, Any] = dict(attrs)
    parsed["@id"] = resolved_id
    parsed["@type"] = resolved_type
    if resolved_context:
        parsed["@context"] = resolved_context
    if options is not None and options.body_predicate is not None:
        parsed[options.body_predicate] = result.body

    return parsed
