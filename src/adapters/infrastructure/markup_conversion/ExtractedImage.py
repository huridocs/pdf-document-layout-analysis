from pydantic import BaseModel


class ExtractedImage(BaseModel):
    image_data: bytes
    filename: str
