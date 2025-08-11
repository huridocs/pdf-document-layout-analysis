import os
import shutil
import subprocess
from pathlib import Path
from ports.services.ocr_service import OCRService
from configuration import OCR_SOURCE, OCR_OUTPUT, OCR_FAILED
from adapters.infrastructure.ocr.languages import iso_to_tesseract, supported_languages


class OCRServiceAdapter(OCRService):
    def process_pdf_ocr(self, filename: str, namespace: str, language: str = "en") -> Path:
        source_pdf_filepath, processed_pdf_filepath, failed_pdf_filepath = self._get_paths(namespace, filename)
        os.makedirs(processed_pdf_filepath.parent, exist_ok=True)

        result = subprocess.run(
            [
                "ocrmypdf",
                "-l",
                iso_to_tesseract[language],
                source_pdf_filepath,
                processed_pdf_filepath,
                "--force-ocr",
            ]
        )

        if result.returncode == 0:
            return processed_pdf_filepath

        os.makedirs(failed_pdf_filepath.parent, exist_ok=True)
        shutil.move(source_pdf_filepath, failed_pdf_filepath)
        return False

    def get_supported_languages(self) -> list[str]:
        return supported_languages()

    def _get_paths(self, namespace: str, pdf_file_name: str) -> tuple[Path, Path, Path]:
        file_name = "".join(pdf_file_name.split(".")[:-1]) if "." in pdf_file_name else pdf_file_name
        source_pdf_filepath = Path(OCR_SOURCE, namespace, pdf_file_name)
        processed_pdf_filepath = Path(OCR_OUTPUT, namespace, f"{file_name}.pdf")
        failed_pdf_filepath = Path(OCR_FAILED, namespace, pdf_file_name)
        return source_pdf_filepath, processed_pdf_filepath, failed_pdf_filepath
