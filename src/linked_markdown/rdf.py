from collections.abc import Generator
from typing import Any

from rdflib import Graph, Literal, URIRef
from rdflib.namespace import RDF

from .parser import _expand_curie
from .types import LmpDocument

ARTICLE_BODY = URIRef("https://schema.org/articleBody")


def to_triples(doc: LmpDocument) -> Generator[tuple[URIRef, URIRef, Any], None, None]:
    if not doc.id:
        return

    subject = URIRef(doc.id)

    for doc_type in doc.types:
        yield subject, RDF.type, URIRef(doc_type)

    if doc.body:
        yield subject, ARTICLE_BODY, Literal(doc.body)

    for key, value in doc.frontmatter.items():
        if key in {"id", "@id", "type", "@type", "@context"}:
            continue
        if not isinstance(value, str):
            continue
        yield subject, URIRef(_expand_curie(key, doc.context)), Literal(value)


def to_graph(doc: LmpDocument, graph: Graph | None = None) -> Graph:
    target = graph or Graph()
    for triple in to_triples(doc):
        target.add(triple)
    return target


def to_ntriples(doc: LmpDocument) -> str:
    graph = to_graph(doc)
    lines = graph.serialize(format="nt").splitlines()
    return "\n".join(sorted(line for line in lines if line)) + "\n"
