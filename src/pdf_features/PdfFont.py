from lxml.etree import ElementBase
from pydantic import BaseModel


class PdfFont(BaseModel):
    font_id: str
    font_size: float
    bold: bool
    italics: bool
    color: str

    @staticmethod
    def from_poppler_etree(xml_text_style_tag: ElementBase):
        bold: bool = "Bold" in xml_text_style_tag.attrib["family"]
        italics: bool = "Italic" in xml_text_style_tag.attrib["family"]
        font_size: float = float(xml_text_style_tag.attrib["size"])
        color: str = "#000000" if "color" not in xml_text_style_tag.attrib else xml_text_style_tag.attrib["color"]
        font_id = xml_text_style_tag.attrib["id"]
        return PdfFont(font_id=font_id, font_size=font_size, bold=bold, italics=italics, color=color)
