from abc import ABC, abstractmethod
from typing import AnyStr, List


class PDFAnalysisService(ABC):
    @abstractmethod
    def analyze_pdf_layout(
        self, pdf_content: AnyStr, xml_filename: str = "", ocr_tables: bool = False, keep_pdf: bool = False
    ) -> List[dict]:
        pass

    @abstractmethod
    def analyze_pdf_layout_fast(
        self, pdf_content: AnyStr, xml_filename: str = "", ocr_tables: bool = False, keep_pdf: bool = False
    ) -> List[dict]:
        pass
