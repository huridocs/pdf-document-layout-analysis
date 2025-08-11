from abc import ABC, abstractmethod
from domain.PdfImages import PdfImages
from domain.PdfSegment import PdfSegment


class FormatConversionService(ABC):

    @abstractmethod
    def convert_table_to_html(self, pdf_images: PdfImages, segments: list[PdfSegment]) -> None:
        pass

    @abstractmethod
    def convert_formula_to_latex(self, pdf_images: PdfImages, segments: list[PdfSegment]) -> None:
        pass
