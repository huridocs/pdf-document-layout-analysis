from pathlib import Path
from fastapi import UploadFile
from starlette.responses import FileResponse
from file_utils import sanitize_filename
from ports.services.ocr_service import OCRService
from ports.repositories.file_repository import FileRepository
from configuration import OCR_SOURCE


class ProcessOCRUseCase:
    def __init__(self, ocr_service: OCRService, file_repository: FileRepository):
        self.ocr_service = ocr_service
        self.file_repository = file_repository

    def execute(
        self, file: UploadFile, language: str = "en", rotate_pages: bool = False, deskew: bool = False
    ) -> FileResponse:
        namespace = "sync_pdfs"
        filename = sanitize_filename(file.filename)

        self.file_repository.save_pdf_to_directory(
            content=file.file.read(), filename=filename, directory=Path(OCR_SOURCE), namespace=namespace
        )

        processed_pdf_filepath = self.ocr_service.process_pdf_ocr(filename, namespace, language, rotate_pages, deskew)

        return FileResponse(path=processed_pdf_filepath, media_type="application/pdf")

    def get_supported_languages(self) -> list:
        return self.ocr_service.get_supported_languages()
