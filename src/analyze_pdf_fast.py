from os.path import join
from typing import AnyStr

from paragraph_extraction_trainer.ParagraphExtractorTrainer import ParagraphExtractorTrainer
from paragraph_extraction_trainer.model_configuration import MODEL_CONFIGURATION as PARAGRAPH_EXTRACTION_CONFIGURATION
from pdf_features.PdfFeatures import PdfFeatures
from pdf_tokens_type_trainer.TokenTypeTrainer import TokenTypeTrainer
from pdf_tokens_type_trainer.ModelConfiguration import ModelConfiguration

from analyze_pdf import pdf_content_to_pdf_path
from configuration import ROOT_PATH, service_logger
from data_model.SegmentBox import SegmentBox


def analyze_pdf_fast(file: AnyStr):
    pdf_path = pdf_content_to_pdf_path(file)
    service_logger.info("Creating Paragraph Tokens [fast]")
    pdf_features = PdfFeatures.from_pdf_path(pdf_path)
    token_type_trainer = TokenTypeTrainer([pdf_features], ModelConfiguration())
    token_type_trainer.set_token_types(join(ROOT_PATH, "models", "token_type_lightgbm.model"))
    trainer = ParagraphExtractorTrainer(pdfs_features=[pdf_features], model_configuration=PARAGRAPH_EXTRACTION_CONFIGURATION)
    segments = trainer.get_pdf_segments(join(ROOT_PATH, "models", "paragraph_extraction_lightgbm.model"))
    return [SegmentBox.from_pdf_segment(pdf_segment, pdf_features.pages).to_dict() for pdf_segment in segments]
