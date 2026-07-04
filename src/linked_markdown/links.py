import re

from .types import LmpLink

_EXTERNAL_TARGET = re.compile(r"^[a-z][a-z0-9+.-]*:", re.IGNORECASE)
_CODE_SPAN = re.compile(r"`[^`]*`")
_MARKDOWN_LINK = re.compile(r"\[([^\]\n]+)\]\(([^)\n]+)\)")
_WIKILINK = re.compile(r"\[\[([^\]\n]+)\]\]")


def extract_links(body: str) -> list[LmpLink]:
    masked = _CODE_SPAN.sub(lambda match: " " * len(match.group(0)), body)
    links: list[LmpLink] = []

    for match in _MARKDOWN_LINK.finditer(masked):
        raw = match.group(0)
        text = match.group(1)
        target = match.group(2)
        links.append(
            LmpLink(
                link_type="markdown",
                target=target,
                text=text,
                span=(match.start(), match.start() + len(raw)),
                is_external=bool(_EXTERNAL_TARGET.match(target)),
            )
        )

    for match in _WIKILINK.finditer(masked):
        raw = match.group(0)
        text = match.group(1)
        links.append(
            LmpLink(
                link_type="wikilink",
                target=text,
                text=text,
                span=(match.start(), match.start() + len(raw)),
                is_external=bool(_EXTERNAL_TARGET.match(text)),
            )
        )

    return sorted(links, key=lambda link: link.span[0])
