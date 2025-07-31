from abc import ABC, abstractmethod
from pathlib import Path
from typing import List
from starlette.responses import FileResponse


class VisualizationService(ABC):
    @abstractmethod
    def create_pdf_visualization(self, pdf_path: Path, segment_boxes: List[dict]) -> Path:
        pass

    @abstractmethod
    def get_visualization_response(self, pdf_path: Path) -> FileResponse:
        pass
