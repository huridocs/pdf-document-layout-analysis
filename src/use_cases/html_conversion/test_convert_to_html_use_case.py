from unittest import TestCase
from ports.services.html_conversion_service import HtmlConversionService
from ports.services.pdf_analysis_service import PDFAnalysisService
from use_cases.html_conversion.convert_to_html_use_case import ConvertToHtmlUseCase


class FailingPDFAnalysisService(PDFAnalysisService):
    def analyze_pdf_layout(self, pdf_content, xml_filename="", parse_tables_and_math=False, keep_pdf=False):
        raise AssertionError("analyze_pdf_layout should not be called when segment_boxes is provided")

    def analyze_pdf_layout_fast(self, pdf_content, xml_filename="", parse_tables_and_math=False, keep_pdf=False):
        raise AssertionError("analyze_pdf_layout_fast should not be called when segment_boxes is provided")


class StubPDFAnalysisService(PDFAnalysisService):
    def __init__(self, segments):
        self.segments = segments
        self.calls = []

    def analyze_pdf_layout(self, pdf_content, xml_filename="", parse_tables_and_math=False, keep_pdf=False):
        self.calls.append("analyze_pdf_layout")
        return self.segments

    def analyze_pdf_layout_fast(self, pdf_content, xml_filename="", parse_tables_and_math=False, keep_pdf=False):
        self.calls.append("analyze_pdf_layout_fast")
        return self.segments


class RecordingHtmlConversionService(HtmlConversionService):
    def __init__(self):
        self.received_segments = None

    def convert_to_html(
        self,
        pdf_content,
        segments,
        extract_toc=False,
        dpi=120,
        output_file=None,
        target_languages=None,
        translation_model="gpt-oss",
    ):
        self.received_segments = segments
        return "converted"


class TestConvertToHtmlUseCase(TestCase):
    def test_segment_boxes_skips_analysis(self):
        html_conversion_service = RecordingHtmlConversionService()
        use_case = ConvertToHtmlUseCase(FailingPDFAnalysisService(), html_conversion_service)

        segment_boxes = [
            {
                "left": 1,
                "top": 2,
                "width": 3,
                "height": 4,
                "page_number": 1,
                "page_width": 10,
                "page_height": 20,
                "text": "hi",
                "type": "Text",
            }
        ]

        result = use_case.execute(b"pdf-bytes", segment_boxes=segment_boxes)

        self.assertEqual("converted", result)
        self.assertEqual(1, len(html_conversion_service.received_segments))
        self.assertEqual("hi", html_conversion_service.received_segments[0].text)

    def test_without_segment_boxes_runs_analysis(self):
        pdf_analysis_service = StubPDFAnalysisService(
            [
                {
                    "left": 0,
                    "top": 0,
                    "width": 0,
                    "height": 0,
                    "page_number": 1,
                    "page_width": 0,
                    "page_height": 0,
                    "type": "Text",
                }
            ]
        )
        html_conversion_service = RecordingHtmlConversionService()
        use_case = ConvertToHtmlUseCase(pdf_analysis_service, html_conversion_service)

        use_case.execute(b"pdf-bytes")

        self.assertEqual(["analyze_pdf_layout"], pdf_analysis_service.calls)
        self.assertEqual(1, len(html_conversion_service.received_segments))

    def test_without_segment_boxes_fast_mode_uses_fast_analysis(self):
        pdf_analysis_service = StubPDFAnalysisService([])
        use_case = ConvertToHtmlUseCase(pdf_analysis_service, RecordingHtmlConversionService())

        use_case.execute(b"pdf-bytes", use_fast_mode=True)

        self.assertEqual(["analyze_pdf_layout_fast"], pdf_analysis_service.calls)
