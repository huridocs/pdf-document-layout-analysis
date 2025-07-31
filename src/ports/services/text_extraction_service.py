from abc import ABC, abstractmethod
from typing import List
from pdf_token_type_labels import TokenType


class TextExtractionService(ABC):
    @abstractmethod
    def extract_text_by_types(self, segment_boxes: List[dict], token_types: List[TokenType]) -> dict:
        pass

    @abstractmethod
    def extract_all_text(self, segment_boxes: List[dict]) -> dict:
        pass
