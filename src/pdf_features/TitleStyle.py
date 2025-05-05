from dataclasses import dataclass
from enum import StrEnum


@dataclass
class HeightRatioThresholds:
    H1 = 2.0
    H2 = 1.4
    H3 = 1.2


class TitleStyle(StrEnum):
    H1 = "H1"
    H2 = "H2"
    H3 = "H3"
    H4 = "H4"

    @staticmethod
    def from_token_height(height_ratio: float) -> str:
        if height_ratio > HeightRatioThresholds.H1:
            return TitleStyle.H1
        elif height_ratio > HeightRatioThresholds.H2:
            return TitleStyle.H2
        elif height_ratio > HeightRatioThresholds.H3:
            return TitleStyle.H3
        else:
            return TitleStyle.H4

    @property
    def markdown(self) -> str:
        symbols = {TitleStyle.H1: "#", TitleStyle.H2: "##", TitleStyle.H3: "###", TitleStyle.H4: "####"}
        return symbols[self]

    @property
    def html(self) -> str:
        tags = {TitleStyle.H1: "h1", TitleStyle.H2: "h2", TitleStyle.H3: "h3", TitleStyle.H4: "h4"}
        return tags[self]

    @staticmethod
    def get_styled_content_markdown(token) -> str:
        return token.token_style.title_style.markdown + " " + token.content

    @staticmethod
    def get_styled_content_html(token) -> str:
        html_tag = token.token_style.title_style.html
        return f"<{html_tag}>" + token.content + f"</{html_tag}>"
