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


def test_extract_crlf():
    md = "---\r\ntitle: CRLF Title\r\n---\r\n# Hello\r\n\r\nBody.\r\n"
    result = extract(md)
    assert result.attrs["title"] == "CRLF Title"
    assert result.body == "# Hello\n\nBody.\n"


def test_extract_bom():
    md = "\ufeff---\ntitle: BOM Title\n---\n# BOM\n\nBody.\n"
    result = extract(md)
    assert result.attrs["title"] == "BOM Title"
    assert result.body == "# BOM\n\nBody.\n"


def test_extract_empty_frontmatter():
    md = "---\n---\n# Just body\n"
    result = extract(md)
    assert result.attrs == {}
    assert result.body == "# Just body\n"


def test_extract_body_contains_dashes():
    md = """---
title: Dashes
---
# Body

Triple dashes in body:

---

More content.
"""
    result = extract(md)
    assert result.attrs["title"] == "Dashes"
    assert "Triple dashes in body" in result.body
