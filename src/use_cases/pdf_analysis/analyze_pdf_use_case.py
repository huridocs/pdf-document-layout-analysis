from typing import AnyStr, List
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
        extraction_format: str = "",
        use_fast_mode: bool = False,
        keep_pdf: bool = False,
    ) -> List[dict]:
        if use_fast_mode:
            return self.pdf_analysis_service.analyze_pdf_layout_fast(pdf_content, xml_filename, extraction_format, keep_pdf)
        else:
            return self.pdf_analysis_service.analyze_pdf_layout(pdf_content, xml_filename, extraction_format, keep_pdf)

    def execute_and_save_xml(self, pdf_content: AnyStr, xml_filename: str, use_fast_mode: bool = False) -> List[dict]:
        result = self.execute(pdf_content, xml_filename, "", use_fast_mode, keep_pdf=False)
        return result
