from abc import ABC, abstractmethod
from typing import AnyStr


class TOCService(ABC):
    @abstractmethod
    def extract_table_of_contents(self, pdf_content: AnyStr, segment_boxes: list[dict]) -> list[dict]:
        pass

    @abstractmethod
    def extract_table_of_contents_from_xml(self, xml_content: AnyStr, segment_boxes: list[dict]) -> list[dict]:
        pass

    @abstractmethod
    def format_toc_for_uwazi(self, toc_items: list[dict]) -> list[dict]:
        pass
