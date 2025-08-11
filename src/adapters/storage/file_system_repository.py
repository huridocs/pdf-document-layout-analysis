import tempfile
import uuid
from pathlib import Path
from typing import AnyStr
from ports.repositories.file_repository import FileRepository
from configuration import XMLS_PATH


class FileSystemRepository(FileRepository):
    def save_pdf(self, content: AnyStr, filename: str = "") -> Path:
        if not filename:
            filename = str(uuid.uuid1())

        pdf_path = Path(tempfile.gettempdir(), f"{filename}.pdf")
        pdf_path.write_bytes(content)
        return pdf_path

    def save_xml(self, content: str, filename: str) -> Path:
        if not filename.endswith(".xml"):
            filename = f"{filename}.xml"

        xml_path = Path(XMLS_PATH, filename)
        xml_path.parent.mkdir(parents=True, exist_ok=True)
        xml_path.write_text(content)
        return xml_path

    def get_xml(self, filename: str) -> str:
        if not filename.endswith(".xml"):
            filename = f"{filename}.xml"

        xml_path = Path(XMLS_PATH, filename)
        if not xml_path.exists():
            raise FileNotFoundError(f"XML file {filename} not found")

        return xml_path.read_text()

    def delete_file(self, filepath: Path) -> None:
        filepath.unlink(missing_ok=True)

    def cleanup_temp_files(self) -> None:
        pass

    def save_pdf_to_directory(self, content: AnyStr, filename: str, directory: Path, namespace: str = "") -> Path:
        if namespace:
            target_path = Path(directory, namespace, filename)
        else:
            target_path = Path(directory, filename)

        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_bytes(content)
        return target_path

    def save_markdown(self, content: str, filepath: Path) -> Path:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text(content, encoding="utf-8")
        return filepath
