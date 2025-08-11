from domain.PdfImages import PdfImages
from domain.PdfSegment import PdfSegment
from ports.services.format_conversion_service import FormatConversionService
from adapters.infrastructure.format_converters.convert_table_to_html import extract_table_format
from adapters.infrastructure.format_converters.convert_formula_to_latex import extract_formula_format


class FormatConversionServiceAdapter(FormatConversionService):
    def convert_table_to_html(self, pdf_images: PdfImages, segments: list[PdfSegment]) -> None:
        extract_table_format(pdf_images, segments)

    def convert_formula_to_latex(self, pdf_images: PdfImages, segments: list[PdfSegment]) -> None:
        extract_formula_format(pdf_images, segments)
