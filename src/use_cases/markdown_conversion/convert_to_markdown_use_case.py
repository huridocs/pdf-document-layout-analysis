from typing import Optional, Union
from starlette.responses import Response
from ports.services.markdown_conversion_service import MarkdownConversionService
from ports.services.pdf_analysis_service import PDFAnalysisService
from domain.SegmentBox import SegmentBox


class ConvertToMarkdownUseCase:
    def __init__(
        self,
        pdf_analysis_service: PDFAnalysisService,
        markdown_conversion_service: MarkdownConversionService,
    ):
        self.pdf_analysis_service = pdf_analysis_service
        self.markdown_conversion_service = markdown_conversion_service

    def execute(
        self,
        pdf_content: bytes,
        use_fast_mode: bool = False,
        extract_toc: bool = False,
        dpi: int = 120,
        output_file: Optional[str] = None,
        target_languages: Optional[list[str]] = None,
        translation_model: str = "gpt-oss",
    ) -> Union[str, Response]:
        if use_fast_mode:
            analysis_result = self.pdf_analysis_service.analyze_pdf_layout_fast(pdf_content, "", True, False)
        else:
            analysis_result = self.pdf_analysis_service.analyze_pdf_layout(pdf_content, "", True, False)

        segments: list[SegmentBox] = []
        for item in analysis_result:
            if isinstance(item, dict):
                segment = SegmentBox(
                    left=item.get("left", 0),
                    top=item.get("top", 0),
                    width=item.get("width", 0),
                    height=item.get("height", 0),
                    page_number=item.get("page_number", 1),
                    page_width=item.get("page_width", 0),
                    page_height=item.get("page_height", 0),
                    text=item.get("text", ""),
                    type=item.get("type", "TEXT"),
                )
                segments.append(segment)
            elif isinstance(item, SegmentBox):
                segments.append(item)

        return self.markdown_conversion_service.convert_to_markdown(
            pdf_content, segments, extract_toc, dpi, output_file, target_languages, translation_model
        )
