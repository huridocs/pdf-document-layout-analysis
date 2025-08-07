from pydantic import BaseModel
from domain.SegmentBox import SegmentBox


class Link(BaseModel):
    source_segment: SegmentBox
    destination_segment: SegmentBox
    text: str
