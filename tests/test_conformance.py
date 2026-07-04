import json
from pathlib import Path

import pytest

from linked_markdown import LmdError, parse, to_ntriples

CONFORMANCE_ROOT = Path(__file__).parent.parent / "test" / "linked-markdown-spec" / "conformance"
MANIFEST = json.loads((CONFORMANCE_ROOT / "manifest.json").read_text())


@pytest.mark.parametrize("case", MANIFEST["cases"], ids=lambda case: case["id"])
def test_conformance(case: dict) -> None:
    input_text = _read_fixture(case["input"])

    if "expectError" in case:
        with pytest.raises(LmdError) as error:
            parse(input_text)
        assert error.value.code == case["expectError"]["code"]
        return

    doc = parse(input_text)

    if parsed_path := case.get("expect", {}).get("parsed"):
        assert doc.conformance_dict() == json.loads(_read_fixture(parsed_path))

    if rdf_path := case.get("expect", {}).get("rdf"):
        assert _normalize_triples(to_ntriples(doc)) == _normalize_triples(_read_fixture(rdf_path))


def _read_fixture(path: str) -> str:
    return (CONFORMANCE_ROOT / path).read_text()


def _normalize_triples(value: str) -> str:
    lines = [line for line in value.replace("\r\n", "\n").strip().split("\n") if line]
    return "\n".join(sorted(lines)) + "\n"
