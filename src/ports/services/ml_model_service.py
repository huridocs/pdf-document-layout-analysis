from abc import ABC, abstractmethod
from domain.PdfImages import PdfImages
from domain.PdfSegment import PdfSegment


class MLModelService(ABC):
    @abstractmethod
    def predict_document_layout(self, pdf_images: list[PdfImages]) -> list[PdfSegment]:
        pass

    @abstractmethod
    def predict_layout_fast(self, pdf_images: list[PdfImages]) -> list[PdfSegment]:
        pass
