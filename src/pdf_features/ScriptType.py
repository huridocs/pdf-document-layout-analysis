from enum import StrEnum
from pdf_features.Rectangle import Rectangle


class ScriptType(StrEnum):
    REGULAR = "Regular"
    SUPERSCRIPT = "Superscript"
    SUBSCRIPT = "Subscript"

    @staticmethod
    def _get_same_line_tokens(token, page_tokens):
        top, bottom = token.bounding_box.top, token.bounding_box.bottom

        same_line_tokens = [
            each_token
            for each_token in page_tokens
            if not (each_token.bounding_box.bottom < top or bottom < each_token.bounding_box.top)
        ]

        return same_line_tokens

    @staticmethod
    def from_text_height(most_common_text_height: int, token, page_tokens):
        if token.bounding_box.height > 0.8 * most_common_text_height:
            return ScriptType.REGULAR
        if not token.content.isdigit():
            return ScriptType.REGULAR

        same_line_tokens = ScriptType._get_same_line_tokens(token, page_tokens)

        if not same_line_tokens:
            return ScriptType.REGULAR

        line_rectangle = Rectangle.merge_rectangles([t.bounding_box for t in same_line_tokens])
        middle_of_the_line = line_rectangle.top + line_rectangle.height / 2

        top_distance_to_center = abs(token.bounding_box.top - middle_of_the_line)
        bottom_distance_to_center = abs(token.bounding_box.bottom - middle_of_the_line)

        if top_distance_to_center > bottom_distance_to_center:
            return ScriptType.SUPERSCRIPT
        else:
            return ScriptType.SUBSCRIPT

    @staticmethod
    def get_styled_content(token) -> str:
        if token.token_style.script_type == ScriptType.SUPERSCRIPT:
            return "<sup>" + token.content + "</sup>"
        if token.token_style.script_type == ScriptType.SUBSCRIPT:
            return "<sub>" + token.content + "</sub>"
        return token.content
