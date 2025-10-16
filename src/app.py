from configuration import RESTART_IF_NO_GPU, service_logger
from drivers.web.dependency_injection import setup_dependencies
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import PlainTextResponse, Response
from catch_exceptions import catch_exceptions
from typing import Optional, Union
from starlette.concurrency import run_in_threadpool
import torch
import sys
import subprocess
import json

from use_cases.pdf_analysis.get_pdf_word_positions import get_pdf_word_positions

if RESTART_IF_NO_GPU:
    if not torch.cuda.is_available():
        raise RuntimeError("No GPU available. Restarting the service is required.")

service_logger.info(f"Is PyTorch using GPU: {torch.cuda.is_available()}")

controllers = setup_dependencies()

app = FastAPI()


@app.get("/")
async def root():
    return sys.version + " Using GPU: " + str(torch.cuda.is_available())


@app.get("/info")
async def info():
    return {
        "sys": sys.version,
        "tesseract_version": subprocess.run("tesseract --version", shell=True, text=True, capture_output=True).stdout,
        "ocrmypdf_version": subprocess.run("ocrmypdf --version", shell=True, text=True, capture_output=True).stdout,
        "supported_languages": controllers.process_ocr_use_case.get_supported_languages(),
    }


@app.get("/error")
async def error():
    raise FileNotFoundError("This is a test error from the error endpoint")


@app.post("/")
@catch_exceptions
async def analyze_pdf(file: UploadFile = File(...), fast: bool = Form(False), parse_tables_and_math: bool = Form(False)):
    return await run_in_threadpool(
        controllers.analyze_pdf_use_case.execute, file.file.read(), "", parse_tables_and_math, fast, False
    )


@app.post("/word_positions")
@catch_exceptions
async def word_positions(file: UploadFile = File(...)):
    return await run_in_threadpool(get_pdf_word_positions, file.file.read())


@app.post("/save_xml/{xml_file_name}")
@catch_exceptions
async def analyze_and_save_xml(xml_file_name: str, file: UploadFile = File(...), fast: bool = Form(False)):
    if not xml_file_name.endswith(".xml"):
        xml_file_name = f"{xml_file_name}.xml"
    return await run_in_threadpool(
        controllers.analyze_pdf_use_case.execute_and_save_xml, file.file.read(), xml_file_name, fast
    )


@app.get("/get_xml/{xml_file_name}", response_class=PlainTextResponse)
@catch_exceptions
async def get_xml_by_name(xml_file_name: str):
    if not xml_file_name.endswith(".xml"):
        xml_file_name = f"{xml_file_name}.xml"
    return await run_in_threadpool(controllers.file_repository.get_xml, xml_file_name)


@app.post("/toc")
@catch_exceptions
async def get_toc_endpoint(file: UploadFile = File(...), fast: bool = Form(False)):
    return await run_in_threadpool(controllers.extract_toc_use_case.execute, file, fast)


@app.post("/toc_legacy_uwazi_compatible")
@catch_exceptions
async def toc_legacy_uwazi_compatible(file: UploadFile = File(...)):
    return await run_in_threadpool(controllers.extract_toc_use_case.execute_uwazi_compatible, file)


@app.post("/toc_from_xml")
@catch_exceptions
async def toc_from_xml(segment_boxes: str = Form(...), file: UploadFile = File(...)):
    segment_boxes_list = json.loads(segment_boxes)
    service_logger.info(f"Received {len(segment_boxes_list)} segment boxes for TOC extraction from XML.")
    file_content: bytes = await file.read()
    return await run_in_threadpool(controllers.extract_toc_use_case.execute_with_segments, file_content, segment_boxes_list)


@app.post("/text")
@catch_exceptions
async def get_text_endpoint(file: UploadFile = File(...), fast: bool = Form(False), types: str = Form("all")):
    return await run_in_threadpool(controllers.extract_text_use_case.execute, file, fast, types)


@app.post("/visualize")
@catch_exceptions
async def get_visualization_endpoint(file: UploadFile = File(...), fast: bool = Form(False)):
    return await run_in_threadpool(controllers.create_visualization_use_case.execute, file, fast)


@app.post("/markdown", response_model=None)
@catch_exceptions
async def convert_to_markdown_endpoint(
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
        controllers.convert_to_markdown_use_case.execute,
        file.file.read(),
        fast,
        extract_toc,
        dpi,
        output_file,
        target_languages_list,
        translation_model,
    )


@app.post("/html", response_model=None)
@catch_exceptions
async def convert_to_html_endpoint(
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
        controllers.convert_to_html_use_case.execute,
        file.file.read(),
        fast,
        extract_toc,
        dpi,
        output_file,
        target_languages_list,
        translation_model,
    )


@app.post("/ocr")
@catch_exceptions
async def ocr_pdf_sync(file: UploadFile = File(...), language: str = Form("en")):
    return await run_in_threadpool(controllers.process_ocr_use_case.execute, file, language)
