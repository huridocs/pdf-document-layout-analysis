import sys
import torch
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import PlainTextResponse
from starlette.concurrency import run_in_threadpool

from catch_exceptions import catch_exceptions
from configuration import service_logger
from pdf_layout_analysis.get_xml import get_xml
from pdf_layout_analysis.run_pdf_layout_analysis import analyze_pdf
from pdf_layout_analysis.run_pdf_layout_analysis_fast import analyze_pdf_fast
from toc.extract_table_of_contents import extract_table_of_contents
from toc.get_toc import get_toc

service_logger.info(f"Is PyTorch using GPU: {torch.cuda.is_available()}")

app = FastAPI()


@app.get("/")
async def info():
    return sys.version + " Using GPU: " + str(torch.cuda.is_available())


@app.get("/error")
async def error():
    raise FileNotFoundError("This is a test error from the error endpoint")


@app.post("/")
@catch_exceptions
async def run(file: UploadFile = File(...)):
    return await run_in_threadpool(analyze_pdf, file.file.read(), "")


@app.post("/save_xml/{xml_file_name}")
@catch_exceptions
async def analyze_and_save_xml(file: UploadFile = File(...), xml_file_name: str | None = None):
    return await run_in_threadpool(analyze_pdf, file.file.read(), xml_file_name)


@app.get("/get_xml/{xml_file_name}", response_class=PlainTextResponse)
@catch_exceptions
async def get_xml_by_name(xml_file_name: str):
    return await run_in_threadpool(get_xml, xml_file_name)


@app.post("/fast")
@catch_exceptions
async def run_fast(file: UploadFile = File(...)):
    return await run_in_threadpool(analyze_pdf_fast, file.file.read())


@app.post("/toc")
@catch_exceptions
async def get_toc_endpoint(file: UploadFile = File(...), fast: bool = Form(False)):
    return await run_in_threadpool(get_toc, file, fast)
