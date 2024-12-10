import os
import shutil
import subprocess
from pathlib import Path

from configuration import OCR_SOURCE, OCR_OUTPUT, OCR_FAILED
from ocr.languages import iso_to_tesseract


def get_paths(namespace: str, pdf_file_name: str):
    file_name = "".join(pdf_file_name.split(".")[:-1]) if "." in pdf_file_name else pdf_file_name
    source_pdf_filepath = Path(OCR_SOURCE, namespace, pdf_file_name)
    processed_pdf_filepath = Path(OCR_OUTPUT, namespace, f"{file_name}.pdf")
    failed_pdf_filepath = Path(OCR_FAILED, namespace, pdf_file_name)
    return source_pdf_filepath, processed_pdf_filepath, failed_pdf_filepath


def ocr_pdf(filename, namespace, language="en"):
    source_pdf_filepath, processed_pdf_filepath, failed_pdf_filepath = get_paths(namespace, filename)
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
