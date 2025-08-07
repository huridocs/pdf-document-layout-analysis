from abc import ABC, abstractmethod
from typing import List, Optional, Union
from starlette.responses import Response
from domain.SegmentBox import SegmentBox


class MarkdownConversionService(ABC):

    @abstractmethod
    def convert_to_markdown(
        self,
        pdf_content: bytes,
        segments: List[SegmentBox],
        extract_toc: bool = False,
        dpi: int = 120,
        output_file: Optional[str] = None,
    ) -> Union[str, Response]:
        pass
