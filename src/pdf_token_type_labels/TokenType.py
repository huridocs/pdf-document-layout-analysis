from enum import Enum


class TokenType(Enum):
    FORMULA = "Formula"
    FOOTNOTE = "Footnote"
    LIST_ITEM = "List item"
    TABLE = "Table"
    PICTURE = "Picture"
    TITLE = "Title"
    TEXT = "Text"
    PAGE_HEADER = "Page header"
    SECTION_HEADER = "Section header"
    CAPTION = "Caption"
    PAGE_FOOTER = "Page footer"

    @staticmethod
    def from_text(text: str):
        try:
            return TokenType[text.upper()]
        except KeyError:
            return TokenType.TEXT

    @staticmethod
    def from_index(index: int):
        try:
            return list(TokenType)[index]
        except IndexError:
            return TokenType.TEXT.name.lower()

    def get_index(self) -> int:
        return list(TokenType).index(self)
