import time
from typing import Optional

import torch
from PIL import Image
from struct_eqtable import build_model

from configuration import service_logger
from data_model.PdfImages import PdfImages
from fast_trainer.PdfSegment import PdfSegment
from pdf_token_type_labels.TokenType import TokenType


def get_table_format(
    model,
    raw_image: Image = None,
    image_path: str = "",
    max_waiting_time: int = 1000,
    extraction_format: str = "latex",
) -> str:
    from pypandoc import convert_text

    if not raw_image:
        raw_image = Image.open(image_path)

    start_time = time.time()
    with torch.no_grad():
        output = model(raw_image)

    cost_time = time.time() - start_time

    if cost_time >= max_waiting_time:
        warn_log = (
            f"The table extraction model inference time exceeds the maximum waiting time {max_waiting_time} seconds.\n"
            "Please increase the maximum waiting time or model may not support the type of input table image"
        )
        service_logger.info(warn_log)

    for i, latex_code in enumerate(output):
        for tgt_fmt in [extraction_format]:
            tgt_code = convert_text(latex_code, tgt_fmt, format="latex") if tgt_fmt != "latex" else latex_code
            return tgt_code


def get_model():

    ckpt_path: str = "U4R/StructTable-base"
    max_new_tokens: int = 2048
    max_waiting_time: int = 1000
    use_cpu: bool = False
    tensorrt_path: Optional[str] = None
    model = build_model(ckpt_path, max_new_tokens=max_new_tokens, max_time=max_waiting_time, tensorrt_path=tensorrt_path)
    if not use_cpu and tensorrt_path is None:
        try:
            model = model.cuda()
        except RuntimeError:
            pass
    return model


def extract_table_format(pdf_images: PdfImages, predicted_segments: list[PdfSegment], extraction_format: str):
    table_segments = [
        (index, segment) for index, segment in enumerate(predicted_segments) if segment.segment_type == TokenType.TABLE
    ]
    if not table_segments:
        return

    model = get_model()

    for index, table_segment in table_segments:
        page_image: Image = pdf_images.pdf_images[table_segment.page_number - 1]
        left, top = table_segment.bounding_box.left, table_segment.bounding_box.top
        width, height = table_segment.bounding_box.width, table_segment.bounding_box.height
        table_image = page_image.crop((left, top, left + width, top + height))
        try:
            extracted_table = get_table_format(model, raw_image=table_image, extraction_format=extraction_format)
        except RuntimeError:
            continue
        predicted_segments[index].text_content = extracted_table
