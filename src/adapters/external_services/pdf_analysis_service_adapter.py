from typing import AnyStr, List
from domain.PdfImages import PdfImages
from domain.SegmentBox import SegmentBox
from ports.services.pdf_analysis_service import PDFAnalysisService
from ports.services.ml_model_service import MLModelService
from ports.services.external_format_service import ExternalFormatService
from ports.repositories.file_repository import FileRepository
from configuration import service_logger


class PDFAnalysisServiceAdapter(PDFAnalysisService):
    def __init__(
        self,
        vgt_model_service: MLModelService,
        fast_model_service: MLModelService,
        external_format_service: ExternalFormatService,
        file_repository: FileRepository,
    ):
        self.vgt_model_service = vgt_model_service
        self.fast_model_service = fast_model_service
        self.external_format_service = external_format_service
        self.file_repository = file_repository

    def analyze_pdf_layout(
        self, pdf_content: AnyStr, xml_filename: str = "", extraction_format: str = "", keep_pdf: bool = False
    ) -> List[dict]:
        pdf_path = self.file_repository.save_pdf(pdf_content)
        service_logger.info("Creating PDF images")

        pdf_images_list: List[PdfImages] = [PdfImages.from_pdf_path(pdf_path, "", xml_filename)]

        predicted_segments = self.vgt_model_service.predict_document_layout(pdf_images_list)

        self.external_format_service.extract_formula_formats(pdf_images_list[0], predicted_segments)
        if extraction_format:
            self.external_format_service.extract_table_formats(pdf_images_list[0], predicted_segments, extraction_format)

        if not keep_pdf:
            self.file_repository.delete_file(pdf_path)

        return [
            SegmentBox.from_pdf_segment(pdf_segment, pdf_images_list[0].pdf_features.pages).to_dict()
            for pdf_segment in predicted_segments
        ]

    def analyze_pdf_layout_fast(
        self, pdf_content: AnyStr, xml_filename: str = "", extraction_format: str = "", keep_pdf: bool = False
    ) -> List[dict]:
        pdf_path = self.file_repository.save_pdf(pdf_content)
        service_logger.info("Creating PDF images for fast analysis")

        pdf_images_list: List[PdfImages] = [PdfImages.from_pdf_path(pdf_path, "", xml_filename)]

        predicted_segments = self.fast_model_service.predict_layout_fast(pdf_images_list)

        if extraction_format:
            self.external_format_service.extract_table_formats(pdf_images_list[0], predicted_segments, extraction_format)

        if not keep_pdf:
            self.file_repository.delete_file(pdf_path)

        return [
            SegmentBox.from_pdf_segment(pdf_segment, pdf_images_list[0].pdf_features.pages).to_dict()
            for pdf_segment in predicted_segments
        ]
