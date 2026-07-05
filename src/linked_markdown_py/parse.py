from dataclasses import dataclass
from typing import Any, Optional

from .extract import extract


@dataclass
class ParseOptions:
    body_predicate: Optional[str] = None


def parse(content: str, options: Optional[ParseOptions] = None) -> dict[str, Any]:
    result = extract(content)
    if options is not None and options.body_predicate is not None:
        result.attrs[options.body_predicate] = result.body
    return result.attrs
