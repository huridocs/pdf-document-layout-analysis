from lxml.etree import ElementBase
from pydantic import BaseModel

from pdf_features.HyperlinkStyle import HyperlinkStyle
from pdf_features.ListLevel import ListLevel
from pdf_features.PdfFont import PdfFont
from pdf_features.Rectangle import Rectangle
from pdf_features.ScriptType import ScriptType
from pdf_features.TitleType import TitleType
from pdf_token_type_labels.TokenType import TokenType


class PdfTokenStyle(BaseModel):
    font: PdfFont
    hyperlink_style: HyperlinkStyle = HyperlinkStyle()
    script_type: ScriptType = ScriptType.REGULAR
    is_code: bool = False
    title_type: TitleType = TitleType.NO_TITLE
    list_level: ListLevel = ListLevel.LEVEL_0

    @staticmethod
    def from_xml_tag(xml_tag: ElementBase, content: str, pdf_font: PdfFont) -> "PdfTokenStyle":
        hyperlink_style: HyperlinkStyle = HyperlinkStyle.from_xml_tag(xml_tag, content)
        return PdfTokenStyle(font=pdf_font, hyperlink_style=hyperlink_style)

    def get_styled_content_markdown(self, content: str):
        styled_content = content
        if self.font.italics:
            styled_content = "_" + content + "_"
        if self.font.bold:
            styled_content = "**" + content + "**"
        return styled_content

    def get_styled_content_html(self, content: str):
        styled_content = content
        if self.font.italics:
            styled_content = "<i>" + content + "</i>"
        if self.font.bold:
            styled_content = "<b>" + content + "</b>"
        return styled_content

    def set_title_type(self, text_height: int, most_common_text_height: int, token_type: TokenType):
        height_ratio = text_height / most_common_text_height
        self.title_type = TitleType.from_height_ratio(height_ratio, token_type)

    def set_script_style(self, common_text_height: int, content: str, token_box: Rectangle, page_boxes: list[Rectangle]):
        self.script_type = ScriptType.from_text_height(common_text_height, content, token_box, page_boxes)

    def set_list_level(self, content: str):
        self.list_level = ListLevel.from_content(content)
