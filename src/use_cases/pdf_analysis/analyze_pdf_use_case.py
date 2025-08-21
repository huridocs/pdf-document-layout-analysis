from typing import AnyStr
from ports.services.pdf_analysis_service import PDFAnalysisService
from ports.services.ml_model_service import MLModelService


class AnalyzePDFUseCase:
    def __init__(
        self,
        pdf_analysis_service: PDFAnalysisService,
        ml_model_service: MLModelService,
    ):
        self.pdf_analysis_service = pdf_analysis_service
        self.ml_model_service = ml_model_service

    def execute(
        self,
        pdf_content: AnyStr,
        xml_filename: str = "",
        parse_tables_and_math: bool = False,
        use_fast_mode: bool = False,
        keep_pdf: bool = False,
    ) -> list[dict]:
        if use_fast_mode:
            return self.pdf_analysis_service.analyze_pdf_layout_fast(
                pdf_content, xml_filename, parse_tables_and_math, keep_pdf
            )
        else:
            return self.pdf_analysis_service.analyze_pdf_layout(pdf_content, xml_filename, parse_tables_and_math, keep_pdf)

    def execute_and_save_xml(self, pdf_content: AnyStr, xml_filename: str, use_fast_mode: bool = False) -> list[dict]:
        result = self.execute(pdf_content, xml_filename, False, use_fast_mode, keep_pdf=False)
        return result
