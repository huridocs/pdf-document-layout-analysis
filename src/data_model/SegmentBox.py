from fast_trainer.PdfSegment import PdfSegment
from pdf_features.PdfPage import PdfPage
from pdf_token_type_labels.TokenType import TokenType
from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class SegmentBox(BaseModel):
    left: float
    top: float
    width: float
    height: float
    page_number: int
    page_width: int
    page_height: int
    text: str = ""
    type: TokenType = TokenType.TEXT
    sub_element_positions: Optional[List[Dict[str, Any]]] = None

    def to_dict(self):
        result = {
            "left": self.left,
            "top": self.top,
            "width": self.width,
            "height": self.height,
            "page_number": self.page_number,
            "page_width": self.page_width,
            "page_height": self.page_height,
            "text": self.text,
            "type": self.type.value,
        }
        if self.sub_elements_positions is not None:
            result["sub_elements_positions"] = self.sub_elements_positions
        return result

    @staticmethod
    def from_pdf_segment(pdf_segment: PdfSegment, pdf_pages: list[PdfPage], sub_elements: Optional[List[Dict[str, Any]]] = None):
        return SegmentBox(
            left=pdf_segment.bounding_box.left,
            top=pdf_segment.bounding_box.top,
            width=pdf_segment.bounding_box.width,
            height=pdf_segment.bounding_box.height,
            page_number=pdf_segment.page_number,
            page_width=pdf_pages[pdf_segment.page_number - 1].page_width,
            page_height=pdf_pages[pdf_segment.page_number - 1].page_height,
            text=pdf_segment.text_content,
            type=pdf_segment.segment_type,
            sub_elements_positions=sub_elements,
        )


if __name__ == "__main__":
    a = TokenType.TEXT
    print(a.value)
