from os import makedirs
from os.path import join
from pdf_annotate import PdfAnnotator, Location, Appearance
from configuration import ROOT_PATH

DOCLAYNET_COLOR_BY_TYPE = {
    "Caption": "#FFC300",
    "Footnote": "#581845",
    "Formula": "#FF5733",
    "List item": "#008B8B",
    "Page footer": "#FF5733",
    "Page header": "#581845",
    "Picture": "#C70039",
    "Section header": "#C70039",
    "Table": "#FF8C00",
    "Text": "#606060",
    "Title": "#EED400",
}


def hex_color_to_rgb(color: str):
    r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
    alpha = 1
    return r / 255, g / 255, b / 255, alpha


def add_prediction_annotation(annotator: PdfAnnotator, segment_box: dict, segment_index, page_height: int):
    predicted_type = segment_box["type"]
    color = DOCLAYNET_COLOR_BY_TYPE[predicted_type]
    left, top, right, bottom = (
        segment_box["left"],
        page_height - segment_box["top"],
        segment_box["left"] + segment_box["width"],
        page_height - (segment_box["top"] + segment_box["height"]),
    )
    text_box_size = len(predicted_type) * 8 + 8
    annotator.add_annotation(
        "square",
        Location(x1=left, y1=bottom, x2=right, y2=top, page=int(segment_box["page_number"]) - 1),
        Appearance(stroke_color=hex_color_to_rgb(color)),
    )

    annotator.add_annotation(
        "square",
        Location(x1=left, y1=top, x2=left + text_box_size, y2=top + 10, page=int(segment_box["page_number"]) - 1),
        Appearance(fill=hex_color_to_rgb(color)),
    )

    content = predicted_type.capitalize() + f"  [{str(segment_index+1)}]"
    annotator.add_annotation(
        "text",
        Location(x1=left, y1=top, x2=left + text_box_size, y2=top + 10, page=int(segment_box["page_number"]) - 1),
        Appearance(content=content, font_size=8, fill=(1, 1, 1), stroke_width=3),
    )


def save_output(annotator: PdfAnnotator, output_pdf_path: str):
    annotator.write(output_pdf_path)


def save_output_to_pdf(pdf_path: str, segment_boxes: list[dict]):
    pdf_outputs_path = join(ROOT_PATH, f"pdf_outputs")
    makedirs(pdf_outputs_path, exist_ok=True)
    annotator = PdfAnnotator(str(pdf_path))
    segment_index = 0
    current_page = 1
    for segment_box in segment_boxes:
        if int(segment_box["page_number"]) != current_page:
            segment_index = 0
            current_page += 1
        page_height = int(segment_box["page_height"])
        add_prediction_annotation(annotator, segment_box, segment_index, page_height)
        segment_index += 1
    save_output(annotator, pdf_path)
