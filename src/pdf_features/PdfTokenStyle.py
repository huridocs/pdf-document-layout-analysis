from lxml import etree
from lxml.etree import ElementBase
from pydantic import BaseModel

from pdf_features.ListLevel import ListLevel
from pdf_features.PdfFont import PdfFont
from pdf_features.ScriptType import ScriptType
from pdf_features.TitleStyle import TitleStyle


class PdfTokenStyle(BaseModel):
    font: PdfFont
    href: str = ""
    is_bold_markup: bool = False
    is_italic_markup: bool = False
    script_type: ScriptType = ScriptType.REGULAR
    is_code: bool = False
    indentation: int = 0
    height_ratio: float = 1.0
    title_style: TitleStyle = ""
    list_style: ListLevel = 0

    @staticmethod
    def from_xml_tag(xml_tag: ElementBase, content: str, pdf_font: PdfFont) -> "PdfTokenStyle":
        html = etree.tostring(xml_tag, encoding="unicode", method="xml")
        is_bold_markup = "</b>" in html
        is_italic_markup = "</i>" in html
        links = xml_tag.findall(".//a")

        href = ""
        if links and links[0].attrib.get("href", "").startswith("http"):
            link_element = links[0]
            link_text = "".join(link_element.itertext()).strip()
            if link_text == content:
                href = link_element.attrib["href"]
        return PdfTokenStyle(font=pdf_font, href=href, is_bold_markup=is_bold_markup, is_italic_markup=is_italic_markup)

    @property
    def is_bold(self) -> bool:
        return self.is_bold_markup or self.font.bold

    @property
    def is_italic(self) -> bool:
        return self.is_italic_markup or self.font.italics

    def set_title_format(self, text_height: int, most_common_text_height: int):
        self.height_ratio = text_height / most_common_text_height
        self.title_style = TitleStyle.from_token_height(self.height_ratio)
