from abc import ABC, abstractmethod
from typing import List
from domain.PdfImages import PdfImages
from domain.PdfSegment import PdfSegment


class ExternalFormatService(ABC):

    @abstractmethod
    def extract_table_formats(self, pdf_images: PdfImages, segments: List[PdfSegment], extraction_format: str) -> None:
        pass

    @abstractmethod
    def extract_formula_formats(self, pdf_images: PdfImages, segments: List[PdfSegment]) -> None:
        pass
