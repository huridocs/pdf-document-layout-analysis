from lxml.etree import ElementBase
from pydantic import BaseModel


class PdfFont(BaseModel):
    font_id: str
    font_size: float
    bold: bool
    italics: bool
    color: str

    @classmethod
    def from_poppler_etree(cls, root: ElementBase) -> list["PdfFont"]:
        fonts: dict[str, ElementBase] = {font.attrib["id"]: font for font in root.findall(".//fontspec")}
        processed_font_ids: set[str] = set()
        pdf_fonts: list[PdfFont] = []
        for xml_tag in root.findall(".//text"):
            font_id: str = xml_tag.attrib.get("font", "")
            if not font_id or font_id in processed_font_ids:
                continue
            pdf_font = cls._get_pdf_font(font_id, fonts, xml_tag)
            pdf_fonts.append(pdf_font)
            processed_font_ids.add(font_id)
        return pdf_fonts

    @classmethod
    def _get_pdf_font(cls, font_id: str, fonts: dict[str, ElementBase], xml_tag: ElementBase) -> "PdfFont":
        font = fonts[font_id]
        font_size = float(font.attrib.get("size", 0))
        font_family = font.attrib.get("family", "")
        color = font.attrib.get("color", "#000000")
        content = "".join(xml_tag.itertext()).strip()
        bold = cls._is_bold(content, font_family, xml_tag)
        italics = cls._is_italic(content, font_family, xml_tag)
        return cls(font_id=font_id, font_size=font_size, bold=bold, italics=italics, color=color)

    @staticmethod
    def _is_italic(content: str, font_family: str, xml_tag: ElementBase) -> bool:
        italic_content = "".join("".join(i.itertext()) for i in xml_tag.iter("i")).strip()
        italics_list = ["Italic", "italic", "Ital", "ital", "Ita"]
        return content == italic_content and italic_content != "" or any(x in font_family for x in italics_list)

    @staticmethod
    def _is_bold(content: str, font_family: str, xml_tag: ElementBase) -> bool:
        bold_content = "".join("".join(b.itertext()) for b in xml_tag.iter("b")).strip()
        return content == bold_content and bold_content != "" or any(x in font_family for x in ["Bold", "bold"])
