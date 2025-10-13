from typing import AnyStr
from domain.PdfImages import PdfImages
from domain.SegmentBox import SegmentBox
from ports.services.pdf_analysis_service import PDFAnalysisService
from ports.services.ml_model_service import MLModelService
from ports.services.format_conversion_service import FormatConversionService
from ports.repositories.file_repository import FileRepository
from configuration import service_logger


class PDFAnalysisServiceAdapter(PDFAnalysisService):
    def __init__(
        self,
        vgt_model_service: MLModelService,
        fast_model_service: MLModelService,
        format_conversion_service: FormatConversionService,
        file_repository: FileRepository,
    ):
        self.vgt_model_service = vgt_model_service
        self.fast_model_service = fast_model_service
        self.format_conversion_service = format_conversion_service
        self.file_repository = file_repository

    def analyze_pdf_layout(
        self, pdf_content: AnyStr, xml_filename: str = "", parse_tables_and_math: bool = False, keep_pdf: bool = False
    ) -> list[dict]:
        pdf_path = self.file_repository.save_pdf(pdf_content)
        service_logger.info("Creating PDF images")

        pdf_images_list: list[PdfImages] = [PdfImages.from_pdf_path(pdf_path, "", xml_filename)]

        predicted_segments = self.vgt_model_service.predict_document_layout(pdf_images_list)

        if predicted_segments:
            service_logger.info(f"Predicted {len(predicted_segments)} segments")

        if parse_tables_and_math:
            service_logger.info("Parsing tables and formulas")
            pdf_images_200_dpi = PdfImages.from_pdf_path(pdf_path, "", xml_filename, dpi=200)
            self.format_conversion_service.convert_formula_to_latex(pdf_images_200_dpi, predicted_segments)
            self.format_conversion_service.convert_table_to_html(pdf_images_200_dpi, predicted_segments)

        if not keep_pdf:
            self.file_repository.delete_file(pdf_path)

        return [
            SegmentBox.from_pdf_segment(pdf_segment, pdf_images_list[0].pdf_features.pages).to_dict()
            for pdf_segment in predicted_segments
        ]

    def analyze_pdf_layout_fast(
        self, pdf_content: AnyStr, xml_filename: str = "", parse_tables_and_math: bool = False, keep_pdf: bool = False
    ) -> list[dict]:
        pdf_path = self.file_repository.save_pdf(pdf_content)
        service_logger.info("Creating PDF images for fast analysis")

        pdf_images_list: list[PdfImages] = [PdfImages.from_pdf_path(pdf_path, "", xml_filename)]

        predicted_segments = self.fast_model_service.predict_layout_fast(pdf_images_list)

        if parse_tables_and_math:
            pdf_images_200_dpi = PdfImages.from_pdf_path(pdf_path, "", xml_filename, dpi=200)
            self.format_conversion_service.convert_formula_to_latex(pdf_images_200_dpi, predicted_segments)
            self.format_conversion_service.convert_table_to_html(pdf_images_list[0], predicted_segments)

        if not keep_pdf:
            self.file_repository.delete_file(pdf_path)

        return [
            SegmentBox.from_pdf_segment(pdf_segment, pdf_images_list[0].pdf_features.pages).to_dict()
            for pdf_segment in predicted_segments
        ]
