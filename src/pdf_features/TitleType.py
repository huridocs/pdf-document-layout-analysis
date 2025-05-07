from enum import StrEnum
from pdf_token_type_labels.TokenType import TokenType


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

    @classmethod
    def from_height_ratio(cls, height_ratio: float, token_type: TokenType) -> "TitleType":
        if token_type not in {TokenType.TITLE, TokenType.SECTION_HEADER}:
            return cls.NO_TITLE
        if height_ratio > HeightRatioThresholds.H1:
            return cls.H1
        elif height_ratio > HeightRatioThresholds.H2:
            return cls.H2
        elif height_ratio > HeightRatioThresholds.H3:
            return cls.H3
        else:
            return cls.H4

    @property
    def markdown(self) -> str:
        return {TitleType.H1: "#", TitleType.H2: "##", TitleType.H3: "###", TitleType.H4: "####"}.get(self, "")

    @property
    def html(self) -> str:
        return {TitleType.H1: "h1", TitleType.H2: "h2", TitleType.H3: "h3", TitleType.H4: "h4"}.get(self, "")

    def get_styled_content_markdown(self, content: str) -> str:
        if self == TitleType.NO_TITLE:
            return content
        return self.markdown + " " + content.strip()

    def get_styled_content_html(self, content: str) -> str:
        if self == TitleType.NO_TITLE:
            return content
        tag = self.html
        return f"<{tag}>{content.strip()}</{tag}>"
