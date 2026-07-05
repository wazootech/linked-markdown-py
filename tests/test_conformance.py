import json
from pathlib import Path

import pytest

from linked_markdown_py.parse import parse


def _find_conformance_root():
    root = Path(__file__).parent / "test" / "linked-markdown-spec" / "conformance"
    if root.exists():
        return root
    alt = Path(__file__).parent.parent / "test" / "linked-markdown-spec" / "conformance"
    if alt.exists():
        return alt
    raise RuntimeError("Cannot find conformance fixtures; run 'git submodule update --init --recursive'")


def conformance_cases():
    root = _find_conformance_root()
    manifest = json.loads((root / "manifest.json").read_text())
    for case in manifest["cases"]:
        parsed_path = case.get("expect", {}).get("parsed")
        if not parsed_path:
            continue
        input_path = root / case["input"]
        expected_path = root / parsed_path
        yield pytest.param(input_path, expected_path, id=case["id"])


@pytest.mark.parametrize(["input_path", "expected_path"], conformance_cases())
def test_conformance(input_path: Path, expected_path: Path):
    raw = input_path.read_text(encoding="utf-8")
    result = parse(raw)
    expected = json.loads(expected_path.read_text(encoding="utf-8"))
    assert result == expected
