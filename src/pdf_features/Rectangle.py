import os
import sys

from lxml.etree import ElementBase
from pydantic import BaseModel

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))


class Rectangle(BaseModel):
    left: int
    top: int
    right: int
    bottom: int
    width: int
    height: int

    @staticmethod
    def from_poppler_tag_etree(tag: ElementBase) -> "Rectangle":
        content = "".join(tag.itertext())

        x_min = int(tag.attrib["left"])
        y_min = int(tag.attrib["top"])
        x_max = x_min + int(tag.attrib["width"])
        y_max = y_min + int(tag.attrib["height"])

        if len(content) <= 1:
            return Rectangle.from_coordinates(x_min, y_min, x_max, y_max)

        one_character_length = max(int((x_max - x_min) / len(content)), 2)
        if content[0] == " ":
            x_min += one_character_length

        if content[-1] == " ":
            x_max -= one_character_length

        return Rectangle.from_coordinates(x_min, y_min, x_max, y_max)

    def get_intersection_percentage(self, rectangle: "Rectangle") -> float:
        x1 = max(self.left, rectangle.left)
        y1 = max(self.top, rectangle.top)
        x2 = min(self.right, rectangle.right)
        y2 = min(self.bottom, rectangle.bottom)

        if x2 <= x1 or y2 <= y1:
            return 0

        return 100 * (x2 - x1) * (y2 - y1) / self.area()

    def get_vertical_intersection(self, rectangle: "Rectangle") -> float:
        top = max(self.top, rectangle.top)
        bottom = min(self.bottom, rectangle.bottom)

        if bottom <= top:
            return 0

        return bottom - top

    def get_horizontal_distance(self, rectangle: "Rectangle") -> float:
        left = max(self.left, rectangle.left)
        right = min(self.right, rectangle.right)

        return left - right

    def area(self):
        return self.width * self.height

    def to_dict(self):
        return {"top": self.top, "left": self.left, "right": self.right, "bottom": self.bottom}

    @staticmethod
    def merge_rectangles(rectangles: list["Rectangle"]) -> "Rectangle":
        left = min([rectangle.left for rectangle in rectangles])
        top = min([rectangle.top for rectangle in rectangles])
        right = max([rectangle.right for rectangle in rectangles])
        bottom = max([rectangle.bottom for rectangle in rectangles])

        return Rectangle.from_coordinates(left, top, right, bottom)

    @staticmethod
    def from_width_height(left: int, top: int, width: int, height: int):
        return Rectangle.from_coordinates(left, top, left + width, top + height)

    @staticmethod
    def from_coordinates(left: float, top: float, right: float, bottom: float):
        left, top, right, bottom = Rectangle.fix_wrong_areas(left, top, right, bottom)
        width = right - left
        height = bottom - top
        return Rectangle(left=left, top=top, right=right, bottom=bottom, width=width, height=height)

    @staticmethod
    def fix_wrong_areas(left: float, top: float, right: float, bottom: float):
        if right == left:
            left -= 1
            right += 1

        if top == bottom:
            top -= 1
            bottom += 1

        if right < left:
            right, left = left, right

        if bottom < top:
            top, bottom = bottom, top

        return int(left), int(top), int(right), int(bottom)
