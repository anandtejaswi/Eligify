from flask import Blueprint, request, jsonify
from lib.pdf_parser import extract_text_from_pdf, extract_marksheet_fields

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.post('/parse-pdf')
def parse_pdf_ep():
    f = request.files.get('file')
    if not f:
        return jsonify({'error': 'No file uploaded.'}), 400
    method = (request.args.get('method') or 'auto').lower()
    dpi_param = request.args.get('dpi')
    try:
        dpi = int(dpi_param) if dpi_param else 300
    except ValueError:
        return jsonify({'error': 'Invalid dpi value.'}), 400

    try:
        text = extract_text_from_pdf(f, method=method, dpi=dpi)
        return jsonify({'text': text, 'method': method})
    except RuntimeError as e:
        return jsonify({'error': str(e)}), 500


@api_bp.post('/parse-marksheet')
def parse_marksheet_ep():
    f = request.files.get('file')
    if not f:
        return jsonify({'error': 'No file uploaded.'}), 400
    method = (request.args.get('method') or 'auto').lower()
    dpi_param = request.args.get('dpi')
    try:
        dpi = int(dpi_param) if dpi_param else 300
    except ValueError:
        return jsonify({'error': 'Invalid dpi value.'}), 400

    fields = extract_marksheet_fields(f, method=method, dpi=dpi)
    return jsonify({'fields': fields, 'method': method, 'dpi': dpi})