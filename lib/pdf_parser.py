from io import BytesIO
from typing import Union
import os

from PIL import Image
import pytesseract
from pdf2image import convert_from_bytes, convert_from_path


def _configure_tesseract_from_env() -> None:
    cmd = os.getenv("TESSERACT_CMD")
    if cmd:
        pytesseract.pytesseract.tesseract_cmd = cmd
    else:
        # Common default path on Windows installs; ignore if not present
        default_win_path = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
        if os.path.exists(default_win_path):
            pytesseract.pytesseract.tesseract_cmd = default_win_path


def _images_from_input(input_obj: Union[bytes, bytearray, str, BytesIO], dpi: int = 300):
    if isinstance(input_obj, (bytes, bytearray)):
        return convert_from_bytes(input_obj, dpi=dpi)
    if hasattr(input_obj, "read"):
        # file-like object
        data = input_obj.read()
        return convert_from_bytes(data, dpi=dpi)
    if isinstance(input_obj, str):
        return convert_from_path(input_obj, dpi=dpi)
    raise ValueError("Unsupported input")


def parse_pdf(input_obj: Union[bytes, bytearray, str, BytesIO], dpi: int = 300, ocr_lang: str = "eng") -> str:
    """
    Extract text from a PDF using OCR (PyTesseract).

    - input_obj: bytes, file-like, or filesystem path to a PDF
    - dpi: rasterization DPI for converting PDF pages to images
    - ocr_lang: language code for Tesseract (default 'eng')
    """
    _configure_tesseract_from_env()

    images = _images_from_input(input_obj, dpi=dpi)

    texts = []
    for img in images:
        # Light preprocessing: convert to grayscale which often helps OCR
        if img.mode != "L":
            img = img.convert("L")
        text = pytesseract.image_to_string(img, lang=ocr_lang, config="--psm 6")
        texts.append(text)

    return "\n\n".join(t.strip() for t in texts if t)