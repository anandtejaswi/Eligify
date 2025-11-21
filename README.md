# sem_three_eligify

## Overview
ELIGIFY is a simple Flask-backed app with a frontend for exam eligibility checks. The backend exposes an endpoint to parse PDF files. PDF parsing now uses OCR via PyTesseract.

## OCR Setup (Windows)
To use the OCR-based PDF parser, install these prerequisites:

- Install Tesseract OCR: https://github.com/UB-Mannheim/tesseract/wiki
  - Default install path: `C:\Program Files\Tesseract-OCR\tesseract.exe`
  - Optionally set env var `TESSERACT_CMD` to the full path of `tesseract.exe`.

- Install Poppler for Windows (required by `pdf2image`):
  - Download from: https://github.com/oschwartz10612/poppler-windows/releases/
  - Add the `bin` folder to your system `PATH`.

## Python Dependencies
Install Python packages:

```
pip install -r requirements.txt
```

`requirements.txt` includes: `flask`, `pytesseract`, `pdf2image`, `Pillow`.

## Run the App
Start the Flask server:

```
python app.py
```

Visit `http://localhost:3000/` in a browser.

## PDF Parsing API
- Endpoint: `POST /api/parse-pdf`
- Form field: `file` (PDF)
- Response:

```
{
  "text": "...extracted OCR text..."
}
```
