from abc import ABC, abstractmethod
from pdf_token_type_labels import TokenType


class TextExtractionService(ABC):
    @abstractmethod
    def extract_text_by_types(self, segment_boxes: list[dict], token_types: list[TokenType]) -> dict:
        pass

    @abstractmethod
    def extract_all_text(self, segment_boxes: list[dict]) -> dict:
        pass
