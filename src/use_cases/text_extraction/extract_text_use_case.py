from fastapi import UploadFile
from pdf_token_type_labels import TokenType
from ports.services.pdf_analysis_service import PDFAnalysisService
from ports.services.text_extraction_service import TextExtractionService


class ExtractTextUseCase:
    def __init__(self, pdf_analysis_service: PDFAnalysisService, text_extraction_service: TextExtractionService):
        self.pdf_analysis_service = pdf_analysis_service
        self.text_extraction_service = text_extraction_service

    def execute(self, file: UploadFile, use_fast_mode: bool = False, types: str = "all") -> dict:
        file_content = file.file.read()

        if types == "all":
            token_types: list[TokenType] = [t for t in TokenType]
        else:
            token_types = list(set([TokenType.from_text(t.strip().replace(" ", "_")) for t in types.split(",")]))

        if use_fast_mode:
            segment_boxes = self.pdf_analysis_service.analyze_pdf_layout_fast(file_content)
        else:
            segment_boxes = self.pdf_analysis_service.analyze_pdf_layout(file_content, "")

        return self.text_extraction_service.extract_text_by_types(segment_boxes, token_types)
