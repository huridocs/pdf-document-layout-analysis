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
    def get_styled_content_markdown(content: str, list_level: "ListLevel") -> str:
        indentation = "\t" * list_level
        return f"{indentation}- {content}"

    @staticmethod
    def get_styled_content_html(content: str, list_level: "ListLevel") -> str:
        html = content
        for _ in range(list_level):
            html = f"<ul><li>{html}</li></ul>"
        return html
