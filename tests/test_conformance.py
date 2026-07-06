import json
from pathlib import Path

import pytest

from linked_markdown import LinkedMarkdownError, extract

CONFORMANCE_ROOT = Path(__file__).parent.parent / "test" / "linked-markdown-spec" / "conformance"
MANIFEST = json.loads((CONFORMANCE_ROOT / "manifest.json").read_text())


@pytest.mark.parametrize("case", MANIFEST["cases"], ids=lambda case: case["id"])
def test_conformance(case: dict) -> None:
    input_text = _read_fixture(case["input"])

    expect = case.get("expect", {})

    if "error" in expect:
        with pytest.raises(LinkedMarkdownError) as error:
            extract(input_text)
        assert error.value.code == expect["error"]["code"]
        return

    result = extract(input_text)

    if parsed := expect.get("parsed"):
        expected = json.loads(_read_fixture(parsed))
        assert result["attrs"] == expected, f"attrs mismatch for {case['id']}"

    if extracted := expect.get("extracted"):
        expected = json.loads(_read_fixture(extracted))
        assert result == expected, f"extracted mismatch for {case['id']}"


def _read_fixture(path: str) -> str:
    return (CONFORMANCE_ROOT / path).read_text(encoding="utf-8")
