import os
import sys
from os.path import join
from pathlib import Path
import torch
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import PlainTextResponse

from catch_exceptions import catch_exceptions
from configuration import service_logger, XMLS_PATH
from pdf_layout_analysis.run_pdf_layout_analysis import analyze_pdf
from pdf_layout_analysis.run_pdf_layout_analysis_fast import analyze_pdf_fast
from toc.extract_table_of_contents import extract_table_of_contents

service_logger.info(f"Is PyTorch using GPU: {torch.cuda.is_available()}")

app = FastAPI()


@app.get("/")
async def info():
    return sys.version


@app.post("/")
@catch_exceptions
async def run(file: UploadFile = File(...), fast: bool = Form(False)):
    service_logger.info(f"Processing file: {file.filename}")
    return analyze_pdf_fast(file.file.read()) if fast else analyze_pdf(file.file.read())


@app.post("/save_xml/{xml_file_name}")
@catch_exceptions
async def analyze_and_save_xml(file: UploadFile = File(...), xml_file_name: str | None = None):
    return analyze_pdf(file.file.read(), xml_file_name)


@app.get("/get_xml/{xml_file_name}", response_class=PlainTextResponse)
@catch_exceptions
async def get_xml(xml_file_name: str):
    xml_file_path = Path(join(XMLS_PATH, xml_file_name))

    with open(xml_file_path, mode="r") as file:
        content = file.read()
        os.remove(xml_file_path)
        return content


@app.post("/toc")
@catch_exceptions
async def get_toc(file: UploadFile = File(...), fast: bool = Form(False)):
    file_content = file.file.read()
    if fast:
        return extract_table_of_contents(file_content, analyze_pdf_fast(file_content))
    return extract_table_of_contents(file_content, analyze_pdf(file_content))
