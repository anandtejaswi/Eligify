# sem_three_eligify

## Overview
ELIGIFY is a simple Flask-backed app with a frontend for exam eligibility checks. The backend exposes an endpoint to parse PDF files. PDF parsing now prefers the embedded text layer (PyPDF2) and falls back to OCR via Tesseract when needed.

## OCR Setup (Windows)
To use the OCR-based PDF parser, install these prerequisites:

- Install Tesseract OCR: https://github.com/UB-Mannheim/tesseract/wiki
  - Default install path: `C:\Program Files\Tesseract-OCR\tesseract.exe`
  - Optionally set env var `TESSERACT_CMD` to the full path of `tesseract.exe`.

- Install Poppler for Windows (required by `pdf2image`):
  - Download from: https://github.com/oschwartz10612/poppler-windows/releases/
  - Add the `bin` folder to your system `PATH`.
  - Alternatively, set environment variable `POPPLER_PATH` to the Poppler `bin` directory and the app will use it. Example:
    - PowerShell (current session): `$env:POPPLER_PATH = 'C:\\Tools\\poppler-24.08.0\\Library\\bin'`
    - Permanent: `setx POPPLER_PATH "C:\\Tools\\poppler-24.08.0\\Library\\bin"`

### Windows Quick Setup Commands

Run these in PowerShell:

```
# Set for current session
$env:TESSERACT_CMD = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
$env:POPPLER_PATH = 'C:\\Tools\\poppler-24.08.0\\Library\\bin'

# Persist for future sessions
setx TESSERACT_CMD "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
setx POPPLER_PATH "C:\\Tools\\poppler-24.08.0\\Library\\bin"
```

Note: `method="text"` does not require Poppler/Tesseract; `method="ocr"` requires both.

## Python Dependencies
Install Python packages:

```
pip install -r requirements.txt
```

`requirements.txt` includes: `flask`, `PyPDF2`, `pytesseract`, `pdf2image`, `Pillow`, `opencv-python`.

Notes:
- PyPDF2 is used to extract text from PDFs that have a selectable text layer (no extra system dependencies).
- OpenCV is used to pre-process scanned pages before OCR.

## Run the App
Start the Flask server:

```
python app.py
```

Visit `http://localhost:3000/` in a browser.

## PDF Parsing API
- Endpoint: `POST /api/parse-pdf`
- Form field: `file` (PDF)
- Optional query params:
  - `method`: `auto` (default), `text`, or `ocr`
  - `dpi`: integer DPI for rasterization (default `300`)

- Response:

```
{
  "text": "...extracted text...",
  "method": "auto"
}
```

### Example (curl)

```
curl -F "file=@C:\\path\\to\\your.pdf" "http://localhost:3000/api/parse-pdf?method=auto&dpi=300"
```

## How To Use (Library)

You can import and call the parser directly in Python code.

### Simple import and call

```
from lib.pdf_parser import extract_text_from_pdf

text = extract_text_from_pdf("lib/test_input.pdf")
print(text)
```

### Control parsing strategy

```
# Prefer text layer, fallback to OCR if empty (default)
text_auto = extract_text_from_pdf("lib/test_input.pdf", method="auto")

# Force text-layer only (PyPDF2)
text_text = extract_text_from_pdf("lib/test_input.pdf", method="text")

# Force OCR-only (Tesseract)
text_ocr = extract_text_from_pdf("lib/test_input.pdf", method="ocr", dpi=300)
```

### Using with uploaded files (Flask `request.files['file']`)

```
from flask import request
from lib.pdf_parser import extract_text_from_pdf

@app.post('/api/parse-pdf')
def parse_pdf_ep():
    f = request.files.get('file')
    if not f:
        return {"error": "No file uploaded."}, 400
    text = extract_text_from_pdf(f)  # defaults to method="auto"
    return {"text": text}
```
