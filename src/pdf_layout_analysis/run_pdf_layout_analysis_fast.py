from os.path import join
from typing import AnyStr

from data_model.PdfImages import PdfImages
from extraction_formats.extract_formula_formats import extract_formula_format
from extraction_formats.extract_table_formats import extract_table_format
from fast_trainer.ParagraphExtractorTrainer import ParagraphExtractorTrainer
from fast_trainer.model_configuration import MODEL_CONFIGURATION as PARAGRAPH_EXTRACTION_CONFIGURATION
from pdf_layout_analysis.run_pdf_layout_analysis import pdf_content_to_pdf_path
from pdf_tokens_type_trainer.TokenTypeTrainer import TokenTypeTrainer
from pdf_tokens_type_trainer.ModelConfiguration import ModelConfiguration

from configuration import ROOT_PATH, service_logger
from data_model.SegmentBox import SegmentBox


def analyze_pdf_fast(
    file: AnyStr, xml_file_name: str = "", extraction_format: str = "", keep_pdf: bool = False
) -> list[dict]:
    pdf_path = pdf_content_to_pdf_path(file)
    service_logger.info("Creating Paragraph Tokens [fast]")

    pdf_images = PdfImages.from_pdf_path(pdf_path=pdf_path, pdf_name="", xml_file_name=xml_file_name)

    token_type_trainer = TokenTypeTrainer([pdf_images.pdf_features], ModelConfiguration())
    token_type_trainer.set_token_types(join(ROOT_PATH, "models", "token_type_lightgbm.model"))

    trainer = ParagraphExtractorTrainer(
        pdfs_features=[pdf_images.pdf_features], model_configuration=PARAGRAPH_EXTRACTION_CONFIGURATION
    )
    segments = trainer.get_pdf_segments(join(ROOT_PATH, "models", "paragraph_extraction_lightgbm.model"))

    extract_formula_format(pdf_images, segments)
    if extraction_format:
        extract_table_format(pdf_images, segments, extraction_format)

    pdf_images.remove_images()
    if not keep_pdf:
        pdf_path.unlink(missing_ok=True)
    return [SegmentBox.from_pdf_segment(pdf_segment, pdf_images.pdf_features.pages, pdf_segment.sub_element_positions).to_dict() for pdf_segment in segments]
