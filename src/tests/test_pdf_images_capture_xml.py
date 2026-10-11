import subprocess
import tempfile
import uuid
from pathlib import Path
from unittest import TestCase

from lxml import etree
from pdf_features import PdfFeatures

from configuration import IMAGES_ROOT_PATH, ROOT_PATH
from domain.PdfImages import PdfImages


class TestPdfImagesCaptureXml(TestCase):
    def _write_temp_pdf(self, name: str) -> Path:
        pdf_path = Path(tempfile.gettempdir(), f"{uuid.uuid1()}.pdf")
        pdf_path.write_bytes(Path(ROOT_PATH, "test_pdfs", name).read_bytes())
        return pdf_path

    def test_capture_xml_matches_disk_output(self):
        pdf_path = self._write_temp_pdf("regular.pdf")
        disk_xml_path = Path(tempfile.gettempdir(), f"{uuid.uuid1()}.xml")
        try:
            _, xml_content = PdfImages.from_pdf_path_capture_xml(pdf_path)
            subprocess.run(
                ["pdftohtml", "-nodrm", "-i", "-xml", "-zoom", "1.0", str(pdf_path), str(disk_xml_path)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            self.assertEqual(disk_xml_path.read_text(), xml_content)
        finally:
            pdf_path.unlink(missing_ok=True)
            disk_xml_path.unlink(missing_ok=True)

    def test_capture_xml_features_parity(self):
        pdf_path = self._write_temp_pdf("regular.pdf")
        try:
            pdf_images, xml_content = PdfImages.from_pdf_path_capture_xml(pdf_path)

            self.assertTrue(xml_content.startswith("<?xml"))
            self.assertIn("<pdf2xml", xml_content)
            self.assertEqual(2, len(pdf_images.pdf_features.pages))
            self.assertEqual(39, len(pdf_images.pdf_features.pages[0].tokens))
            self.assertEqual(pdf_path.stem, pdf_images.pdf_features.file_name)
        finally:
            pdf_path.unlink(missing_ok=True)

    def test_capture_xml_hidden_fallback(self):
        pdf_path = self._write_temp_pdf("ocr_pdf.pdf")
        try:
            self.assertFalse(PdfImages._xml_has_text(PdfImages._pdftohtml_stdout(pdf_path, hidden=False)))

            _, xml_content = PdfImages.from_pdf_path_capture_xml(pdf_path)

            self.assertTrue(xml_content.startswith("<?xml"))
            self.assertIn("<pdf2xml", xml_content)
        finally:
            pdf_path.unlink(missing_ok=True)

    def test_capture_xml_non_utf8_font_name(self):
        pdf_path = self._write_temp_pdf("korean.pdf")
        disk_xml_path = Path(tempfile.gettempdir(), f"{uuid.uuid1()}.xml")
        pdf_images = None
        try:
            pdf_images, xml_content = PdfImages.from_pdf_path_capture_xml(pdf_path)
            disk_features = PdfFeatures.from_pdf_path(pdf_path, disk_xml_path)

            etree.fromstring(xml_content.encode("utf-8"))
            self.assertEqual(
                [[token.content for token in page.tokens] for page in disk_features.pages],
                [[token.content for token in page.tokens] for page in pdf_images.pdf_features.pages],
            )
        finally:
            pdf_path.unlink(missing_ok=True)
            disk_xml_path.unlink(missing_ok=True)
            if pdf_images:
                for index in range(len(pdf_images.pdf_images)):
                    Path(IMAGES_ROOT_PATH, f"{pdf_path.stem}_{index}.jpg").unlink(missing_ok=True)
