from fastapi import UploadFile
from starlette.responses import FileResponse
from ports.services.pdf_analysis_service import PDFAnalysisService
from ports.services.visualization_service import VisualizationService
from glob import glob
from os.path import getctime, join
from tempfile import gettempdir
from pathlib import Path


class CreateVisualizationUseCase:
    def __init__(self, pdf_analysis_service: PDFAnalysisService, visualization_service: VisualizationService):
        self.pdf_analysis_service = pdf_analysis_service
        self.visualization_service = visualization_service

    def execute(self, file: UploadFile, use_fast_mode: bool = False) -> FileResponse:
        file_content = file.file.read()

        if use_fast_mode:
            segment_boxes = self.pdf_analysis_service.analyze_pdf_layout_fast(file_content, "", "", True)
        else:
            segment_boxes = self.pdf_analysis_service.analyze_pdf_layout(file_content, "", "", True)

        pdf_path = Path(max(glob(join(gettempdir(), "*.pdf")), key=getctime))
        visualization_path = self.visualization_service.create_pdf_visualization(pdf_path, segment_boxes)

        return self.visualization_service.get_visualization_response(visualization_path)
