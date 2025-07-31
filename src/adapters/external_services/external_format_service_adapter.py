from typing import List
from domain.PdfImages import PdfImages
from domain.PdfSegment import PdfSegment
from ports.services.external_format_service import ExternalFormatService
from adapters.external_services.extraction_formats.extract_table_formats import extract_table_format
from adapters.external_services.extraction_formats.extract_formula_formats import extract_formula_format


class ExternalFormatServiceAdapter(ExternalFormatService):
    def extract_table_formats(self, pdf_images: PdfImages, segments: List[PdfSegment], extraction_format: str) -> None:
        extract_table_format(pdf_images, segments, extraction_format)

    def extract_formula_formats(self, pdf_images: PdfImages, segments: List[PdfSegment]) -> None:
        extract_formula_format(pdf_images, segments)
