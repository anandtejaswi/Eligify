"""API controller for handling API endpoints."""
from flask import Blueprint, request, jsonify
from services.exam_repository import ExamRepository
from services.db import SessionLocal
from models.db_models import CandidateProfile, DocumentUpload, ParsedDocument, AcademicVerification
import json
from lib.pdf_parser import extract_text_from_pdf, extract_marksheet_fields, extract_marksheet_fields_from_image
from middleware.security import (
    validate_file_upload, validate_dpi, validate_method,
    sanitize_input, rate_limit
)
from functools import wraps
from flask import session, jsonify
from io import BytesIO

def require_login(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get('user'):
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return wrapper

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.get('/exams')
def get_exams():
    exams = ExamRepository.get_all_exams()
    return jsonify([e.to_dict() for e in exams])
@api_bp.post('/candidate-profile')
@require_login
def save_candidate_profile():
    data = request.json or {}
    try:
        first_name = str(data.get('first_name', '')).strip()
        dob = str(data.get('dob', ''))
        category = str(data.get('category', ''))
        p10 = float(data.get('p10', 0))
        p12 = float(data.get('p12', 0))
        ug_cgpa = float(data.get('ug_cgpa', 0))
    except Exception:
        return jsonify({'error': 'Invalid payload'}), 400
    db = SessionLocal()
    profile = CandidateProfile(user_sub=session['user']['sub'], first_name=first_name, dob=dob, category=category, p10=p10, p12=p12, ug_cgpa=ug_cgpa)
    db.add(profile)
    db.commit()
    pid = profile.id
    db.close()
    return jsonify({'ok': True, 'candidate_profile_id': pid})

@api_bp.post('/parse-pdf')
@require_login
@rate_limit(max_requests=50, window=60)
def parse_pdf_ep():
    """Parse PDF endpoint with security validation."""
    # Validate file upload
    f = request.files.get('file')
    is_valid, error_msg = validate_file_upload(f)
    if not is_valid:
        return jsonify({'error': error_msg}), 400
    
    # Validate method parameter
    method_param = request.args.get('method', 'auto')
    is_valid, method, error_msg = validate_method(method_param)
    if not is_valid:
        return jsonify({'error': error_msg}), 400
    
    # Validate DPI parameter
    dpi_param = request.args.get('dpi')
    is_valid, dpi, error_msg = validate_dpi(dpi_param)
    if not is_valid:
        return jsonify({'error': error_msg}), 400
    
    try:
        # Extract text from PDF
        text = extract_text_from_pdf(f, method=method, dpi=dpi)
        
        # Sanitize output to prevent XSS
        text = sanitize_input(text, max_length=100000)
        db = SessionLocal()
        doc_type = request.args.get('doc_type', 'unknown')
        upload = DocumentUpload(user_sub=session['user']['sub'], doc_type=doc_type, filename=f.filename, mime=(getattr(f, 'mimetype', None) or 'application/pdf'), stored_path=None)
        db.add(upload)
        db.flush()
        db.add(ParsedDocument(upload_id=upload.id, parsed_json=json.dumps({'text': text, 'method': method, 'dpi': dpi})))
        db.commit()
        db.close()
        return jsonify({
            'text': text,
            'method': method,
            'dpi': dpi
        })
    except RuntimeError as e:
        # Don't expose internal error details
        error_message = str(e)
        # Sanitize error message
        error_message = sanitize_input(error_message, max_length=500)
        return jsonify({'error': 'Failed to parse PDF. Please ensure the file is a valid PDF.'}), 500
    except Exception as e:
        # Log the actual error internally (in production, use proper logging)
        # For now, return generic error
        return jsonify({'error': 'An unexpected error occurred while processing the PDF.'}), 500


@api_bp.post('/parse-marksheet')
@require_login
@rate_limit(max_requests=50, window=60)
def parse_marksheet_ep():
    """Parse marksheet endpoint with security validation."""
    # Validate file upload
    f = request.files.get('file')
    is_valid, error_msg = validate_file_upload(f)
    if not is_valid:
        return jsonify({'error': error_msg}), 400
    
    # Validate method parameter
    method_param = request.args.get('method', 'auto')
    is_valid, method, error_msg = validate_method(method_param)
    if not is_valid:
        return jsonify({'error': error_msg}), 400
    
    # Validate DPI parameter
    dpi_param = request.args.get('dpi')
    is_valid, dpi, error_msg = validate_dpi(dpi_param)
    if not is_valid:
        return jsonify({'error': error_msg}), 400
    
    try:
        mime = getattr(f, 'mimetype', '') or ''
        is_img = str(mime).lower().startswith('image/') or f.filename.lower().endswith(('.png', '.jpg', '.jpeg'))
        fields = extract_marksheet_fields_from_image(f) if is_img else extract_marksheet_fields(f, method=method, dpi=dpi)
        
        # Sanitize all string fields in the response
        if isinstance(fields, dict):
            sanitized_fields = {}
            for key, value in fields.items():
                if isinstance(value, str):
                    sanitized_fields[key] = sanitize_input(value, max_length=500)
                elif isinstance(value, list):
                    # Sanitize list items
                    sanitized_list = []
                    for item in value:
                        if isinstance(item, dict):
                            sanitized_item = {}
                            for k, v in item.items():
                                if isinstance(v, str):
                                    sanitized_item[k] = sanitize_input(v, max_length=200)
                                else:
                                    sanitized_item[k] = v
                            sanitized_list.append(sanitized_item)
                        elif isinstance(item, str):
                            sanitized_list.append(sanitize_input(item, max_length=200))
                        else:
                            sanitized_list.append(item)
                    sanitized_fields[key] = sanitized_list
                else:
                    sanitized_fields[key] = value
            fields = sanitized_fields
        db = SessionLocal()
        doc_type = request.args.get('doc_type', 'marksheet')
        upload = DocumentUpload(user_sub=session['user']['sub'], doc_type=doc_type, filename=f.filename, mime=(getattr(f, 'mimetype', None) or 'application/pdf'), stored_path=None)
        db.add(upload)
        db.flush()
        db.add(ParsedDocument(upload_id=upload.id, parsed_json=json.dumps({'fields': fields, 'method': method, 'dpi': dpi})))
        db.commit()
        db.close()
        return jsonify({
            'fields': fields,
            'method': method,
            'dpi': dpi
        })
    except Exception as e:
        # Don't expose internal error details
        return jsonify({'error': 'An unexpected error occurred while processing the marksheet.'}), 500


@api_bp.post('/verify-academic')
@api_bp.post('/verify-academic/')
@require_login
@rate_limit(max_requests=30, window=60)
def verify_academic():
    stage = (request.args.get('stage') or '').upper().strip()
    if stage not in ('10', '12', 'UG'):
        return jsonify({'error': 'Invalid stage. Use 10, 12, or UG'}), 400
    entered_raw = request.form.get('entered') or request.args.get('entered')
    try:
        entered_val = float(entered_raw)
    except Exception:
        return jsonify({'error': 'Invalid entered value'}), 400
    f = request.files.get('file')
    is_valid, error_msg = validate_file_upload(f)
    if not is_valid:
        return jsonify({'error': error_msg}), 400
    method_param = request.args.get('method', 'auto')
    is_valid, method, error_msg = validate_method(method_param)
    if not is_valid:
        return jsonify({'error': error_msg}), 400
    dpi_param = request.args.get('dpi')
    is_valid, dpi, error_msg = validate_dpi(dpi_param)
    if not is_valid:
        return jsonify({'error': error_msg}), 400
    # Optional tolerance parameter
    tol_param = request.args.get('tolerance') or request.args.get('tol')
    try:
        tolerance = float(tol_param) if tol_param is not None else 0.1
        if tolerance < 0:
            tolerance = 0.1
    except Exception:
        tolerance = 0.1
    # Round the entered value for consistent comparison
    entered_val = round(entered_val, 2)
    try:
        file_bytes = f.read()
        buf = BytesIO(file_bytes)
        mime = getattr(f, 'mimetype', '') or ''
        is_img = str(mime).lower().startswith('image/') or f.filename.lower().endswith(('.png', '.jpg', '.jpeg'))
        fields = (extract_marksheet_fields_from_image(BytesIO(file_bytes)) if is_img else extract_marksheet_fields(buf, method=method, dpi=dpi)) or {}
        # Robust computation from raw fields if percentage missing
        def safe_float(x):
            try:
                return float(x)
            except Exception:
                return None
        total_marks = safe_float(fields.get('total_marks'))
        max_marks = safe_float(fields.get('max_marks'))
        if (total_marks is None or max_marks is None or max_marks <= 0):
            subs = fields.get('subjects') or []
            sm = sum((s.get('marks') or 0) for s in subs if isinstance(s.get('marks'), (int, float)))
            sx = sum((s.get('max') or 0) for s in subs if isinstance(s.get('max'), (int, float)))
            if sm > 0:
                total_marks = sm
            if (sx is None or sx <= 0) and subs:
                sx = 100.0 * len([1 for s in subs if s.get('marks') is not None])
            if sx and sx > 0:
                max_marks = sx
        calc_pct = None
        if total_marks is not None and max_marks is not None and max_marks > 0:
            calc_pct = (total_marks / max_marks) * 100.0
        # Prefer percentage for 10/12, CGPA for UG; fall back to calc_pct
        extracted = None
        source = None
        if stage in ('10', '12'):
            extracted = fields.get('percentage')
            if extracted is None:
                extracted = fields.get('calculated_percentage')
                source = 'calculated_percentage' if extracted is not None else source
            if extracted is None:
                extracted = calc_pct
                source = 'computed_total' if extracted is not None else source
            if extracted is None:
                extracted = fields.get('cgpa')
                source = 'cgpa' if extracted is not None else source
            if source is None and extracted is not None:
                source = 'percentage'
        else:
            extracted = fields.get('cgpa')
            if extracted is None:
                extracted = fields.get('percentage')
                source = 'percentage' if extracted is not None else source
            if extracted is None:
                extracted = fields.get('calculated_percentage')
                source = 'calculated_percentage' if extracted is not None else source
            if extracted is None:
                extracted = calc_pct
                source = 'computed_total' if extracted is not None else source
            if source is None and extracted is not None:
                source = 'cgpa'
        extracted_val = safe_float(extracted)
        if extracted_val is not None:
            extracted_val = round(extracted_val, 2)
        if extracted_val is None or abs(extracted_val - entered_val) > tolerance:
            buf2 = BytesIO(file_bytes)
            fields = (extract_marksheet_fields_from_image(buf2) if is_img else extract_marksheet_fields(buf2, method='ocr', dpi=max(dpi or 300, 300))) or {}
            total_marks = safe_float(fields.get('total_marks'))
            max_marks = safe_float(fields.get('max_marks'))
            calc_pct = None
            if total_marks is not None and max_marks is not None and max_marks > 0:
                calc_pct = (total_marks / max_marks) * 100.0
            # Re-evaluate sources in fallback
            if stage in ('10', '12'):
                extracted = fields.get('percentage')
                source = 'percentage' if extracted is not None else None
                if extracted is None:
                    extracted = fields.get('calculated_percentage')
                    source = 'calculated_percentage' if extracted is not None else source
                if extracted is None:
                    extracted = calc_pct
                    source = 'computed_total' if extracted is not None else source
                if extracted is None:
                    extracted = fields.get('cgpa')
                    source = 'cgpa' if extracted is not None else source
            else:
                extracted = fields.get('cgpa')
                source = 'cgpa' if extracted is not None else None
                if extracted is None:
                    extracted = fields.get('percentage')
                    source = 'percentage' if extracted is not None else source
                if extracted is None:
                    extracted = fields.get('calculated_percentage')
                    source = 'calculated_percentage' if extracted is not None else source
                if extracted is None:
                    extracted = calc_pct
                    source = 'computed_total' if extracted is not None else source
            extracted_val = safe_float(extracted)
            if extracted_val is not None:
                extracted_val = round(extracted_val, 2)
        diff = None
        if extracted_val is not None:
            diff = round(abs(extracted_val - entered_val), 3)
        verified = int(extracted_val is not None and diff is not None and diff <= tolerance)
        db = SessionLocal()
        upload = DocumentUpload(user_sub=session['user']['sub'], doc_type=f"marksheet-{stage}", filename=f.filename, mime=(getattr(f, 'mimetype', None) or 'application/pdf'), stored_path=None)
        db.add(upload)
        db.flush()
        db.add(ParsedDocument(upload_id=upload.id, parsed_json=json.dumps({'fields': fields, 'method': method, 'dpi': dpi})))
        av = AcademicVerification(user_sub=session['user']['sub'], stage=stage, entered_value=entered_val, extracted_value=extracted_val, verified=verified, upload_id=upload.id, filename=f.filename, mime=(getattr(f, 'mimetype', None) or 'application/pdf'))
        db.add(av)
        db.commit()
        db.close()
        return jsonify({
            'stage': stage,
            'entered': entered_val,
            'extracted': extracted_val,
            'difference': diff,
            'tolerance': tolerance,
            'comparison_source': source,
            'total_marks': total_marks,
            'max_marks': max_marks,
            'verified': bool(verified),
            'fields': fields
        })
    except Exception:
        return jsonify({'error': 'Failed to verify academic document'}), 500
