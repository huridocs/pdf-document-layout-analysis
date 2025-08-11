from pdf_token_type_labels import TokenType
from ports.services.text_extraction_service import TextExtractionService
from configuration import service_logger


class TextExtractionAdapter(TextExtractionService):
    def extract_text_by_types(self, segment_boxes: list[dict], token_types: list[TokenType]) -> dict:
        service_logger.info(f"Extracted types: {[t.name for t in token_types]}")
        text = "\n".join(
            [
                segment_box["text"]
                for segment_box in segment_boxes
                if TokenType.from_text(segment_box["type"].replace(" ", "_")) in token_types
            ]
        )
        return text

    def extract_all_text(self, segment_boxes: list[dict]) -> dict:
        all_types = [t for t in TokenType]
        return self.extract_text_by_types(segment_boxes, all_types)
