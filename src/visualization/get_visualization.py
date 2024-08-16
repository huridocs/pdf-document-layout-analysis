from pathlib import Path
from tempfile import gettempdir
from fastapi import UploadFile
from starlette.responses import FileResponse
from pdf_layout_analysis.run_pdf_layout_analysis import analyze_pdf
from pdf_layout_analysis.run_pdf_layout_analysis_fast import analyze_pdf_fast
from visualization.save_output_to_pdf import save_output_to_pdf
from glob import glob
from os.path import getctime, join


def get_visualization(file: UploadFile, fast: bool):
    file_content = file.file.read()
    segment_boxes: list[dict] = analyze_pdf_fast(file_content) if fast else analyze_pdf(file_content, "")
    pdf_path = max(glob(join(gettempdir(), "*.pdf")), key=getctime)
    save_output_to_pdf(pdf_path, segment_boxes)
    file_response = FileResponse(pdf_path, media_type="application/pdf", filename=Path(pdf_path).name)
    return file_response
