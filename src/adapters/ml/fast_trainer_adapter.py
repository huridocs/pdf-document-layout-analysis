from os.path import join
from domain.PdfImages import PdfImages
from domain.PdfSegment import PdfSegment
from ports.services.ml_model_service import MLModelService
from adapters.ml.fast_trainer.ParagraphExtractorTrainer import ParagraphExtractorTrainer
from adapters.ml.fast_trainer.model_configuration import MODEL_CONFIGURATION as PARAGRAPH_EXTRACTION_CONFIGURATION
from adapters.ml.pdf_tokens_type_trainer.TokenTypeTrainer import TokenTypeTrainer
from adapters.ml.pdf_tokens_type_trainer.ModelConfiguration import ModelConfiguration
from configuration import ROOT_PATH, service_logger


class FastTrainerAdapter(MLModelService):
    def predict_document_layout(self, pdf_images: list[PdfImages]) -> list[PdfSegment]:
        return self.predict_layout_fast(pdf_images)

    def predict_layout_fast(self, pdf_images: list[PdfImages]) -> list[PdfSegment]:
        service_logger.info("Creating Paragraph Tokens [fast]")

        pdf_images_obj = pdf_images[0]

        token_type_trainer = TokenTypeTrainer([pdf_images_obj.pdf_features], ModelConfiguration())
        token_type_trainer.set_token_types(join(ROOT_PATH, "models", "token_type_lightgbm.model"))

        trainer = ParagraphExtractorTrainer(
            pdfs_features=[pdf_images_obj.pdf_features], model_configuration=PARAGRAPH_EXTRACTION_CONFIGURATION
        )
        segments = trainer.get_pdf_segments(join(ROOT_PATH, "models", "paragraph_extraction_lightgbm.model"))

        pdf_images_obj.remove_images()

        return segments
