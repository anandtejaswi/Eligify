from io import BytesIO
from typing import Union
import os

from PIL import Image
import pytesseract
from pdf2image import convert_from_bytes, convert_from_path
import re
try:
    import PyPDF2  # type: ignore
except Exception:
    PyPDF2 = None


def _configure_tesseract_from_env() -> None:
    cmd = os.getenv("TESSERACT_CMD")
    if cmd:
        pytesseract.pytesseract.tesseract_cmd = cmd
    else:
        # Common default path on Windows installs; ignore if not present
        default_win_path = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
        if os.path.exists(default_win_path):
            pytesseract.pytesseract.tesseract_cmd = default_win_path


def _is_ocr_available() -> bool:
    poppler_path = os.getenv("POPPLER_PATH") or ""
    pdftoppm = os.path.join(poppler_path, "pdftoppm.exe")
    pdftocairo = os.path.join(poppler_path, "pdftocairo.exe")
    poppler_ok = bool(poppler_path and (os.path.exists(pdftoppm) or os.path.exists(pdftocairo)))

    env_tess = os.getenv("TESSERACT_CMD")
    tess_attr = getattr(pytesseract.pytesseract, "tesseract_cmd", None)
    tess_cmd = env_tess or tess_attr
    tess_ok = bool(tess_cmd and os.path.exists(tess_cmd))

    return poppler_ok and tess_ok


def _images_from_input(input_obj: Union[bytes, bytearray, str, BytesIO], dpi: int = 300):
    poppler_path = os.getenv("POPPLER_PATH")
    if isinstance(input_obj, (bytes, bytearray)):
        return convert_from_bytes(input_obj, dpi=dpi, poppler_path=poppler_path)
    if hasattr(input_obj, "read"):
        data = input_obj.read()
        return convert_from_bytes(data, dpi=dpi, poppler_path=poppler_path)
    if isinstance(input_obj, str):
        return convert_from_path(input_obj, dpi=dpi, poppler_path=poppler_path)
    raise ValueError("Unsupported input")


def _bytes_from_input(input_obj: Union[bytes, bytearray, str, BytesIO]) -> bytes:
    if isinstance(input_obj, (bytes, bytearray)):
        return bytes(input_obj)
    if hasattr(input_obj, "read"):
        return input_obj.read()
    if isinstance(input_obj, str):
        with open(input_obj, "rb") as f:
            return f.read()
    raise ValueError("Unsupported input")


def _extract_text_layer(input_obj: Union[bytes, bytearray, str, BytesIO]) -> str:
    if PyPDF2 is None:
        return ""
    try:
        data = _bytes_from_input(input_obj)
        reader = PyPDF2.PdfReader(BytesIO(data))
        texts = []
        for page in reader.pages:
            t = page.extract_text() or ""
            if t.strip():
                texts.append(t)
        return "\n\n".join(texts).strip()
    except Exception:
        return ""


def parse_pdf(input_obj: Union[bytes, bytearray, str, BytesIO], dpi: int = 300, ocr_lang: str = "eng", method: str = "auto") -> str:
    """
    Extract text from a PDF using OCR (PyTesseract).

    - input_obj: bytes, file-like, or filesystem path to a PDF
    - dpi: rasterization DPI for converting PDF pages to images
    - ocr_lang: language code for Tesseract (default 'eng')
    """
    _configure_tesseract_from_env()
    method = (method or "auto").lower()

    if method in ("text", "auto"):
        text_layer = _extract_text_layer(input_obj)
        if method == "text":
            if text_layer and text_layer.strip():
                return text_layer
            return "No text layer found in PDF. Consider method='ocr' (requires Poppler + Tesseract)."
        if text_layer and len(text_layer.strip()) >= 20:
            return text_layer

    if method == "auto" and not _is_ocr_available():
        return "OCR prerequisites missing. Set POPPLER_PATH to Poppler 'bin' and TESSERACT_CMD to tesseract.exe."

    try:
        images = _images_from_input(input_obj, dpi=dpi)
    except Exception:
        if method == "ocr":
            return "Failed to rasterize PDF. Ensure Poppler is installed and POPPLER_PATH is set correctly."
        return "Could not rasterize pages for OCR. Check Poppler installation and POPPLER_PATH."

    texts = []
    for img in images:
        if img.mode != "L":
            img = img.convert("L")
        try:
            text = pytesseract.image_to_string(img, lang=ocr_lang, config="--psm 6")
        except Exception:
            text = ""
        texts.append(text)

    merged = "\n\n".join(t.strip() for t in texts if t)
    if merged:
        return merged
    return "OCR produced no text. Verify Tesseract installation or try increasing DPI/improving image quality."


def extract_text_from_pdf(
    input_obj: Union[bytes, bytearray, str, BytesIO],
    dpi: int = 300,
    ocr_lang: str = "eng",
    method: str = "auto",
) -> str:
    return parse_pdf(input_obj, dpi=dpi, ocr_lang=ocr_lang, method=method)


def extract_text_with_info(
    input_obj: Union[bytes, bytearray, str, BytesIO],
    dpi: int = 300,
    ocr_lang: str = "eng",
    method: str = "auto",
):
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

    text_layer = _extract_text_layer(input_obj)
    info["text_layer_found"] = bool(text_layer and text_layer.strip())

    if method in ("text", "auto") and info["text_layer_found"]:
        info["decided_method"] = "text"
        info["text"] = text_layer
        return info

    should_ocr = method == "ocr" or (method == "auto" and not info["text_layer_found"])
    if not should_ocr:
        info["warnings"].append("No text layer found and OCR not requested.")
        return info

    if method == "auto" and not info["ocr_available"]:
        info["decided_method"] = "ocr"
        info["warnings"].append("OCR prerequisites missing (POPPLER_PATH/TESSERACT_CMD).")
        return info

    try:
        images = _images_from_input(input_obj, dpi=dpi)
        info["rasterize_ok"] = True
    except Exception:
        info["decided_method"] = "ocr"
        info["warnings"].append("Failed to rasterize PDF (Poppler not installed or invalid POPPLER_PATH).")
        return info

    texts = []
    for img in images:
        if img.mode != "L":
            img = img.convert("L")
        try:
            t = pytesseract.image_to_string(img, lang=ocr_lang, config="--psm 6")
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


def extract_headings_and_bullets(
    input_obj: Union[bytes, bytearray, str, BytesIO],
    dpi: int = 300,
    ocr_lang: str = "eng",
    method: str = "auto",
) -> dict:
    text = parse_pdf(input_obj, dpi=dpi, ocr_lang=ocr_lang, method=method)
    if not isinstance(text, str) or not text.strip():
        return {"headings": [], "items": [], "error": text or "No text"}
    lines = [re.sub(r"\s+", " ", l).strip() for l in text.splitlines() if l.strip()]
    bullets = []
    heads = []
    for l in lines:
        if re.match(r"^(\d+\.|\-|•|●|▪|‣)\s+", l):
            bullets.append(l)
        elif len(l.split()) <= 6:
            heads.append(l)
    return {"headings": heads, "items": bullets}


def extract_modification_items(
    input_obj: Union[bytes, bytearray, str, BytesIO],
    dpi: int = 300,
    ocr_lang: str = "eng",
    method: str = "auto",
) -> list:
    r = extract_headings_and_bullets(input_obj, dpi=dpi, ocr_lang=ocr_lang, method=method)
    if "error" in r:
        return []
    items = []
    for s in r.get("items", []):
        s2 = re.sub(r"^[\-•●▪‣]+\s+", "", s)
        items.append(s2)
    return items


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

    import unicodedata
    def _normalize(s: str) -> str:
        s2 = unicodedata.normalize('NFKC', s)
        s2 = s2.replace('\u2013', '-').replace('\u2014', '-').replace('\u2212', '-')
        s2 = s2.replace('\u00A0', ' ').replace('\u2009', ' ').replace('\u2026', '...')
        s2 = s2.replace('–', '-').replace('—', '-')
        s2 = re.sub(r"\s+/\s+", "/", s2)
        s2 = re.sub(r"\s+", " ", s2)
        return s2
    norm = _normalize(text)
    lines = [l.strip() for l in norm.splitlines() if l.strip()]
    joined = " \n ".join(lines)

    def find_first(patterns):
        for p in patterns:
            m = re.search(p, joined, flags=re.IGNORECASE)
            if m:
                return m.group(1).strip()
        return None

    sep = r"[:\-–—]"
    name = find_first([
        rf"(?:Student\s*name|Name(?: of the Candidate)?|Student Name|Candidate Name)\s*{sep}\s*(.+?)\s*(?:\n|$)",
    ])
    father_name = find_first([
        r"(?:Father(?:'s)? Name|Guardian Name)\s*[:\-]\s*(.+?)\s*(?:\n|$)",
    ])
    roll_number = find_first([
        rf"(?:Roll(?:\s*No\.?|\s*Number)?|Roll number|Enrollment No|Enrolment No)\s*{sep}\s*([A-Za-z0-9\-/]+)",
    ])
    registration_number = find_first([
        r"(?:Registration No|Reg\.? No|Registration Number)\s*[:\-]\s*([A-Za-z0-9\-/]+)",
    ])
    dob = find_first([
        rf"(?:Date of Birth|DOB)\s*{sep}\s*([0-3]?\d[\-/][0-1]?\d[\-/][12]\d{3})",
        rf"(?:Date of Birth|DOB)\s*{sep}\s*([0-3]?\d\s+[A-Za-z]{3,9}\s+[12]\d{3})",
    ])
    exam = find_first([
        rf"(?:Examination|Exam|Course|Programme|Program)\s*{sep}\s*(.+?)\s*(?:\n|$)",
    ])
    year = find_first([
        rf"(?:Year(?: of Passing)?|Passing Year|Session|Year)\s*{sep}\s*([12]\d{3})",
    ])
    university = find_first([
        rf"(?:Board/University|University|Board)\s*{sep}\s*(.+?)\s*(?:\n|$)",
    ])
    college = find_first([
        rf"(?:College|Institute|School)\s*{sep}\s*(.+?)\s*(?:\n|$)",
    ])
    percentage = find_first([
        rf"(?:Percentage(?:\s*/\s*CGPA)?|Marks Percentage)\s*{sep}\s*([0-9]{{1,3}}(?:\.[0-9]+)?)%?",
        rf"(?:Percent)\s*{sep}\s*([0-9]{{1,3}}(?:\.[0-9]+)?)%?",
        rf"(?:Percentage\s*/\s*CGPA)\s*{sep}\s*([0-9]{{1,3}}(?:\.[0-9]+)?)%?",
    ])
    cgpa = find_first([
        rf"(?:CGPA|SGPA)\s*{sep}\s*([0-9](?:\.[0-9]+)?)",
        rf"(?:CGPA|SGPA)\s*{sep}\s*([0-9](?:\.[0-9]+)?)(?:\s*/\s*10)?",
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
        rf"^([A-Za-z][A-Za-z0-9 &./()\-]{{2,}})\s*(?:{sep}\s*)?([0-9]{{1,3}}(?:\.[0-9]+)?)(?:\s*/\s*([0-9]{{1,3}}))?\s*(?:([A-Za-z]{{1,3}}))?$",
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
            try:
                max_val = float(m.group(3)) if m.group(3) else None
            except Exception:
                max_val = None
            grade_val = (m.group(4) or "").strip() or None
            subjects.append({"name": subj_name, "marks": marks_val, "max": max_val, "grade": grade_val})

    total_marks = None
    max_marks = None
    m_total = re.search(rf"(?:Total\s*marks?|Aggregate|Marks\s*Obtained)\s*{sep}\s*([0-9]{{1,4}})(?:\s*(?:out\s*of|of|/)?\s*([0-9]{{1,4}}))", joined, flags=re.IGNORECASE)
    if m_total:
        try:
            total_marks = float(m_total.group(1))
            max_marks = float(m_total.group(2))
        except Exception:
            total_marks = None
            max_marks = None
    else:
        sm = sum((s.get("marks") or 0) for s in subjects if isinstance(s.get("marks"), (int, float)))
        sx = sum((s.get("max") or 0) for s in subjects if isinstance(s.get("max"), (int, float)))
        total_marks = sm if sm > 0 else None
        # If denominators missing, infer from typical maxima (e.g., 100 per subject)
        if sx <= 0 and sm > 0 and len(subjects) > 0:
            sx = 100.0 * len([1 for s in subjects if s.get("marks") is not None])
        max_marks = sx if sx > 0 else None

    calculated_percentage = None
    if percentage:
        try:
            calculated_percentage = float(percentage)
        except Exception:
            calculated_percentage = None
    elif cgpa:
        try:
            calculated_percentage = float(cgpa) * 9.5
        except Exception:
            calculated_percentage = None
    elif total_marks and max_marks and max_marks > 0:
        try:
            calculated_percentage = (float(total_marks) / float(max_marks)) * 100.0
        except Exception:
            calculated_percentage = None

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
        "total_marks": total_marks,
        "max_marks": max_marks,
        "calculated_percentage": calculated_percentage,
        "subjects": subjects,
    }
    subjects_map = {s.get("name"): {"marks": s.get("marks"), "max": s.get("max"), "grade": s.get("grade")} for s in subjects if s.get("name")}
    total_outoff = f"{int(total_marks) if isinstance(total_marks, (int, float)) else total_marks}/{int(max_marks) if isinstance(max_marks, (int, float)) else max_marks}" if (total_marks is not None and max_marks is not None) else None
    pref_val = result["percentage"] if result["percentage"] is not None else (result["cgpa"] if result["cgpa"] is not None else result["calculated_percentage"])
    result.update({
        "student_name": name,
        "board_university": university,
        "subjects_and_marks": subjects_map,
        "total_marks_obtained_outoff": total_outoff,
        "percentage_cgpa": pref_val,
    })
    return result
