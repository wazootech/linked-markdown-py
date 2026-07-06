import json
from pathlib import Path

import pytest
import rdflib
from rdflib import RDF, Literal, URIRef

from linked_markdown import extract

CONFORMANCE_ROOT = Path(__file__).parent.parent / "test" / "linked-markdown-spec" / "conformance"
SCHEMA = rdflib.Namespace("https://schema.org/")


def _read_fixture(path: str) -> str:
    return (CONFORMANCE_ROOT / path).read_text(encoding="utf-8")


def test_valid_yaml_marker_loads_into_rdflib():
    input_text = _read_fixture("cases/valid-yaml-marker/input.md")
    result = extract(input_text)

    g = rdflib.Graph()
    g.parse(data=json.dumps(result["attrs"]), format="json-ld")

    subject = URIRef("https://example.org/docs/fixture")
    assert (subject, RDF.type, SCHEMA.Article) in g
    assert (subject, SCHEMA.name, Literal("Delimiter Fixture")) in g


def test_missing_id_generates_blank_node():
    input_text = _read_fixture("cases/missing-id/input.md")
    result = extract(input_text)

    g = rdflib.Graph()
    g.parse(data=json.dumps(result["attrs"]), format="json-ld")

    subjects = {s for s, _, _ in g}
    assert any(isinstance(s, rdflib.BNode) for s in subjects)


def test_missing_type_produces_no_rdf_type():
    input_text = _read_fixture("cases/missing-type/input.md")
    result = extract(input_text)

    g = rdflib.Graph()
    g.parse(data=json.dumps(result["attrs"]), format="json-ld")

    assert len(list(g.triples((None, RDF.type, None)))) == 0


def test_bare_keywords_produces_no_triples_without_context():
    input_text = _read_fixture("cases/bare-keywords-preserved/input.md")
    result = extract(input_text)

    g = rdflib.Graph()
    g.parse(data=json.dumps(result["attrs"]), format="json-ld")

    assert len(g) == 0


def test_canonical_type():
    input_text = _read_fixture("cases/canonical-type/input.md")
    result = extract(input_text)

    g = rdflib.Graph()
    g.parse(data=json.dumps(result["attrs"]), format="json-ld")

    subject = URIRef("https://example.org/docs/canonical-type")
    assert (subject, RDF.type, SCHEMA.Note) in g
    assert (subject, SCHEMA.name, Literal("Canonical Type")) in g
