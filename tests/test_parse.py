from linked_markdown_py.parse import ParseOptions, parse


def test_parse_preserves_attrs():
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


def test_parse_works_without_id_or_type():
    content = """---
title: Untitled
---
Body
"""
    result = parse(content)
    assert result == {"title": "Untitled"}


def test_parse_attaches_body_with_body_predicate():
    content = """---
"@id": https://example.org/docs/article
"@type": schema:Article
---
# Main Heading

Article text body goes here.
"""
    result = parse(content, ParseOptions(body_predicate="schema:articleBody"))
    assert result["schema:articleBody"] == "# Main Heading\n\nArticle text body goes here.\n"
