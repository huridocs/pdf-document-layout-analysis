from unittest import TestCase

from ports.services.pdf_analysis_service import PDFAnalysisService
from use_cases.pdf_analysis.analyze_pdf_use_case import AnalyzePDFUseCase


class StubPDFAnalysisService(PDFAnalysisService):
    def __init__(self, segments, xml):
        self.segments = segments
        self.xml = xml
        self.calls = []

    def analyze_pdf_layout(self, pdf_content, xml_filename="", parse_tables_and_math=False, keep_pdf=False):
        raise AssertionError("analyze_pdf_layout should not be called")

    def analyze_pdf_layout_fast(self, pdf_content, xml_filename="", parse_tables_and_math=False, keep_pdf=False):
        raise AssertionError("analyze_pdf_layout_fast should not be called")

    def analyze_pdf_layout_with_xml(self, pdf_content):
        self.calls.append("analyze_pdf_layout_with_xml")
        return self.segments, self.xml

    def analyze_pdf_layout_fast_with_xml(self, pdf_content):
        self.calls.append("analyze_pdf_layout_fast_with_xml")
        return self.segments, self.xml


class TestAnalyzePDFUseCaseWithXml(TestCase):
    def _build_use_case(self):
        segments = [{"text": "hello", "page_number": 1}]
        pdf_analysis_service = StubPDFAnalysisService(segments, "<pdf2xml/>")
        return AnalyzePDFUseCase(pdf_analysis_service=pdf_analysis_service, ml_model_service=None), pdf_analysis_service

    def test_execute_with_xml_dispatches_vgt(self):
        use_case, pdf_analysis_service = self._build_use_case()

        result = use_case.execute_with_xml(b"content", use_fast_mode=False)

        self.assertEqual(([{"text": "hello", "page_number": 1}], "<pdf2xml/>"), result)
        self.assertEqual(["analyze_pdf_layout_with_xml"], pdf_analysis_service.calls)

    def test_execute_with_xml_dispatches_fast(self):
        use_case, pdf_analysis_service = self._build_use_case()

        result = use_case.execute_with_xml(b"content", use_fast_mode=True)

        self.assertEqual(([{"text": "hello", "page_number": 1}], "<pdf2xml/>"), result)
        self.assertEqual(["analyze_pdf_layout_fast_with_xml"], pdf_analysis_service.calls)
