from typing import Any, Literal

from pydantic import BaseModel, ConfigDict


class LmpLink(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    link_type: Literal["wikilink", "markdown"]
    target: str
    text: str
    span: tuple[int, int]
    is_external: bool

    def conformance_dict(self) -> dict[str, Any]:
        return {
            "linkType": self.link_type,
            "target": self.target,
            "text": self.text,
            "span": list(self.span),
            "isExternal": self.is_external,
        }


class LmpDocument(BaseModel):
    id: str | None
    types: list[str]
    context: dict[str, str]
    frontmatter: dict[str, Any]
    body: str
    links: list[LmpLink]

    def conformance_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "types": self.types,
            "context": self.context,
            "frontmatter": self.frontmatter,
            "body": self.body,
            "links": [link.conformance_dict() for link in self.links],
        }
