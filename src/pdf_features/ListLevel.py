from enum import IntEnum


class ListLevel(IntEnum):
    LEVEL_0 = 0
    LEVEL_1 = 1
    LEVEL_2 = 2
    LEVEL_3 = 3

    @staticmethod
    def from_content(content: str) -> "ListLevel":
        first_word = content.split()[0]
        indentation = max(0, first_word.count(".") - 1)

        if indentation >= 3:
            return ListLevel.LEVEL_3
        elif indentation == 2:
            return ListLevel.LEVEL_2
        elif indentation == 1:
            return ListLevel.LEVEL_1
        else:
            return ListLevel.LEVEL_0

    @staticmethod
    def get_styled_content_markdown(token) -> str:
        indentation = "\t" * token.token_style.list_style
        return f"{indentation}- {token.content}"

    @staticmethod
    def get_styled_content_html(token) -> str:
        html = token.content
        for _ in range(token.token_style.list_style):
            html = f"<ul><li>{html}</li></ul>"
        return html
