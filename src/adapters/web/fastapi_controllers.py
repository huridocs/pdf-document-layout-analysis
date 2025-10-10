import sys
import subprocess
from fastapi import UploadFile, File, Form
from typing import Optional, Union
from starlette.responses import Response
from starlette.concurrency import run_in_threadpool
from use_cases.pdf_analysis.analyze_pdf_use_case import AnalyzePDFUseCase
from use_cases.text_extraction.extract_text_use_case import ExtractTextUseCase
from use_cases.toc_extraction.extract_toc_use_case import ExtractTOCUseCase
from use_cases.visualization.create_visualization_use_case import CreateVisualizationUseCase
from use_cases.ocr.process_ocr_use_case import ProcessOCRUseCase
from use_cases.markdown_conversion.convert_to_markdown_use_case import ConvertToMarkdownUseCase
from use_cases.html_conversion.convert_to_html_use_case import ConvertToHtmlUseCase
from adapters.storage.file_system_repository import FileSystemRepository


class FastAPIControllers:
    def __init__(
        self,
        analyze_pdf_use_case: AnalyzePDFUseCase,
        extract_text_use_case: ExtractTextUseCase,
        extract_toc_use_case: ExtractTOCUseCase,
        create_visualization_use_case: CreateVisualizationUseCase,
        process_ocr_use_case: ProcessOCRUseCase,
        convert_to_markdown_use_case: ConvertToMarkdownUseCase,
        convert_to_html_use_case: ConvertToHtmlUseCase,
        file_repository: FileSystemRepository,
    ):
        self.analyze_pdf_use_case = analyze_pdf_use_case
        self.extract_text_use_case = extract_text_use_case
        self.extract_toc_use_case = extract_toc_use_case
        self.create_visualization_use_case = create_visualization_use_case
        self.process_ocr_use_case = process_ocr_use_case
        self.convert_to_markdown_use_case = convert_to_markdown_use_case
        self.convert_to_html_use_case = convert_to_html_use_case
        self.file_repository = file_repository

    async def root(self):
        import torch

        return sys.version + " Using GPU: " + str(torch.cuda.is_available())

    async def info(self):
        return {
            "sys": sys.version,
            "tesseract_version": subprocess.run("tesseract --version", shell=True, text=True, capture_output=True).stdout,
            "ocrmypdf_version": subprocess.run("ocrmypdf --version", shell=True, text=True, capture_output=True).stdout,
            "supported_languages": self.process_ocr_use_case.get_supported_languages(),
        }

    async def error(self):
        raise FileNotFoundError("This is a test error from the error endpoint")

    async def analyze_pdf(
        self, file: UploadFile = File(...), fast: bool = Form(False), parse_tables_and_math: bool = Form(False)
    ):
        return await run_in_threadpool(
            self.analyze_pdf_use_case.execute, file.file.read(), "", parse_tables_and_math, fast, False
        )

    async def analyze_and_save_xml(
        self, file: UploadFile = File(...), xml_file_name: str | None = None, fast: bool = Form(False)
    ):
        if not xml_file_name.endswith(".xml"):
            xml_file_name = f"{xml_file_name}.xml"
        return await run_in_threadpool(self.analyze_pdf_use_case.execute_and_save_xml, file.file.read(), xml_file_name, fast)

    async def get_xml_by_name(self, xml_file_name: str):
        if not xml_file_name.endswith(".xml"):
            xml_file_name = f"{xml_file_name}.xml"
        return await run_in_threadpool(self.file_repository.get_xml, xml_file_name)

    async def get_toc_endpoint(self, file: UploadFile = File(...), fast: bool = Form(False)):
        return await run_in_threadpool(self.extract_toc_use_case.execute, file, fast)

    async def toc_legacy_uwazi_compatible(self, file: UploadFile = File(...)):
        return await run_in_threadpool(self.extract_toc_use_case.execute_uwazi_compatible, file)

    async def get_text_endpoint(self, file: UploadFile = File(...), fast: bool = Form(False), types: str = Form("all")):
        return await run_in_threadpool(self.extract_text_use_case.execute, file, fast, types)

    async def get_visualization_endpoint(self, file: UploadFile = File(...), fast: bool = Form(False)):
        return await run_in_threadpool(self.create_visualization_use_case.execute, file, fast)

    async def ocr_pdf_sync(self, file: UploadFile = File(...), language: str = Form("en")):
        return await run_in_threadpool(self.process_ocr_use_case.execute, file, language)

    async def convert_to_markdown_endpoint(
        self,
        file: UploadFile = File(...),
        fast: bool = Form(False),
        extract_toc: bool = Form(False),
        dpi: int = Form(120),
        output_file: Optional[str] = Form(None),
        target_languages: Optional[str] = Form(None),
        translation_model: str = Form("gpt-oss"),
    ) -> Union[str, Response]:
        target_languages_list = None
        if target_languages:
            target_languages_list = [lang.strip() for lang in target_languages.split(",") if lang.strip()]

        return await run_in_threadpool(
            self.convert_to_markdown_use_case.execute,
            file.file.read(),
            fast,
            extract_toc,
            dpi,
            output_file,
            target_languages_list,
            translation_model,
        )

    async def convert_to_html_endpoint(
        self,
        file: UploadFile = File(...),
        fast: bool = Form(False),
        extract_toc: bool = Form(False),
        dpi: int = Form(120),
        output_file: Optional[str] = Form(None),
        target_languages: Optional[str] = Form(None),
        translation_model: str = Form("gpt-oss"),
    ) -> Union[str, Response]:
        target_languages_list = None
        if target_languages:
            target_languages_list = [lang.strip() for lang in target_languages.split(",") if lang.strip()]

        return await run_in_threadpool(
            self.convert_to_html_use_case.execute,
            file.file.read(),
            fast,
            extract_toc,
            dpi,
            output_file,
            target_languages_list,
            translation_model,
        )
