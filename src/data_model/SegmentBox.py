from paragraph_extraction_trainer.PdfSegment import PdfSegment
from pdf_features.Rectangle import Rectangle
from pdf_token_type_labels.TokenType import TokenType
from pydantic import BaseModel

from configuration import DOCLAYNET_TYPE_BY_ID


class SegmentBox(BaseModel):
    left: float
    top: float
    width: float
    height: float
    page_number: int
    text: str = ""
    type: TokenType = TokenType.TEXT

    def to_dict(self):
        return {
            "left": self.left,
            "top": self.top,
            "width": self.width,
            "height": self.height,
            "page_number": self.page_number,
            "text": self.text,
            "type": self.type.name,
        }

    @staticmethod
    def from_pdf_segment(pdf_segment: PdfSegment):
        return SegmentBox(
            left=pdf_segment.bounding_box.left,
            top=pdf_segment.bounding_box.top,
            width=pdf_segment.bounding_box.width,
            height=pdf_segment.bounding_box.height,
            page_number=pdf_segment.page_number,
            text=pdf_segment.text_content,
            type=pdf_segment.segment_type,
        )
