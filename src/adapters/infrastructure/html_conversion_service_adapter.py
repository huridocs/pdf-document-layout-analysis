from typing import Optional, Union
from starlette.responses import Response

from domain.SegmentBox import SegmentBox
from ports.services.html_conversion_service import HtmlConversionService
from adapters.infrastructure.markup_conversion.pdf_to_markup_service_adapter import PdfToMarkupServiceAdapter
from adapters.infrastructure.markup_conversion.OutputFormat import OutputFormat


class HtmlConversionServiceAdapter(HtmlConversionService, PdfToMarkupServiceAdapter):

    def __init__(self):
        PdfToMarkupServiceAdapter.__init__(self, OutputFormat.HTML)

    def convert_to_html(
        self,
        pdf_content: bytes,
        segments: list[SegmentBox],
        extract_toc: bool = False,
        dpi: int = 120,
        output_file: Optional[str] = None,
        target_languages: Optional[list[str]] = None,
        translation_model: str = "gpt-oss",
    ) -> Union[str, Response]:
        return self.convert_to_format(
            pdf_content, segments, extract_toc, dpi, output_file, target_languages, translation_model
        )
