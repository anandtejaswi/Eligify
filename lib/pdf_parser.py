from io import BytesIO
from typing import Union
import os
import re

from PIL import Image
import pytesseract
from pdf2image import convert_from_bytes, convert_from_path
import cv2
import numpy as np

# Optional text-layer extractor
try:
    import PyPDF2  # type: ignore
except Exception:
    PyPDF2 = None


def _is_ocr_available() -> bool:
    """Check if OCR prerequisites appear available (Poppler + Tesseract).

    More robust checks: verify Poppler executables in the POPPLER_PATH and
    resolve Tesseract either from env var or configured attribute.
    """
    poppler_path = os.getenv("POPPLER_PATH") or ""
    pdftoppm = os.path.join(poppler_path, "pdftoppm.exe")
    pdftocairo = os.path.join(poppler_path, "pdftocairo.exe")
    poppler_ok = bool(poppler_path and (os.path.exists(pdftoppm) or os.path.exists(pdftocairo)))

    env_tess = os.getenv("TESSERACT_CMD")
    tess_attr = getattr(pytesseract.pytesseract, "tesseract_cmd", None)
    tess_cmd = env_tess or tess_attr
    tess_ok = bool(tess_cmd and os.path.exists(tess_cmd))

    return poppler_ok and tess_ok

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
    # Allow explicit Poppler path via environment variable
    poppler_path = os.getenv("POPPLER_PATH")

    if isinstance(input_obj, (bytes, bytearray)):
        return convert_from_bytes(input_obj, dpi=dpi, poppler_path=poppler_path)
    if hasattr(input_obj, "read"):
        # file-like object
        data = input_obj.read()
        return convert_from_bytes(data, dpi=dpi, poppler_path=poppler_path)
    if isinstance(input_obj, str):
        return convert_from_path(input_obj, dpi=dpi, poppler_path=poppler_path)
    raise ValueError("Unsupported input")


def _bytes_from_input(input_obj: Union[bytes, bytearray, str, BytesIO]) -> bytes:
    """Normalize supported inputs to PDF bytes."""
    if isinstance(input_obj, (bytes, bytearray)):
        return bytes(input_obj)
    if hasattr(input_obj, "read"):
        return input_obj.read()
    if isinstance(input_obj, str):
        with open(input_obj, "rb") as f:
            return f.read()
    raise ValueError("Unsupported input")


def _extract_text_layer(input_obj: Union[bytes, bytearray, str, BytesIO]) -> str:
    """
    Extract text using the PDF's embedded text layer (if available) via PyPDF2.
    Returns an empty string if PyPDF2 is unavailable or if no text was found.
    """
    if PyPDF2 is None:
        return ""

    try:
        # Use bytes for consistent handling across input types
        data = _bytes_from_input(input_obj)
        reader = PyPDF2.PdfReader(BytesIO(data))
        texts = []
        for page in reader.pages:
            t = page.extract_text() or ""
            if t.strip():
                texts.append(t)
        return "\n\n".join(texts).strip()
    except Exception:
        # Any parsing failures -> fall back to OCR
        return ""


def parse_pdf(
    input_obj: Union[bytes, bytearray, str, BytesIO],
    dpi: int = 300,
    ocr_lang: str = "eng",
    method: str = "auto",
) -> str:
    """
    Extract text from a PDF.

    Strategies:
    - method='text': Use embedded text layer only (PyPDF2)
    - method='ocr': Use OCR on rasterized pages only (Tesseract)
    - method='auto': Prefer text layer; fallback to OCR if text seems empty

    - input_obj: bytes, file-like, or filesystem path to a PDF
    - dpi: rasterization DPI for converting PDF pages to images
    - ocr_lang: language code for Tesseract (default 'eng')
    """
    _configure_tesseract_from_env()
    method = (method or "auto").lower()

    # Try text-layer first when requested or in auto-mode
    if method in ("text", "auto"):
        text_layer = _extract_text_layer(input_obj)
        if method == "text":
            if text_layer and text_layer.strip():
                return text_layer
            return (
                "No text layer found in PDF. Consider method='ocr' (requires Poppler + Tesseract)."
            )
        # In auto mode, only fallback if the text layer seems empty
        if text_layer and len(text_layer.strip()) >= 20:
            return text_layer

    # If in auto-mode and OCR prerequisites are missing, return empty string gracefully
    if method == "auto" and not _is_ocr_available():
        return (
            "OCR prerequisites missing. Set POPPLER_PATH to Poppler 'bin' (folder containing pdftoppm.exe) and TESSERACT_CMD to tesseract.exe."
        )

    # OCR path
    try:
        images = _images_from_input(input_obj, dpi=dpi)
    except Exception:
        # Rasterization failed (likely Poppler missing or corrupt PDF)
        if method == "ocr":
            return (
                "Failed to rasterize PDF. Ensure Poppler is installed and POPPLER_PATH is set correctly."
            )
        # In auto-mode, give a helpful message
        return (
            "Could not rasterize pages for OCR. Check Poppler installation and POPPLER_PATH."
        )

    texts = []
    for img in images:
        # Convert PIL image to OpenCV (numpy array)
        arr = np.array(img)
        if img.mode == "RGBA":
            arr = cv2.cvtColor(arr, cv2.COLOR_RGBA2RGB)
        elif img.mode == "RGB":
            pass
        elif img.mode == "L":
            arr = cv2.cvtColor(arr, cv2.COLOR_GRAY2RGB)

        # Grayscale
        gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)

        # Denoise lightly
        gray = cv2.bilateralFilter(gray, 9, 75, 75)

        # Binarize with Otsu
        _, thr = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Optional: small morphological opening to remove specks
        kernel = np.ones((1, 1), np.uint8)
        thr = cv2.morphologyEx(thr, cv2.MORPH_OPEN, kernel)

        try:
            text = pytesseract.image_to_string(thr, lang=ocr_lang, config="--psm 6")
        except Exception:
            # OCR failed (likely Tesseract not installed/configured) -> describe
            text = ""
        texts.append(text)

    merged = "\n\n".join(t.strip() for t in texts if t)
    if merged:
        return merged
    # No OCR text
    return (
        "OCR produced no text. Verify Tesseract installation or try increasing DPI/improving image quality."
    )


def extract_text_from_pdf(
    input_obj: Union[bytes, bytearray, str, BytesIO],
    dpi: int = 300,
    ocr_lang: str = "eng",
    method: str = "auto",
) -> str:
    """
    Convenience alias that mirrors `parse_pdf` for simpler imports and usage.

    Example:
        text = extract_text_from_pdf("lib/test_input.pdf")
    """
    return parse_pdf(input_obj, dpi=dpi, ocr_lang=ocr_lang, method=method)


def extract_text_with_info(
    input_obj: Union[bytes, bytearray, str, BytesIO],
    dpi: int = 300,
    ocr_lang: str = "eng",
    method: str = "auto",
):
    """
    Extract text but also return diagnostic information explaining what happened.

    Returns a dict with keys:
    - text: extracted text (may be empty)
    - decided_method: 'text' | 'ocr' | 'none'
    - text_layer_found: bool
    - ocr_available: bool
    - rasterize_ok: bool
    - ocr_ok: bool
    - warnings: list of strings describing why OCR was skipped/failing, etc.
    - env: { poppler_path, tesseract_cmd }
    """
    _configure_tesseract_from_env()
    method = (method or "auto").lower()

    info = {
        "text": "",
        "decided_method": "none",
        "text_layer_found": False,
        "ocr_available": _is_ocr_available(),
        "rasterize_ok": False,
        "ocr_ok": False,
        "warnings": [],
        "env": {
            "poppler_path": os.getenv("POPPLER_PATH"),
            "tesseract_cmd": getattr(pytesseract.pytesseract, "tesseract_cmd", None),
        },
    }

    # Text layer attempt
    text_layer = _extract_text_layer(input_obj)
    info["text_layer_found"] = bool(text_layer and text_layer.strip())

    if method in ("text", "auto") and info["text_layer_found"]:
        info["decided_method"] = "text"
        info["text"] = text_layer
        return info

    # Decide if we should attempt OCR
    should_ocr = method == "ocr" or (method == "auto" and not info["text_layer_found"])
    if not should_ocr:
        # No text layer and not instructed to OCR -> return empty
        info["warnings"].append("No text layer found and OCR not requested.")
        return info

    # If OCR prerequisites missing and method is auto, explain and return
    if method == "auto" and not info["ocr_available"]:
        info["decided_method"] = "ocr"
        info["warnings"].append("OCR prerequisites missing (POPPLER_PATH/TESSERACT_CMD).")
        return info

    # Try rasterization
    try:
        images = _images_from_input(input_obj, dpi=dpi)
        info["rasterize_ok"] = True
    except Exception:
        info["decided_method"] = "ocr"
        info["warnings"].append("Failed to rasterize PDF (Poppler not installed or invalid POPPLER_PATH).")
        return info

    # Try OCR per page
    texts = []
    for img in images:
        arr = np.array(img)
        if img.mode == "RGBA":
            arr = cv2.cvtColor(arr, cv2.COLOR_RGBA2RGB)
        elif img.mode == "L":
            arr = cv2.cvtColor(arr, cv2.COLOR_GRAY2RGB)
        gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
        gray = cv2.bilateralFilter(gray, 9, 75, 75)
        _, thr = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        kernel = np.ones((1, 1), np.uint8)
        thr = cv2.morphologyEx(thr, cv2.MORPH_OPEN, kernel)
        try:
            t = pytesseract.image_to_string(thr, lang=ocr_lang, config="--psm 6")
        except Exception:
            t = ""
        texts.append(t)

    merged = "\n\n".join(s.strip() for s in texts if s)
    info["decided_method"] = "ocr"
    info["ocr_ok"] = bool(merged)
    if not info["ocr_ok"]:
        info["warnings"].append("OCR produced no text. Check Tesseract installation or image quality.")
    info["text"] = merged
    return info


def extract_marksheet_fields(
    input_obj: Union[bytes, bytearray, str, BytesIO],
    dpi: int = 300,
    ocr_lang: str = "eng",
    method: str = "auto",
) -> dict:
    """Return key–value fields typically present on marksheets/degrees.

    If extraction fails, returns {"error": <reason>}.
    """
    text = parse_pdf(input_obj, dpi=dpi, ocr_lang=ocr_lang, method=method)

    issue_markers = (
        "No text layer found",
        "OCR prerequisites missing",
        "Failed to rasterize",
        "Could not rasterize",
        "OCR produced no text",
    )
    if not text or any(m in text for m in issue_markers):
        return {"error": text or "No text extracted"}

    lines = [l.strip() for l in text.splitlines() if l.strip()]
    joined = " \n ".join(lines)

    def find_first(patterns):
        for p in patterns:
            m = re.search(p, joined, flags=re.IGNORECASE)
            if m:
                return m.group(1).strip()
        return None

    name = find_first([
        r"(?:Name(?: of the Candidate)?|Student Name|Candidate Name)\s*[:\-]\s*(.+?)\s*(?:\n|$)",
    ])
    father_name = find_first([
        r"(?:Father(?:'s)? Name|Guardian Name)\s*[:\-]\s*(.+?)\s*(?:\n|$)",
    ])
    roll_number = find_first([
        r"(?:Roll(?:\s*No\.?|\s*Number)?|Enrollment No|Enrolment No)\s*[:\-]\s*([A-Za-z0-9\-/]+)",
    ])
    registration_number = find_first([
        r"(?:Registration No|Reg\.? No|Registration Number)\s*[:\-]\s*([A-Za-z0-9\-/]+)",
    ])
    dob = find_first([
        r"(?:Date of Birth|DOB)\s*[:\-]\s*([0-3]?\d[\-/][0-1]?\d[\-/][12]\d{3})",
        r"(?:Date of Birth|DOB)\s*[:\-]\s*([0-3]?\d\s+[A-Za-z]{3,9}\s+[12]\d{3})",
    ])
    exam = find_first([
        r"(?:Examination|Exam|Course|Programme|Program)\s*[:\-]\s*(.+?)\s*(?:\n|$)",
    ])
    year = find_first([
        r"(?:Year of Passing|Passing Year|Session|Year)\s*[:\-]\s*([12]\d{3})",
    ])
    university = find_first([
        r"(?:University|Board)\s*[:\-]\s*(.+?)\s*(?:\n|$)",
    ])
    college = find_first([
        r"(?:College|Institute|School)\s*[:\-]\s*(.+?)\s*(?:\n|$)",
    ])
    percentage = find_first([
        r"(?:Percentage|Marks Percentage)\s*[:\-]\s*([0-9]{1,3}(?:\.[0-9]+)?)%?",
    ])
    cgpa = find_first([
        r"(?:CGPA|SGPA)\s*[:\-]\s*([0-9](?:\.[0-9]+)?)",
    ])

    subjects = []
    exclude_starts = (
        "name",
        "roll",
        "enrol",
        "reg",
        "date",
        "exam",
        "course",
        "program",
        "university",
        "board",
        "college",
        "institute",
        "school",
        "percentage",
        "cgpa",
        "sgpa",
    )
    subj_pattern = re.compile(
        r"^([A-Za-z][A-Za-z0-9 &./()\-]{2,})\s+([0-9]{1,3}(?:\.[0-9]+)?)(?:\s*/\s*[0-9]{1,3})?\s*(?:([A-Za-z]{1,3}))?$",
        flags=re.IGNORECASE,
    )
    for line in lines:
        low = line.lower()
        if any(low.startswith(s) for s in exclude_starts):
            continue
        m = subj_pattern.match(line)
        if m:
            subj_name = m.group(1).strip()
            try:
                marks_val = float(m.group(2))
            except Exception:
                marks_val = None
            grade_val = (m.group(3) or "").strip() or None
            subjects.append({"name": subj_name, "marks": marks_val, "grade": grade_val})

    result = {
        "name": name,
        "father_name": father_name,
        "roll_number": roll_number,
        "registration_number": registration_number,
        "dob": dob,
        "exam": exam,
        "year": year,
        "university": university,
        "college": college,
        "percentage": float(percentage) if percentage else None,
        "cgpa": float(cgpa) if cgpa else None,
        "subjects": subjects,
    }
    return result