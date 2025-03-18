from typing import Optional

from lxml.etree import ElementBase
from pydantic import BaseModel

from pdf_features.PdfFont import PdfFont
from pdf_features.PdfToken import PdfToken


class PdfPage(BaseModel):
    page_number: int
    page_width: int
    page_height: int
    tokens: list[PdfToken]
    pdf_name: Optional[str]

    @staticmethod
    def from_poppler_etree(xml_page: ElementBase, fonts_by_font_id: dict[str, PdfFont], pdf_name: str):
        page_number = int(xml_page.attrib["number"])
        tokens = [
            PdfToken.from_poppler_etree(page_number, xml_tag, fonts_by_font_id[xml_tag.attrib["font"]])
            for xml_tag in xml_page.findall(".//text")
        ]
        tokens = [token for token in tokens if token.content.strip()]
        width = int(xml_page.attrib["width"])
        height = int(xml_page.attrib["height"])
        return PdfPage(
            page_number=page_number,
            page_width=width,
            page_height=height,
            tokens=tokens,
            pdf_name=pdf_name,
        )
