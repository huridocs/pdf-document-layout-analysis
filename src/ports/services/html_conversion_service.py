from abc import ABC, abstractmethod
from typing import Optional, Union
from starlette.responses import Response
from domain.SegmentBox import SegmentBox


class HtmlConversionService(ABC):

    @abstractmethod
    def convert_to_html(
        self,
        pdf_content: bytes,
        segments: list[SegmentBox],
        extract_toc: bool = False,
        dpi: int = 120,
        output_file: Optional[str] = None,
        target_languages: Optional[list[str]] = None,
        translation_model: str = "gpt-oss",
    ) -> Union[str, Response]:
        pass
