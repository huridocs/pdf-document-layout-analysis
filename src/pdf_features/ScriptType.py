from enum import StrEnum
from pdf_features.Rectangle import Rectangle


class ScriptType(StrEnum):
    REGULAR = "Regular"
    SUPERSCRIPT = "Superscript"
    SUBSCRIPT = "Subscript"

    @staticmethod
    def _get_same_line_boxes(token_box: Rectangle, page_boxes: list[Rectangle]):
        top, bottom = token_box.top, token_box.bottom
        same_line_tokens = [each_box for each_box in page_boxes if not (each_box.bottom < top or bottom < each_box.top)]
        return same_line_tokens

    @staticmethod
    def from_text_height(common_text_height: int, content: str, token_box: Rectangle, page_boxes: list[Rectangle]):
        if not content.isdigit():
            return ScriptType.REGULAR
        if token_box.height > 0.8 * common_text_height:
            return ScriptType.REGULAR

        same_line_boxes = ScriptType._get_same_line_boxes(token_box, page_boxes)

        if not same_line_boxes:
            return ScriptType.REGULAR

        line_rectangle = Rectangle.merge_rectangles([t.bounding_box for t in same_line_boxes])
        middle_of_the_line = line_rectangle.top + line_rectangle.height / 2

        top_distance_to_center = abs(token_box.top - middle_of_the_line)
        bottom_distance_to_center = abs(token_box.bottom - middle_of_the_line)

        if top_distance_to_center > bottom_distance_to_center:
            return ScriptType.SUPERSCRIPT
        else:
            return ScriptType.SUBSCRIPT

    @staticmethod
    def get_styled_content(content: str, script_type: "ScriptType") -> str:
        if script_type == ScriptType.SUPERSCRIPT:
            return "<sup>" + content + "</sup>"
        if script_type == ScriptType.SUBSCRIPT:
            return "<sub>" + content + "</sub>"
        return content
