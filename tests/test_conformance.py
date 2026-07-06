import json
from pathlib import Path

import pytest
from linked_markdown.errors import LinkedMarkdownError

from linked_markdown.extract import extract


def _find_conformance_root() -> Path:
    # Try multiple locations to find the submodule
    candidates = [
        Path(__file__).parent / "linked-markdown-spec" / "conformance",
        Path(__file__).parent.parent / "test" / "linked-markdown-spec" / "conformance",
    ]
    for candidate in candidates:
        if (candidate / "manifest.json").exists():
            return candidate
    raise RuntimeError(
        "Cannot find conformance fixtures; run 'git submodule update --init --recursive'"
    )


def conformance_cases():
    root = _find_conformance_root()
    manifest = json.loads((root / "manifest.json").read_text())
    for case in manifest["cases"]:
        expect = case.get("expect", {})
        input_path = root / case["input"]

        # Error cases
        if "error" in expect:
            yield pytest.param(
                input_path,
                None,
                None,
                expect["error"].get("code"),
                id=f"{case['id']} (error)",
            )
            continue

        # Parsed cases
        parsed_path = expect.get("parsed")
        extracted_path = expect.get("extracted")
        if parsed_path:
            yield pytest.param(
                input_path,
                root / parsed_path,
                root / extracted_path if extracted_path else None,
                None,
                id=case["id"],
            )


@pytest.mark.parametrize(
    ["input_path", "expected_parsed_path", "expected_extracted_path", "expected_error_code"],
    list(conformance_cases()),
)
def test_conformance(
    input_path: Path,
    expected_parsed_path: Path | None,
    expected_extracted_path: Path | None,
    expected_error_code: str | None,
):
    raw = input_path.read_text(encoding="utf-8")

    if expected_error_code:
        with pytest.raises(LinkedMarkdownError) as exc_info:
            extract(raw)
        assert exc_info.value.code == expected_error_code
        return

    result = extract(raw)

    if expected_parsed_path:
        expected_parsed = json.loads(expected_parsed_path.read_text(encoding="utf-8"))
        assert result.attrs == expected_parsed

    if expected_extracted_path:
        expected_extracted = json.loads(expected_extracted_path.read_text(encoding="utf-8"))
        assert result.front_matter == expected_extracted["frontMatter"]
        assert result.body == expected_extracted["body"]
        assert result.attrs == expected_extracted["attrs"]
