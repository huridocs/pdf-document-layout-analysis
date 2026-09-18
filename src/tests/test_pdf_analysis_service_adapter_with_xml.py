import tempfile
from pathlib import Path
from unittest import TestCase

from adapters.infrastructure.pdf_analysis_service_adapter import PDFAnalysisServiceAdapter
from adapters.storage.file_system_repository import FileSystemRepository
from configuration import IMAGES_ROOT_PATH, ROOT_PATH, XMLS_PATH
from domain.PdfSegment import PdfSegment
from pdf_features import Rectangle
from pdf_token_type_labels import TokenType


class FakeModelService:
    def __init__(self):
        self.predict_calls = 0

    def predict_document_layout(self, pdf_images):
        self.predict_calls += 1
        return [PdfSegment(1, Rectangle.from_width_height(0, 0, 10, 10), "hello", TokenType.TEXT, "")]

    def predict_layout_fast(self, pdf_images):
        self.predict_calls += 1
        return [PdfSegment(1, Rectangle.from_width_height(0, 0, 10, 10), "hello", TokenType.TEXT, "")]


class TestPDFAnalysisServiceAdapterWithXml(TestCase):
    def setUp(self):
        self.images_before = {path.name for path in IMAGES_ROOT_PATH.glob("*")} if IMAGES_ROOT_PATH.exists() else set()

    def tearDown(self):
        if not IMAGES_ROOT_PATH.exists():
            return
        for path in IMAGES_ROOT_PATH.glob("*"):
            if path.name not in self.images_before:
                path.unlink(missing_ok=True)

    def _build_adapter(self):
        model_service = FakeModelService()
        adapter = PDFAnalysisServiceAdapter(
            vgt_model_service=model_service,
            fast_model_service=model_service,
            format_conversion_service=None,
            file_repository=FileSystemRepository(),
        )
        return adapter, model_service

    def _xml_file_names(self):
        return {path.name for path in XMLS_PATH.glob("*.xml")} if XMLS_PATH.exists() else set()

    def _temp_pdf_names(self):
        return {path.name for path in Path(tempfile.gettempdir()).glob("*.pdf")}

    def _assert_with_xml_result(self, method_name):
        adapter, model_service = self._build_adapter()
        pdf_content = Path(ROOT_PATH, "test_pdfs", "regular.pdf").read_bytes()
        xml_files_before = self._xml_file_names()
        temp_pdfs_before = self._temp_pdf_names()

        segments, xml_content = getattr(adapter, method_name)(pdf_content)

        self.assertEqual(1, model_service.predict_calls)
        self.assertIsInstance(segments, list)
        self.assertIsInstance(xml_content, str)
        self.assertEqual(1, len(segments))
        self.assertEqual("hello", segments[0]["text"])
        self.assertEqual(1, segments[0]["page_number"])
        self.assertTrue(xml_content.startswith("<?xml"))
        self.assertIn("<pdf2xml", xml_content)
        self.assertEqual(xml_files_before, self._xml_file_names())
        self.assertEqual(temp_pdfs_before, self._temp_pdf_names())

    def test_analyze_pdf_layout_with_xml(self):
        self._assert_with_xml_result("analyze_pdf_layout_with_xml")

    def test_analyze_pdf_layout_fast_with_xml(self):
        self._assert_with_xml_result("analyze_pdf_layout_fast_with_xml")
