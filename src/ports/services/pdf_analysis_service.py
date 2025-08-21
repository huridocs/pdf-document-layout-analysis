from abc import ABC, abstractmethod
from typing import AnyStr


class PDFAnalysisService(ABC):
    @abstractmethod
    def analyze_pdf_layout(
        self, pdf_content: AnyStr, xml_filename: str = "", parse_tables_and_math: bool = False, keep_pdf: bool = False
    ) -> list[dict]:
        pass

    @abstractmethod
    def analyze_pdf_layout_fast(
        self, pdf_content: AnyStr, xml_filename: str = "", parse_tables_and_math: bool = False, keep_pdf: bool = False
    ) -> list[dict]:
        pass
