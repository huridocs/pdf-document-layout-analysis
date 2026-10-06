import tempfile
import uuid
from pathlib import Path
from unittest import TestCase
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
