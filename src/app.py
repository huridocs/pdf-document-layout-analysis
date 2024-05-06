import sys

import torch
from fastapi import FastAPI, HTTPException, UploadFile, File

from configuration import service_logger
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
