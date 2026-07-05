from linked_markdown_py.extract import extract


def test_extract_yaml():
    md = """---
title: Test Title
---
# Hello World

Body content.
"""
    result = extract(md)
    assert result.attrs["title"] == "Test Title"
    assert result.body == "# Hello World\n\nBody content.\n"
    assert "title" in result.front_matter


def test_extract_json():
    md = """---json
{"title": "JSON Title"}
---
# Hello

Content here.
"""
    result = extract(md)
    assert result.attrs["title"] == "JSON Title"
    assert result.body == "# Hello\n\nContent here.\n"


def test_extract_no_front_matter():
    md = "# Just a heading\n\nNo front matter here."
    try:
        extract(md)
        assert False, "expected ValueError"
    except ValueError:
        pass
