"""Security middleware and utilities."""
from functools import wraps
from flask import request, jsonify, g
import os
import re
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge


# File upload security settings
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_FILENAME_LENGTH = 255


def setup_security_headers(response):
    """Add security headers to response."""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://accounts.google.com; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data: https://lh3.googleusercontent.com; "
        "connect-src 'self' https://accounts.google.com https://oauth2.googleapis.com; "
        "frame-src https://accounts.google.com;"
    )
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


def sanitize_input(text: str, max_length: int = 1000) -> str:
    """
    Sanitize user input to prevent XSS attacks.
    
    Args:
        text: Input string to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized string
    """
    if not isinstance(text, str):
        return ""
    
    # Truncate to max length
    text = text[:max_length]
    
    # Remove null bytes
    text = text.replace('\x00', '')
    
    # Remove control characters except newlines and tabs
    text = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', '', text)
    
    return text.strip()


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe storage.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    if not filename:
        return "unnamed.pdf"
    
    # Use werkzeug's secure_filename
    safe_name = secure_filename(filename)
    
    # Ensure it has .pdf extension
    if not safe_name.lower().endswith('.pdf'):
        safe_name = safe_name + '.pdf'
    
    # Limit length
    if len(safe_name) > MAX_FILENAME_LENGTH:
        name, ext = os.path.splitext(safe_name)
        safe_name = name[:MAX_FILENAME_LENGTH - len(ext)] + ext
    
    return safe_name


def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed."""
    if not filename:
        return False
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def validate_file_upload(file):
    """
    Validate uploaded file.
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not file:
        return False, "No file provided"
    
    if not file.filename:
        return False, "No filename provided"
    
    # Check file extension
    if not allowed_file(file.filename):
        return False, f"File type not allowed. Only {', '.join(ALLOWED_EXTENSIONS)} files are permitted."
    
    # Check file size
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)  # Reset file pointer
    
    if file_size > MAX_FILE_SIZE:
        return False, f"File size exceeds maximum allowed size of {MAX_FILE_SIZE / (1024*1024):.1f}MB"
    
    if file_size == 0:
        return False, "File is empty"
    
    # Check filename
    if len(file.filename) > MAX_FILENAME_LENGTH:
        return False, f"Filename too long. Maximum length is {MAX_FILENAME_LENGTH} characters"
    
    return True, ""


def validate_dpi(dpi_param: str):
    """
    Validate DPI parameter.
    
    Returns:
        Tuple of (is_valid, dpi_value, error_message)
    """
    if not dpi_param:
        return True, 300, ""  # Default DPI
    
    try:
        dpi = int(dpi_param)
        if dpi < 100 or dpi > 600:
            return False, 300, "DPI must be between 100 and 600"
        return True, dpi, ""
    except ValueError:
        return False, 300, "Invalid DPI value. Must be an integer"


def validate_method(method_param: str):
    """
    Validate parsing method parameter.
    
    Returns:
        Tuple of (is_valid, method_value, error_message)
    """
    if not method_param:
        return True, "auto", ""  # Default method
    
    method = method_param.lower().strip()
    valid_methods = ['auto', 'text', 'ocr']
    
    if method not in valid_methods:
        return False, "auto", f"Invalid method. Must be one of: {', '.join(valid_methods)}"
    
    return True, method, ""


def rate_limit(max_requests: int = 100, window: int = 60):
    """
    Simple rate limiting decorator (in-memory).
    In production, use Redis or similar for distributed rate limiting.
    """
    from collections import defaultdict
    from time import time
    
    request_counts = defaultdict(list)
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_ip = request.remote_addr
            current_time = time()
            
            # Clean old entries
            request_counts[client_ip] = [
                req_time for req_time in request_counts[client_ip]
                if current_time - req_time < window
            ]
            
            # Check rate limit
            if len(request_counts[client_ip]) >= max_requests:
                return jsonify({
                    'error': 'Rate limit exceeded. Please try again later.'
                }), 429
            
            # Add current request
            request_counts[client_ip].append(current_time)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

