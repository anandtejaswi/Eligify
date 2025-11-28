# ELIGIFY

ELIGIFY is a Flask web application that helps candidates find exams they are eligible for and verify academic credentials by parsing PDFs or images of marksheets. The project includes a secure API, a Tailwind-based UI, and optional Google Sign-In.

## Features
- Exam browsing with eligibility checks on the client and server (`services/exam_repository.py`).
- PDF and image parsing for marksheets with text-layer extraction and OCR fallback (`lib/pdf_parser.py`).
- Secure file upload validation, rate limiting, and response sanitization (`middleware/security.py`).
- Optional Google Sign-In for authenticated API usage (`controllers/auth_controller.py`).
- SQLite by default, configurable `DATABASE_URL` for other databases (`services/db.py`).

## Tech Stack
- Backend: `Flask`, `SQLAlchemy`
- Parsing/OCR: `PyPDF2`, `pdf2image`, `pytesseract`, `Pillow`, `opencv-python`
- Frontend: Tailwind via CDN, vanilla JS modules under `static/js`

## Quick Start
1. Create a virtual environment: `python -m venv .venv`
2. Upgrade pip: `.\.venv\Scripts\python.exe -m pip install --upgrade pip`
3. Install dependencies: `.\.venv\Scripts\python.exe -m pip install -r requirements.txt`
4. Run the server: `.\\.venv\\Scripts\\python.exe app.py`
5. Open `http://127.0.0.1:3000/` in a browser.

## Upload Guidelines
- Upload only Digilocker-verified marksheets or PDFs with selectable text.
- Avoid scanned photos or images; OCR is best-effort and may fail or be rejected.
- Allowed file types: `pdf`, `png`, `jpg`, `jpeg` (images are discouraged for reliability).
- Max file size: 10MB (`middleware/security.py:12`); oversized files are rejected with `413` (`app.py:77`).
- Do not upload password-protected or corrupted PDFs.
- If the document shows selectable text in a PDF viewer, prefer `method=text` for highest accuracy.
- If you must use an image, ensure good lighting, straight alignment, readable text, and at least `300 DPI`.

## Configuration
Environment variables loaded from the process and optionally `.env.local` in the repo root (`app.py`).

- `SECRET_KEY`: Flask session secret (default dev-only value).
- `GOOGLE_CLIENT_ID`: OAuth Client ID to enable Google Sign-In. If unset, the app attempts to read `client_secret_*.json` from known locations.
- `FLASK_DEBUG`: Set to `true` to enable debug mode.
- `DATABASE_URL`: SQLAlchemy connection string. Defaults to `sqlite:///eligify.db`.
- `TESSERACT_CMD`: Path to `tesseract.exe` if not at the default.
- `POPPLER_PATH`: Path to Poppler `bin` directory for `pdf2image`.

## OCR Setup (Windows)
- Install Tesseract OCR: https://github.com/UB-Mannheim/tesseract/wiki
  - Default Windows path: `C:\\Program Files\\Tesseract-OCR\\tesseract.exe`
- Install Poppler for Windows: https://github.com/oschwartz10612/poppler-windows/releases/
  - Add `bin` to `PATH` or set `POPPLER_PATH` to the Poppler `bin` directory.

Example PowerShell (current session):
```
$env:TESSERACT_CMD = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
$env:POPPLER_PATH = 'C:\\Tools\\poppler-24.08.0\\Library\\bin'
```

## API Endpoints
Base URL: `http://127.0.0.1:3000/`

- `GET /api/exams` — List all exams.
- `POST /api/candidate-profile` — Save candidate profile. Auth required.
- `POST /api/parse-pdf?method=auto|text|ocr&dpi=300` — Parse a PDF. Auth required.
- `POST /api/parse-marksheet?method=auto|text|ocr&dpi=300` — Parse marksheet PDF or image. Auth required.
- `POST /api/verify-academic?stage=10|12|UG&entered=NN.NN` — Verify extracted marks against entered values. Auth required.

Auth routes:
- `GET /login` — Google Sign-In page.
- `POST /auth/google` — Callback for Google Sign-In.
- `POST /logout` — Log out.

## Frontend
- Main template: `templates/index.html`
- JS modules: `static/js`
  - `views` for UI
  - `models` and `services` for client logic

## Security
- Response security headers (`middleware/security.py:16`).
- Strict file validation: type, size, filename (`middleware/security.py:99`).
- Input sanitization to prevent XSS (`middleware/security.py:38`).
- Simple in-memory rate limiting (`middleware/security.py:172`).

## Eligibility Logic
- Server-side exam data is provided by `services/exam_repository.py` and `models/exam.py`.
- Client-side eligibility checks complement server logic in `templates/index.html` and `static/js`.
- Saved results and snapshots use SQLAlchemy models (`models/db_models.py`).

## Troubleshooting
- Missing OCR prerequisites:
  - If `parse-pdf` returns messages like "OCR prerequisites missing" or "Could not rasterize", install and configure Tesseract and Poppler (`lib/pdf_parser.py:106`, `lib/pdf_parser.py:32`).
- Google Sign-In issues:
  - Ensure `GOOGLE_CLIENT_ID` is set or a valid `client_secret_*.json` exists where the app can find it (`app.py:39`, `controllers/web_controller.py:15`, `controllers/auth_controller.py:12`).
- Database:
  - Default SQLite file `eligify.db` is created automatically (`services/db.py:10`). To use Postgres, set `DATABASE_URL` and install `psycopg2-binary`.
- File rejections:
  - Check allowed types and size limits (`middleware/security.py:11`, `middleware/security.py:121`).

## Use Cases
- Students check eligibility for entrance exams and estimate qualification likelihood.
- Users verify that entered percentages or CGPA match official marksheet values via document parsing (`controllers/api_controller.py:178`).

## Project Structure
```
controllers/           # Flask blueprints: web, api, auth
middleware/            # Security headers, validation, rate limiting
models/                # Dataclasses and SQLAlchemy models
services/              # DB init, exam repository, business logic
lib/                   # PDF/marksheet parsing utilities
static/                # Frontend assets (css/js)
templates/             # HTML templates
app.py                 # Flask app entrypoint
requirements.txt       # Python dependencies
```

## Development Tips
- For OCR endpoints, ensure Tesseract and Poppler are installed; otherwise responses may indicate missing prerequisites.
- The default DB is SQLite; to use Postgres, set `DATABASE_URL` and ensure `psycopg2-binary` is installed.
- Google Sign-In is optional; API endpoints requiring auth return `401` if unauthenticated.

## License
Proprietary. All rights reserved. Contact the maintainers for licensing inquiries.
