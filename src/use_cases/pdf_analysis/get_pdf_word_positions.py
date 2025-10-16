import tempfile
import os
from pdf_features.PdfTextPosition import PdfTextPosition
from pdf_features.PdfWord import PdfWord


def get_pdf_word_positions(file_content: bytes) -> list[PdfWord]:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(file_content)
        tmp_path = tmp_file.name

    try:
        pdf_text_position = PdfTextPosition(tmp_path)
        return pdf_text_position.get_all_pdf_words()
    finally:
        os.unlink(tmp_path)
