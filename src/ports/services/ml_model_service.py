from abc import ABC, abstractmethod
from typing import List
from domain.PdfImages import PdfImages
from domain.PdfSegment import PdfSegment


class MLModelService(ABC):
    @abstractmethod
    def predict_document_layout(self, pdf_images: List[PdfImages]) -> List[PdfSegment]:
        pass

    @abstractmethod
    def predict_layout_fast(self, pdf_images: List[PdfImages]) -> List[PdfSegment]:
        pass
