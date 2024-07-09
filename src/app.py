import os
import sys
from os.path import join
from pathlib import Path
import torch
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import PlainTextResponse

from catch_exceptions import catch_exceptions
from configuration import service_logger, XMLS_PATH
from pdf_layout_analysis.run_pdf_layout_analysis import analyze_pdf
from pdf_layout_analysis.run_pdf_layout_analysis_fast import analyze_pdf_fast

service_logger.info(f"Is PyTorch using GPU: {torch.cuda.is_available()}")

app = FastAPI()


@app.get("/")
async def info():
    return sys.version


@app.post("/")
@catch_exceptions
async def run(file: UploadFile = File(...)):
    service_logger.info(f"Processing file: {file.filename}")
    return analyze_pdf(file.file.read())


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


@app.post("/fast")
@catch_exceptions
async def run_fast(file: UploadFile = File(...)):
    return analyze_pdf_fast(file.file.read())
