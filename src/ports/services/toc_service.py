from abc import ABC, abstractmethod
from typing import List, AnyStr


class TOCService(ABC):
    @abstractmethod
    def extract_table_of_contents(self, pdf_content: AnyStr, segment_boxes: List[dict]) -> List[dict]:
        pass

    @abstractmethod
    def format_toc_for_uwazi(self, toc_items: List[dict]) -> List[dict]:
        pass
