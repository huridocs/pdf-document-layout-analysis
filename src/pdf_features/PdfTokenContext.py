from pydantic import BaseModel


class PdfTokenContext(BaseModel):
    right_of_token_on_the_left: float = 0
    left_of_token_on_the_left: float = 0
    left_of_token_on_the_right: float = 0
    right_of_token_on_the_right: float = 0
