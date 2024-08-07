from pathlib import Path
from fastapi import UploadFile
from starlette.responses import FileResponse
from pdf_layout_analysis.run_pdf_layout_analysis import analyze_pdf, pdf_content_to_pdf_path, get_file_path
from pdf_layout_analysis.run_pdf_layout_analysis_fast import analyze_pdf_fast
from visualization.save_output_to_pdf import save_output_to_pdf


def get_visualization(file: UploadFile, fast: bool):
    file_content = file.file.read()
    segment_boxes: list[dict] = analyze_pdf_fast(file_content) if fast else analyze_pdf(file_content, "")
    pdf_path = pdf_content_to_pdf_path(file_content)
    output_pdf_path = get_file_path(pdf_path.name.split(".")[0], "pdf")
    save_output_to_pdf(pdf_path, segment_boxes, output_pdf_path)
    pdf_name = Path(output_pdf_path).name
    file_response = FileResponse(output_pdf_path, media_type="application/pdf", filename=pdf_name)
    return file_response
