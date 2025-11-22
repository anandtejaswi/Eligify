"""API controller for handling API endpoints."""
from flask import Blueprint, request, jsonify
from lib.pdf_parser import extract_text_from_pdf, extract_marksheet_fields
from middleware.security import (
    validate_file_upload, validate_dpi, validate_method,
    sanitize_input, rate_limit
)

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.post('/parse-pdf')
@rate_limit(max_requests=50, window=60)  # 50 requests per minute
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
        text = sanitize_input(text, max_length=100000)  # Allow longer text for PDF content
        
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
@rate_limit(max_requests=50, window=60)  # 50 requests per minute
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
        # Extract fields from marksheet
        fields = extract_marksheet_fields(f, method=method, dpi=dpi)
        
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
        
        return jsonify({
            'fields': fields,
            'method': method,
            'dpi': dpi
        })
    except Exception as e:
        # Don't expose internal error details
        return jsonify({'error': 'An unexpected error occurred while processing the marksheet.'}), 500
