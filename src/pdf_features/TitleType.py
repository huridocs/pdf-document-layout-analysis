from dataclasses import dataclass
from enum import StrEnum
from pdf_token_type_labels.TokenType import TokenType


@dataclass
class HeightRatioThresholds:
    H1 = 2.0
    H2 = 1.4
    H3 = 1.2


class TitleType(StrEnum):
    H1 = "H1"
    H2 = "H2"
    H3 = "H3"
    H4 = "H4"
    NO_TITLE = "No title"

    @staticmethod
    def from_height_ratio(height_ratio: float, token_type: TokenType) -> "TitleType":
        if token_type not in {TokenType.TITLE, TokenType.SECTION_HEADER}:
            return TitleType.NO_TITLE
        if height_ratio > HeightRatioThresholds.H1:
            return TitleType.H1
        elif height_ratio > HeightRatioThresholds.H2:
            return TitleType.H2
        elif height_ratio > HeightRatioThresholds.H3:
            return TitleType.H3
        else:
            return TitleType.H4

    @property
    def markdown(self) -> str:
        return {TitleType.H1: "#", TitleType.H2: "##", TitleType.H3: "###", TitleType.H4: "####"}.get(self, "")

    @property
    def html(self) -> str:
        return {TitleType.H1: "h1", TitleType.H2: "h2", TitleType.H3: "h3", TitleType.H4: "h4"}.get(self, "")

    @classmethod
    def get_styled_content_markdown(cls, content: str, title_type: "TitleType") -> str:
        if title_type == cls.NO_TITLE:
            return content
        return title_type.markdown + " " + content

    @classmethod
    def get_styled_content_html(cls, content: str, title_type: "TitleType") -> str:
        if title_type == cls.NO_TITLE:
            return content
        tag = title_type.html
        return f"<{tag}>{content}</{tag}>"
