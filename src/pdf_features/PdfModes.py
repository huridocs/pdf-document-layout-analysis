from pydantic import BaseModel


class PdfModes(BaseModel):
    lines_space_mode: float = 0
    right_space_mode: float = 0
    font_size_mode: float = 0
