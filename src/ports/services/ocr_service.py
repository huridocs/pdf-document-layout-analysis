from abc import ABC, abstractmethod
from pathlib import Path


class OCRService(ABC):
    @abstractmethod
    def process_pdf_ocr(self, filename: str, namespace: str, language: str = "en") -> Path:
        pass

    @abstractmethod
    def get_supported_languages(self) -> list[str]:
        pass
