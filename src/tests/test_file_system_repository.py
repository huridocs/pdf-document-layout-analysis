import tempfile
import uuid
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch
from shutil import rmtree

from file_utils import sanitize_filename
from adapters.storage.file_system_repository import FileSystemRepository


class TestSanitizeFilename(TestCase):
    def test_strips_parent_segments(self):
        self.assertEqual("bar.pdf", sanitize_filename("../../bar.pdf"))
        self.assertEqual("b.pdf", sanitize_filename("a/../b.pdf"))

    def test_strips_leading_absolute_parts(self):
        self.assertEqual("bar.pdf", sanitize_filename("/etc/bar.pdf"))

    def test_strips_windows_style_parts(self):
        self.assertEqual("bar.pdf", sanitize_filename("C:\\bar.pdf"))
        self.assertEqual("bar.pdf", sanitize_filename("..\\bar.pdf"))

    def test_plain_basename_is_kept(self):
        self.assertEqual("bar.pdf", sanitize_filename("bar.pdf"))

    def test_unsafe_names_fall_back_to_generated_name(self):
        for unsafe_name in ("", None, ".", "..", ".//..", "/", "//", "../../"):
            name = sanitize_filename(unsafe_name)
            self.assertTrue(name)
            self.assertNotIn("/", name)
            self.assertNotIn("..", name)


class TestSavePdfToDirectory(TestCase):
    def setUp(self):
        self.directory = Path(tempfile.gettempdir(), f"pdf_dla_test_{uuid.uuid1()}")
        self.namespace = "sync_pdfs"
        self.repository = FileSystemRepository()

    def tearDown(self):
        rmtree(self.directory, ignore_errors=True)

    def test_plain_basename_stays_in_namespace(self):
        path = self.repository.save_pdf_to_directory(b"content", "source.pdf", self.directory, self.namespace)

        self.assertEqual(b"content", path.read_bytes())
        self.assertTrue(path.is_relative_to(Path(self.directory, self.namespace)))

    def test_parent_segment_filename_stays_in_namespace(self):
        path = self.repository.save_pdf_to_directory(b"content", "../source.pdf", self.directory, self.namespace)

        namespace = Path(self.directory, self.namespace)
        self.assertTrue(path.is_relative_to(namespace))
        self.assertEqual(b"content", path.read_bytes())
        self.assertEqual(["source.pdf"], [item.name for item in namespace.rglob("*.pdf") if "generated" not in item.name])
        self.assertFalse((self.directory / "source.pdf").exists())

    def test_absolute_filename_stays_in_namespace(self):
        path = self.repository.save_pdf_to_directory(
            b"content", "/tmp/pdf_dla_abs/source.pdf", self.directory, self.namespace
        )

        namespace = Path(self.directory, self.namespace)
        self.assertTrue(path.is_relative_to(namespace))
        self.assertEqual(b"content", path.read_bytes())
        self.assertFalse(Path("/tmp/pdf_dla_abs/source.pdf").exists())

    def test_windows_style_filename_stays_in_namespace(self):
        path = self.repository.save_pdf_to_directory(b"content", "..\\source.pdf", self.directory, self.namespace)

        self.assertTrue(path.is_relative_to(Path(self.directory, self.namespace)))
        self.assertEqual(b"content", path.read_bytes())

    def test_empty_filename_generates_uuid_name(self):
        path = self.repository.save_pdf_to_directory(b"content", "", self.directory, self.namespace)

        self.assertTrue(path.is_relative_to(Path(self.directory, self.namespace)))
        self.assertEqual(b"content", path.read_bytes())


class TestXmlMethodsStaysInXmlsPath(TestCase):
    def setUp(self):
        self.xmls_path = Path(tempfile.gettempdir(), f"pdf_dla_test_{uuid.uuid1()}")
        self.xmls_patcher = patch("adapters.storage.file_system_repository.XMLS_PATH", self.xmls_path)
        self.xmls_patcher.start()
        self.repository = FileSystemRepository()

    def tearDown(self):
        self.xmls_patcher.stop()
        rmtree(self.xmls_path, ignore_errors=True)

    def test_save_xml_with_parent_segment_stays_in_xmls_path(self):
        self.repository.save_xml("<xml/>", "../evil")

        self.assertEqual(["evil.xml"], [item.name for item in self.xmls_path.rglob("*.xml")])
        self.assertEqual("<xml/>", (self.xmls_path / "evil.xml").read_text())
        self.assertFalse((self.xmls_path.parent / "evil.xml").exists())

    def test_save_xml_with_absolute_filename_stays_in_xmls_path(self):
        self.repository.save_xml("<xml/>", "/tmp/pdf_dla_abs/evil")

        self.assertFalse(Path("/tmp/pdf_dla_abs/evil.xml").exists())
        self.assertEqual(["evil.xml"], [item.name for item in self.xmls_path.rglob("*.xml")])

    def test_save_xml_with_windows_style_filename_stays_in_xmls_path(self):
        self.repository.save_xml("<xml/>", "..\\evil")

        self.assertEqual(["evil.xml"], [item.name for item in self.xmls_path.rglob("*.xml")])

    @staticmethod
    def _traversal_filenames():
        return ["../evil", "..\\evil", "/tmp/pdf_dla_abs/evil", ".", "..", ""]

    def test_get_xml_only_reads_inside_xmls_path(self):
        self.repository.save_xml("<xml/>", "safe.xml")

        for filename in self._traversal_filenames():
            with self.assertRaises(FileNotFoundError):
                self.repository.get_xml(filename)

        self.assertEqual("<xml/>", self.repository.get_xml("safe"))

    def test_get_xml_and_delete_only_inside_xmls_path(self):
        self.repository.save_xml("<xml/>", "safe.xml")

        for filename in self._traversal_filenames():
            with self.assertRaises(FileNotFoundError):
                self.repository.get_xml_and_delete(filename)

        self.assertEqual("<xml/>", self.repository.get_xml_and_delete("safe"))
        self.assertFalse((self.xmls_path / "safe.xml").exists())

    def test_save_pdf_with_parent_segment_stays_in_temp_dir(self):
        path = self.repository.save_pdf(b"content", "../../evil")
        self.addCleanup(path.unlink, missing_ok=True)

        self.assertEqual("evil.pdf", path.name)
        self.assertEqual(Path(tempfile.gettempdir()), path.parent)
        self.assertEqual(b"content", path.read_bytes())
