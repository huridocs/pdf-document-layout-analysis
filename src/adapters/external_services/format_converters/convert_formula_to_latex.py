from PIL.Image import Image
from pix2tex.cli import LatexOCR
from domain.PdfImages import PdfImages
from domain.PdfSegment import PdfSegment
from pdf_token_type_labels import TokenType
import latex2mathml.converter


def has_arabic(text: str) -> bool:
    return any("\u0600" <= char <= "\u06FF" or "\u0750" <= char <= "\u077F" for char in text)


def is_valid_latex(formula: str) -> bool:
    try:
        latex2mathml.converter.convert(formula)
        return True
    except Exception:
        return False


def extract_formula_format(pdf_images: PdfImages, predicted_segments: list[PdfSegment]):
    formula_segments = [segment for segment in predicted_segments if segment.segment_type == TokenType.FORMULA]
    if not formula_segments:
        return

    model = LatexOCR()
    model.args.temperature = 1e-8

    for formula_segment in formula_segments:
        if has_arabic(formula_segment.text_content):
            continue
        page_image: Image = pdf_images.pdf_images[formula_segment.page_number - 1]
        left, top = formula_segment.bounding_box.left, formula_segment.bounding_box.top
        right, bottom = formula_segment.bounding_box.right, formula_segment.bounding_box.bottom
        left = int(left * pdf_images.dpi / 72)
        top = int(top * pdf_images.dpi / 72)
        right = int(right * pdf_images.dpi / 72)
        bottom = int(bottom * pdf_images.dpi / 72)
        formula_image = page_image.crop((left, top, right, bottom))
        formula_result = model(formula_image)
        if not is_valid_latex(formula_result):
            continue
        formula_segment.text_content = f"$${formula_result}$$"
