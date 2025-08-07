from abc import ABC, abstractmethod
from pathlib import Path
from typing import AnyStr


class FileRepository(ABC):
    @abstractmethod
    def save_pdf(self, content: AnyStr, filename: str = "") -> Path:
        pass

    @abstractmethod
    def save_xml(self, content: str, filename: str) -> Path:
        pass

    @abstractmethod
    def get_xml(self, filename: str) -> str:
        pass

    @abstractmethod
    def delete_file(self, filepath: Path) -> None:
        pass

    @abstractmethod
    def cleanup_temp_files(self) -> None:
        pass

    @abstractmethod
    def save_pdf_to_directory(self, content: AnyStr, filename: str, directory: Path, namespace: str = "") -> Path:
        pass

    @abstractmethod
    def save_markdown(self, content: str, filepath: Path) -> Path:
        pass
