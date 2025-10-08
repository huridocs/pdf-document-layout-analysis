import fitz
import tempfile
import zipfile
import io
import json
from fitz import Page
from pathlib import Path
from typing import Optional, Union
from PIL.Image import Image
from pdf2image import convert_from_path
from starlette.responses import Response

from configuration import service_logger
from domain.SegmentBox import SegmentBox
from pdf_features.PdfFeatures import PdfFeatures
from pdf_features.PdfToken import PdfToken
from pdf_features.Rectangle import Rectangle
from pdf_token_type_labels.Label import Label
from pdf_token_type_labels.PageLabels import PageLabels
from pdf_token_type_labels.PdfLabels import PdfLabels
from pdf_token_type_labels.TokenType import TokenType

from adapters.infrastructure.markup_conversion.OutputFormat import OutputFormat
from adapters.infrastructure.markup_conversion.Link import Link
from adapters.infrastructure.markup_conversion.ExtractedImage import ExtractedImage
from adapters.infrastructure.translation.ollama_container_manager import OllamaContainerManager
from adapters.infrastructure.translation.translate_markup_document import translate_markup


class PdfToMarkupServiceAdapter:
    def __init__(self, output_format: OutputFormat):
        self.output_format = output_format

    def convert_to_format(
        self,
        pdf_content: bytes,
        segments: list[SegmentBox],
        extract_toc: bool = False,
        dpi: int = 120,
        output_file: Optional[str] = None,
        target_languages: Optional[list[str]] = None,
        translation_model: str = "gpt-oss",
    ) -> Union[str, Response]:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_file.write(pdf_content)
            temp_pdf_path = Path(temp_file.name)

        try:
            extracted_images: list[ExtractedImage] = [] if output_file else None
            user_base_name = Path(output_file).stem if output_file else None

            content_parts = self._get_styled_content_parts(
                temp_pdf_path, segments, extract_toc, dpi, extracted_images, user_base_name
            )
            content = "".join(content_parts)

            if output_file:
                translations = {}
                if target_languages and len(target_languages) > 0 and content_parts:
                    translations = self._generate_translations(
                        segments, content_parts, target_languages, translation_model, extract_toc
                    )

                return self._create_zip_response(content, extracted_images, output_file, segments, translations)

            return content
        finally:
            if temp_pdf_path.exists():
                temp_pdf_path.unlink()

    def _create_zip_response(
        self,
        content: str,
        extracted_images: list[ExtractedImage],
        output_filename: str,
        segments: list[SegmentBox],
        translations: Optional[dict[str, str]] = None,
    ) -> Response:
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr(output_filename, content.encode("utf-8"))

            if extracted_images:
                base_name = Path(output_filename).stem
                pictures_dir = f"{base_name}_pictures/"

                for image in extracted_images:
                    zip_file.writestr(f"{pictures_dir}{image.filename}", image.image_data)

            if translations:
                output_path = Path(output_filename)
                for language, translated_content in translations.items():
                    translated_filename = f"{output_path.stem}_{language}{output_path.suffix}"
                    zip_file.writestr(translated_filename, translated_content.encode("utf-8"))

            base_name = Path(output_filename).stem
            segmentation_filename = f"{base_name}_segmentation.json"
            segmentation_data = self._create_segmentation_json(segments)
            zip_file.writestr(segmentation_filename, segmentation_data)

        zip_buffer.seek(0)

        zip_filename = f"{Path(output_filename).stem}.zip"
        return Response(
            content=zip_buffer.getvalue(),
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename={zip_filename}"},
        )

    def _create_segmentation_json(self, segments: list[SegmentBox]) -> str:
        segmentation_data = []
        for segment in segments:
            segmentation_data.append(segment.to_dict())
        return json.dumps(segmentation_data, indent=4, ensure_ascii=False)

    def _generate_translations(
        self,
        segments: list[SegmentBox],
        content_parts: list[str],
        target_languages: list[str],
        translation_model: str,
        extract_toc: bool = False,
    ) -> dict[str, str]:
        translations = {}

        ollama_manager = OllamaContainerManager()
        if not ollama_manager.ensure_service_ready(translation_model):
            return translations

        for target_language in target_languages:
            service_logger.info(f"\033[96mTranslating content to {target_language}\033[0m")
            translated_content = translate_markup(
                ollama_manager, self.output_format, segments, content_parts, translation_model, target_language, extract_toc
            )
            translations[target_language] = translated_content

        return translations

    def _create_pdf_labels_from_segments(self, vgt_segments: list[SegmentBox]) -> PdfLabels:
        page_numbers = sorted(set(segment.page_number for segment in vgt_segments))
        page_labels: list[PageLabels] = []
        for page_number in page_numbers:
            segments_in_page = [s for s in vgt_segments if s.page_number == page_number]
            labels: list[Label] = []
            for segment in segments_in_page:
                rect = Rectangle.from_width_height(segment.left, segment.top, segment.width, segment.height)
                label = Label.from_rectangle(rect, TokenType.from_text(segment.type).get_index())
                labels.append(label)
            page_labels.append(PageLabels(number=page_number, labels=labels))
        return PdfLabels(pages=page_labels)

    def _find_closest_segment(self, bounding_box: Rectangle, segments: list[SegmentBox]) -> Optional[SegmentBox]:
        if not segments:
            return None

        def intersection_key(segment: SegmentBox) -> float:
            segment_rect = Rectangle.from_width_height(segment.left, segment.top, segment.width, segment.height)
            return bounding_box.get_intersection_percentage(segment_rect)

        closest = max(segments, key=intersection_key)
        max_intersection = intersection_key(closest)
        if max_intersection > 0:
            return closest

        candidates = [s for s in segments if s.top > bounding_box.top]
        if not candidates:
            return None

        def distance_key(segment: SegmentBox) -> tuple[float, float]:
            vertical_dist = segment.top - bounding_box.top
            segment_center_x = segment.left + segment.width / 2
            box_center_x = bounding_box.left + bounding_box.width / 2
            horizontal_dist = abs(segment_center_x - box_center_x)
            return (vertical_dist, horizontal_dist)

        return min(candidates, key=distance_key)

    def _get_link_segments(
        self, link: dict, page: Page, segments_by_page: dict[int, list[SegmentBox]]
    ) -> Optional[tuple[SegmentBox, SegmentBox]]:
        rect = link["from"]
        source_box = Rectangle.from_coordinates(rect[0], rect[1], rect[2], rect[3])
        source_page_num = page.number + 1
        source_segments = segments_by_page.get(source_page_num, [])
        source_segment = self._find_closest_segment(source_box, source_segments)
        if not source_segment:
            return None

        dest_page_num = link.get("page", -1) + 1
        dest_segments = segments_by_page.get(dest_page_num, [])
        if not dest_segments:
            return None

        if "to" not in link:
            dest_box = Rectangle.from_coordinates(0, 0, 20, 20)
        else:
            dest = link["to"] * page.transformation_matrix
            dest_box = Rectangle.from_coordinates(dest[0], dest[1], dest[0] + 20, dest[1] + 20)

        dest_segment = self._find_closest_segment(dest_box, dest_segments)
        if not dest_segment:
            return None

        return source_segment, dest_segment

    def _extract_links_by_segments(
        self, pdf_path: Path, vgt_segments: list[SegmentBox]
    ) -> tuple[dict[SegmentBox, list[Link]], dict[SegmentBox, list[Link]]]:
        links_by_source: dict[SegmentBox, list[Link]] = {}
        links_by_dest: dict[SegmentBox, list[Link]] = {}

        segments_by_page: dict[int, list[SegmentBox]] = {}
        for segment in vgt_segments:
            segments_by_page.setdefault(segment.page_number, []).append(segment)

        doc = fitz.open(pdf_path)
        try:
            for page_num in range(len(doc)):
                page: Page = doc[page_num]
                links = page.get_links()
                for link in links:
                    if "page" not in link:
                        continue
                    rect = link["from"]
                    text = page.get_text("text", clip=rect).strip()
                    if not text:
                        continue
                    segments_pair = self._get_link_segments(link, page, segments_by_page)
                    if not segments_pair:
                        continue
                    source, dest = segments_pair
                    new_link = Link(source_segment=source, destination_segment=dest, text=text)
                    links_by_source.setdefault(source, []).append(new_link)
                    links_by_dest.setdefault(dest, []).append(new_link)
        finally:
            doc.close()

        return links_by_source, links_by_dest

    def _insert_reference_links(self, segment_text: str, links: list[Link]) -> str:
        offset = 0
        for link in links:
            start_idx = segment_text.find(link.text, offset)
            if start_idx == -1:
                continue
            escaped_text = link.text.replace("[", "\\[").replace("]", "\\]")
            md_link = f"[{escaped_text}](#{link.destination_segment.id})"
            segment_text = segment_text[:start_idx] + md_link + segment_text[start_idx + len(link.text) :]
            offset = start_idx + len(md_link)
        return segment_text

    def _process_picture_segment(
        self,
        segment: SegmentBox,
        pdf_images: list[Image],
        pdf_path: Path,
        picture_id: int,
        dpi: int = 72,
        extracted_images: Optional[list[ExtractedImage]] = None,
        user_base_name: Optional[str] = None,
    ) -> str:

        if extracted_images is None:
            return ""

        segment_box = Rectangle.from_width_height(segment.left, segment.top, segment.width, segment.height)
        image = pdf_images[segment.page_number - 1]
        left, top, right, bottom = segment_box.left, segment_box.top, segment_box.right, segment_box.bottom
        if dpi != 72:
            left = left * dpi / 72
            top = top * dpi / 72
            right = right * dpi / 72
            bottom = bottom * dpi / 72
        cropped = image.crop((left, top, right, bottom))

        base_name = user_base_name if user_base_name else pdf_path.stem
        image_name = f"{base_name}_{segment.page_number}_{picture_id}.png"

        img_buffer = io.BytesIO()
        cropped.save(img_buffer, format="PNG")
        extracted_images.append(ExtractedImage(image_data=img_buffer.getvalue(), filename=image_name))
        return f"<span id='{segment.id}'></span>\n" + f"<img src='{base_name}_pictures/{image_name}' alt=''>\n\n"

    def _process_table_segment(self, segment: SegmentBox) -> str:
        return f"<span id='{segment.id}'></span>\n" + segment.text + "\n\n"

    def _get_token_content(self, token: PdfToken) -> str:
        if self.output_format == OutputFormat.HTML:
            return token.content_html
        else:
            return token.content_markdown

    def _get_styled_content(self, token: PdfToken, content: str) -> str:
        if self.output_format == OutputFormat.HTML:
            styled = token.token_style.get_styled_content_html(content)
            styled = token.token_style.script_type.get_styled_content(styled)
            styled = token.token_style.list_level.get_styled_content_html(styled)
            return token.token_style.hyperlink_style.get_styled_content_html(styled)
        else:
            styled = token.token_style.get_styled_content_markdown(content)
            styled = token.token_style.script_type.get_styled_content(styled)
            styled = token.token_style.list_level.get_styled_content_markdown(styled)
            return token.token_style.hyperlink_style.get_styled_content_markdown(styled)

    def _process_title_segment(self, tokens: list[PdfToken], segment: SegmentBox) -> str:
        if not tokens:
            return ""

        title_type = tokens[0].token_style.title_type
        content = " ".join([self._get_styled_content(token, token.content) for token in tokens])
        if self.output_format == OutputFormat.HTML:
            content = title_type.get_styled_content_html(content)
        else:
            content = title_type.get_styled_content_markdown(content)
        anchor = f"<span id='{segment.id}'></span>\n"
        return anchor + content + "\n\n"

    def _process_regular_segment(
        self,
        tokens: list[PdfToken],
        segment: SegmentBox,
        links_by_source: dict[SegmentBox, list[Link]],
        links_by_dest: dict[SegmentBox, list[Link]],
    ) -> str:
        if not tokens:
            return ""
        content = " ".join(self._get_token_content(t) for t in tokens)
        if segment in links_by_source:
            content = self._insert_reference_links(content, links_by_source[segment])
        if segment in links_by_dest:
            content = f"<span id='{segment.id}'></span>\n" + content
        return content + "\n\n"

    def _get_table_of_contents(self, vgt_segments: list[SegmentBox]) -> str:
        title_segments = [s for s in vgt_segments if s.type in {TokenType.TITLE, TokenType.SECTION_HEADER}]
        table_of_contents = "# Table of Contents\n\n"
        for segment in title_segments:
            if not segment.text.strip():
                continue
            first_word = segment.text.split()[0]
            indentation = max(0, first_word.count(".") - 1)
            content = "  " * indentation + "- [" + segment.text + "](#" + segment.id + ")\n"
            table_of_contents += content
        table_of_contents += "\n"
        return table_of_contents + "\n\n"

    def _set_segment_ids(self, vgt_segments: list[SegmentBox]) -> None:
        segments_by_page: dict[int, list[SegmentBox]] = {}
        for segment in vgt_segments:
            segments_by_page.setdefault(segment.page_number, []).append(segment)
        for page_number, segments in segments_by_page.items():
            for segment_index, segment in enumerate(segments):
                segment.id = f"page-{page_number}-{segment_index}"

    def _get_styled_content_parts(
        self,
        pdf_path: Path,
        vgt_segments: list[SegmentBox],
        extract_toc: bool = False,
        dpi: int = 120,
        extracted_images: Optional[list[ExtractedImage]] = None,
        user_base_name: Optional[str] = None,
    ) -> str:
        pdf_labels: PdfLabels = self._create_pdf_labels_from_segments(vgt_segments)
        pdf_features: PdfFeatures = PdfFeatures.from_pdf_path(pdf_path)
        pdf_features.set_token_types(pdf_labels)
        pdf_features.set_token_styles()

        self._set_segment_ids(vgt_segments)
        content_parts: list[str] = []
        if extract_toc:
            content_parts.append(self._get_table_of_contents(vgt_segments))

        links_by_source, links_by_dest = self._extract_links_by_segments(pdf_path, vgt_segments)

        picture_segments = [s for s in vgt_segments if s.type == TokenType.PICTURE]
        pdf_images: list[Image] = convert_from_path(pdf_path, dpi=dpi) if picture_segments else []

        for page in pdf_features.pages:
            segments_in_page = [s for s in vgt_segments if s.page_number == page.page_number]
            picture_id = 0
            for segment in segments_in_page:
                seg_box = Rectangle.from_width_height(segment.left, segment.top, segment.width, segment.height)
                tokens_in_seg = [t for t in page.tokens if t.bounding_box.get_intersection_percentage(seg_box) > 50]

                if segment.type == TokenType.PICTURE:
                    content_parts.append(
                        self._process_picture_segment(
                            segment, pdf_images, pdf_path, picture_id, dpi, extracted_images, user_base_name
                        )
                    )
                    picture_id += 1
                elif segment.type == TokenType.TABLE:
                    content_parts.append(self._process_table_segment(segment))
                elif segment.type in {TokenType.TITLE, TokenType.SECTION_HEADER}:
                    content_parts.append(self._process_title_segment(tokens_in_seg, segment))
                elif segment.type == TokenType.FORMULA:
                    content_parts.append(segment.text + "\n\n")
                else:
                    content_parts.append(
                        self._process_regular_segment(tokens_in_seg, segment, links_by_source, links_by_dest)
                    )

        return content_parts
