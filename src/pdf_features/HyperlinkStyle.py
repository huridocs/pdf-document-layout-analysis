from enum import StrEnum
from lxml.etree import ElementBase
from pydantic import BaseModel


class HyperlinkType(StrEnum):
    WEB_URL = "Web url"
    DOCUMENT_REFERENCE = "Document reference"
    NO_LINK = "No link"


class HyperlinkStyle(BaseModel):
    link: str = ""
    type: HyperlinkType = HyperlinkType.NO_LINK

    @staticmethod
    def from_xml_tag(xml_tag: ElementBase, content: str) -> "HyperlinkStyle":
        links = xml_tag.findall(".//a")
        if not links:
            return HyperlinkStyle(link="", type=HyperlinkType.NO_LINK)

        link_element = links[0]
        link = link_element.attrib.get("href", "")
        if not link:
            return HyperlinkStyle(link="", type=HyperlinkType.NO_LINK)

        link_text = "".join(link_element.itertext()).strip()
        if link.startswith("http"):
            if link_text == content:
                return HyperlinkStyle(link=link, type=HyperlinkType.WEB_URL)
            else:
                return HyperlinkStyle(link="", type=HyperlinkType.NO_LINK)
        else:
            return HyperlinkStyle(link=link, type=HyperlinkType.DOCUMENT_REFERENCE)

    @staticmethod
    def get_styled_content_markdown(content: str, hyperlink_style: "HyperlinkStyle") -> str:
        if hyperlink_style.type != HyperlinkType.WEB_URL:
            return content
        return f"[{content}]({hyperlink_style.link})"

    @staticmethod
    def get_styled_content_html(content: str, hyperlink_style: "HyperlinkStyle") -> str:
        if hyperlink_style.type != HyperlinkType.WEB_URL:
            return content
        return f'<a href="{hyperlink_style.link}">{content}</a>'
