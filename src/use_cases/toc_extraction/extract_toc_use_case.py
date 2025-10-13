from fastapi import UploadFile
from ports.services.pdf_analysis_service import PDFAnalysisService
from ports.services.toc_service import TOCService


class ExtractTOCUseCase:
    def __init__(self, pdf_analysis_service: PDFAnalysisService, toc_service: TOCService):
        self.pdf_analysis_service = pdf_analysis_service
        self.toc_service = toc_service

    def execute(self, file: UploadFile, use_fast_mode: bool = False) -> list[dict]:
        file_content = file.file.read()

        if use_fast_mode:
            segment_boxes = self.pdf_analysis_service.analyze_pdf_layout_fast(file_content)
        else:
            segment_boxes = self.pdf_analysis_service.analyze_pdf_layout(file_content, "")

        return self.toc_service.extract_table_of_contents(file_content, segment_boxes)

    def execute_uwazi_compatible(self, file: UploadFile) -> list[dict]:
        toc_items = self.execute(file, use_fast_mode=True)
        return self.toc_service.format_toc_for_uwazi(toc_items)

    def execute_with_segments(self, xml_content: bytes, segment_boxes: list[dict]) -> list[dict]:
        toc_items = self.toc_service.extract_table_of_contents_from_xml(xml_content, segment_boxes)
        return self.toc_service.format_toc_for_uwazi(toc_items)
