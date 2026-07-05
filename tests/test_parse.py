from linked_markdown_py.parse import ParseOptions, parse
from linked_markdown_py.exceptions import MissingIdError, MissingTypeError


def test_parse_preserves_canonical_fields():
    content = """---
"@id": https://example.org/docs/1
"@type": schema:Article
"@context":
  schema: https://schema.org/
name: Test Article
---
# Hello World
"""
    result = parse(content)
    assert result == {
        "@id": "https://example.org/docs/1",
        "@type": "schema:Article",
        "@context": {"schema": "https://schema.org/"},
        "name": "Test Article",
    }


def test_parse_consolidates_legacy_aliases():
    content = """---
id: https://example.org/docs/legacy
type: schema:Note
context:
  schema: https://schema.org/
title: Legacy Note
---
Body content
"""
    result = parse(content)
    assert result["@id"] == "https://example.org/docs/legacy"
    assert result["@type"] == "schema:Note"
    assert result["@context"] == {"schema": "https://schema.org/"}
    assert result["title"] == "Legacy Note"
    assert "id" not in result
    assert "type" not in result
    assert "context" not in result


def test_parse_options_override_frontmatter():
    content = """---
id: https://example.org/docs/original
type: schema:Article
---
"""
    result = parse(
        content,
        ParseOptions(
            id="https://example.org/docs/overridden",
            type="schema:TechArticle",
        ),
    )
    assert result["@id"] == "https://example.org/docs/overridden"
    assert result["@type"] == "schema:TechArticle"


def test_parse_merges_context():
    content = """---
"@id": https://example.org/doc
"@type": schema:Article
"@context":
  schema: https://schema.org/
---
Body text
"""
    result = parse(
        content,
        ParseOptions(
            context={"lmd": "https://wazootech.github.io/linked-markdown/ns#"},
        ),
    )
    assert result["@context"] == {
        "schema": "https://schema.org/",
        "lmd": "https://wazootech.github.io/linked-markdown/ns#",
    }


def test_parse_attaches_body_with_body_predicate():
    content = """---
id: https://example.org/docs/article
type: schema:Article
---
# Main Heading

Article text body goes here.
"""
    result = parse(content, ParseOptions(body_predicate="schema:articleBody"))
    assert result["schema:articleBody"] == "# Main Heading\n\nArticle text body goes here.\n"


def test_parse_missing_id():
    content = """---
type: schema:Article
---
Body
"""
    try:
        parse(content)
        assert False, "expected MissingIdError"
    except MissingIdError:
        pass


def test_parse_missing_type():
    content = """---
id: https://example.org/doc
---
Body
"""
    try:
        parse(content)
        assert False, "expected MissingTypeError"
    except MissingTypeError:
        pass
