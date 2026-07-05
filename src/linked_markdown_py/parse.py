from dataclasses import dataclass
from typing import Any, Optional

from .extract import extract


@dataclass
class ParseOptions:
    body_predicate: Optional[str] = None


def parse(content: str, options: Optional[ParseOptions] = None) -> dict[str, Any]:
    result = extract(content)
    parsed: dict[str, Any] = dict(result.attrs)
    if options is not None and options.body_predicate is not None:
        parsed[options.body_predicate] = result.body
    return parsed
