import tempfile
import uuid
from os.path import join
from pathlib import Path
from typing import AnyStr
from domain.PdfSegment import PdfSegment
from pdf_features import PdfFeatures, Rectangle
from pdf_token_type_labels import TokenType
from ports.services.toc_service import TOCService
from configuration import service_logger
from adapters.infrastructure.toc.TOCExtractor import TOCExtractor
from adapters.infrastructure.toc.PdfSegmentation import PdfSegmentation

TITLE_TYPES = {TokenType.TITLE, TokenType.SECTION_HEADER}
SKIP_TYPES = {TokenType.TITLE, TokenType.SECTION_HEADER, TokenType.PAGE_HEADER, TokenType.PICTURE}


class TOCServiceAdapter(TOCService):

    def extract_table_of_contents(
        self, pdf_content: AnyStr, segment_boxes: list[dict], skip_document_name=False
    ) -> list[dict]:
        service_logger.info("Getting TOC")
        pdf_path = self._pdf_content_to_pdf_path(pdf_content)
        pdf_features: PdfFeatures = PdfFeatures.from_pdf_path(pdf_path)
        pdf_segments: list[PdfSegment] = self._get_pdf_segments_from_segment_boxes(pdf_features, segment_boxes)
        title_segments = [segment for segment in pdf_segments if segment.segment_type in TITLE_TYPES]
        if skip_document_name:
            self._skip_name_of_the_document(pdf_segments, title_segments)
        pdf_segmentation: PdfSegmentation = PdfSegmentation(pdf_features, title_segments)
        toc_instance: TOCExtractor = TOCExtractor(pdf_segmentation)
        return toc_instance.to_dict()

    def extract_table_of_contents_from_xml(
        self, xml_content: bytes, segment_boxes: list[dict], skip_document_name=False
    ) -> list[dict]:
        service_logger.info("Getting TOC")
        pdf_features: PdfFeatures = PdfFeatures.from_poppler_etree_string(xml_content)
        pdf_segments: list[PdfSegment] = self._get_pdf_segments_from_segment_boxes(pdf_features, segment_boxes)
        title_segments = [segment for segment in pdf_segments if segment.segment_type in TITLE_TYPES]
        if skip_document_name:
            self._skip_name_of_the_document(pdf_segments, title_segments)
        pdf_segmentation: PdfSegmentation = PdfSegmentation(pdf_features, title_segments)
        toc_instance: TOCExtractor = TOCExtractor(pdf_segmentation)
        return toc_instance.to_dict()

    def format_toc_for_uwazi(self, toc_items: list[dict]) -> list[dict]:
        toc_compatible = []
        for toc_item in toc_items:
            toc_compatible.append(toc_item.copy())
            toc_compatible[-1]["bounding_box"]["left"] = int(toc_item["bounding_box"]["left"] / 0.75)
            toc_compatible[-1]["bounding_box"]["top"] = int(toc_item["bounding_box"]["top"] / 0.75)
            toc_compatible[-1]["bounding_box"]["width"] = int(toc_item["bounding_box"]["width"] / 0.75)
            toc_compatible[-1]["bounding_box"]["height"] = int(toc_item["bounding_box"]["height"] / 0.75)
            toc_compatible[-1]["selectionRectangles"] = [toc_compatible[-1]["bounding_box"]]
            del toc_compatible[-1]["bounding_box"]
        return toc_compatible

    def _get_file_path(self, file_name: str, extension: str) -> str:
        return join(tempfile.gettempdir(), file_name + "." + extension)

    def _pdf_content_to_pdf_path(self, file_content: AnyStr) -> Path:
        file_id = str(uuid.uuid1())
        pdf_path = Path(self._get_file_path(file_id, "pdf"))
        pdf_path.write_bytes(file_content)
        return pdf_path

    def _skip_name_of_the_document(self, pdf_segments: list[PdfSegment], title_segments: list[PdfSegment]) -> None:
        segments_to_remove = []
        last_segment = None
        for segment in pdf_segments:
            if segment.segment_type not in SKIP_TYPES:
                break
            if segment.segment_type == TokenType.PAGE_HEADER or segment.segment_type == TokenType.PICTURE:
                continue
            if not last_segment:
                last_segment = segment
            else:
                if segment.bounding_box.right < last_segment.bounding_box.left + last_segment.bounding_box.width * 0.66:
                    break
                last_segment = segment
            if segment.segment_type in TITLE_TYPES:
                segments_to_remove.append(segment)
        for segment in segments_to_remove:
            title_segments.remove(segment)

    def _get_pdf_segments_from_segment_boxes(self, pdf_features: PdfFeatures, segment_boxes: list[dict]) -> list[PdfSegment]:
        pdf_segments: list[PdfSegment] = []
        for segment_box in segment_boxes:
            left, top, width, height = segment_box["left"], segment_box["top"], segment_box["width"], segment_box["height"]
            bounding_box = Rectangle.from_width_height(left, top, width, height)
            segment_type = TokenType.from_value(segment_box["type"])
            pdf_name = pdf_features.file_name
            segment = PdfSegment(segment_box["page_number"], bounding_box, segment_box["text"], segment_type, pdf_name)
            pdf_segments.append(segment)
        return pdf_segments
