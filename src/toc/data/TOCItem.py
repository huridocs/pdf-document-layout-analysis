from pydantic import BaseModel

from data_model.SegmentBox import SegmentBox


class TOCItem(BaseModel):
    indentation: int
    label: str = ""
    # selectionRectangles: list[SegmentBox]
    selection_rectangle: SegmentBox
    point_closed: bool = False
