import os
import sys
from os.path import join
from pathlib import Path

import torch
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import PlainTextResponse

from analyze_pdf_fast import analyze_pdf_fast
from configuration import service_logger, XMLS_PATH
from src.analyze_pdf import analyze_pdf

service_logger.info(f"Is PyTorch using GPU: {torch.cuda.is_available()}")

app = FastAPI()


@app.get("/")
async def info():
    return sys.version


@app.post("/")
async def run(file: UploadFile = File(...)):
    try:
        service_logger.info(f"Processing file: {file.filename}")
        return analyze_pdf(file.file.read())
    except Exception:
        service_logger.error("Error", exc_info=1)
        raise HTTPException(status_code=422, detail="Error extracting paragraphs")


@app.post("/save_xml/{xml_file_name}")
async def analyze_and_save_xml(file: UploadFile = File(...), xml_file_name: str = None):
    try:
        service_logger.info(f"Processing file: {file.filename}")
        service_logger.info(f"Saving xml: {xml_file_name}")
        return analyze_pdf(file.file.read(), xml_file_name)
    except Exception:
        service_logger.error("Error", exc_info=1)
        raise HTTPException(status_code=422, detail="Error extracting paragraphs")


@app.get("/get_xml/{xml_file_name}", response_class=PlainTextResponse)
async def get_xml(xml_file_name: str):
    try:
        xml_file_path = Path(join(XMLS_PATH, xml_file_name))

        with open(xml_file_path, mode="r") as file:
            content = file.read()
            os.remove(xml_file_path)
            return content
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="No xml file")
    except Exception:
        service_logger.error("Error", exc_info=1)
        raise HTTPException(status_code=422, detail="An error has occurred. Check graylog for more info")


@app.post("/fast")
async def run_fast(file: UploadFile = File(...)):
    try:
        service_logger.info(f"Processing file: {file.filename}")
        return analyze_pdf_fast(file.file.read())
    except Exception:
        service_logger.error("Error", exc_info=1)
        raise HTTPException(status_code=422, detail="Error extracting paragraphs")
