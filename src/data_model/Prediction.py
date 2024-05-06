from dataclasses import dataclass

from pdf_features.Rectangle import Rectangle


@dataclass
class Prediction:
    bounding_box: Rectangle
    category_id: int
    score: float
