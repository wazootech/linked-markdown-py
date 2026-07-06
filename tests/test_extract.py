import pytest
from linked_markdown.errors import LinkedMarkdownError, LMD_INVALID_FRONTMATTER, LMD_NO_FRONTMATTER

from linked_markdown.extract import extract


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


def test_extract_toml():
    md = """---toml
title = "TOML Title"
---
# Hello
"""
    result = extract(md)
    assert result.attrs["title"] == "TOML Title"


def test_extract_empty_frontmatter():
    md = "---\n---\n# Just body\n"
    result = extract(md)
    assert result.attrs == {}
    assert result.body == "# Just body\n"


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


def test_extract_no_front_matter():
    md = "# Just a heading\n\nNo front matter.\n"
    with pytest.raises(LinkedMarkdownError) as exc_info:
        extract(md)
    assert exc_info.value.code == LMD_NO_FRONTMATTER


def test_extract_unknown_marker():
    md = "---bogus\nkey: value\n---\nBody\n"
    with pytest.raises(LinkedMarkdownError) as exc_info:
        extract(md)
    assert exc_info.value.code == LMD_INVALID_FRONTMATTER


def test_extract_non_object():
    md = "---\nhello\n---\nBody\n"
    with pytest.raises(LinkedMarkdownError) as exc_info:
        extract(md)
    assert exc_info.value.code == LMD_INVALID_FRONTMATTER


def test_extract_malformed_json():
    md = "---json\n{invalid}\n---\nBody\n"
    with pytest.raises(LinkedMarkdownError) as exc_info:
        extract(md)
    assert exc_info.value.code == LMD_INVALID_FRONTMATTER


def test_extract_malformed_toml():
    md = "---toml\nkey = [[\n---\nBody\n"
    with pytest.raises(LinkedMarkdownError) as exc_info:
        extract(md)
    assert exc_info.value.code == LMD_INVALID_FRONTMATTER


def test_extract_no_closing_delimiter():
    md = "---\nkey: value\n"
    with pytest.raises(LinkedMarkdownError) as exc_info:
        extract(md)
    assert exc_info.value.code == LMD_INVALID_FRONTMATTER


def test_linked_markdown_error_has_code_and_cause():
    inner = ValueError("inner")
    err = LinkedMarkdownError(LMD_INVALID_FRONTMATTER, "message", inner)
    assert err.code == LMD_INVALID_FRONTMATTER
    assert err.cause is inner
    assert str(err) == f"[{LMD_INVALID_FRONTMATTER}] message"
