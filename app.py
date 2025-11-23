"""Main Flask application with MVC architecture and security features."""
from flask import Flask, request, session, redirect, url_for
from controllers.api_controller import api_bp
from controllers.web_controller import web_bp
from controllers.auth_controller import auth_bp
from middleware.security import setup_security_headers
from services.db import init_db
import os
import glob
import json
from typing import Dict

# Initialize Flask app
app = Flask(__name__, template_folder='templates', static_folder='static')

# Security Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['TEMPLATES_AUTO_RELOAD'] = True
def _load_env_local(path: str) -> Dict[str,str]:
    env = {}
    try:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    s = line.strip()
                    if not s or s.startswith('#'):
                        continue
                    if '=' in s:
                        k, v = s.split('=', 1)
                        env[k.strip()] = v.strip()
    except Exception:
        pass
    return env

# Load local environment overrides for secrets
_env_local = _load_env_local(os.path.join(os.path.dirname(__file__), '.env.local'))
for k, v in _env_local.items():
    os.environ.setdefault(k, v)
_cid = os.environ.get('GOOGLE_CLIENT_ID')
if not _cid:
    try:
        _files = []
        _files.extend(glob.glob(os.path.join(os.path.dirname(__file__), 'client_secret_*.json')))
        _files.extend(glob.glob(os.path.join(os.getcwd(), 'client_secret_*.json')))
        for _p in _files:
            with open(_p, 'r', encoding='utf-8') as _f:
                _data = json.load(_f)
                _cid = (_data.get('web') or {}).get('client_id')
                if _cid:
                    break
    except Exception:
        _cid = None
app.config['GOOGLE_CLIENT_ID'] = _cid
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max file size
app.config['WTF_CSRF_ENABLED'] = True  # Enable CSRF protection (if using Flask-WTF forms)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(web_bp)
app.register_blueprint(api_bp)

init_db(app)


# No global redirect; gating is handled at action time on the UI and per-API

# Add security headers to all responses
@app.after_request
def after_request(response):
    """Add security headers to all responses."""
    return setup_security_headers(response)


# Error handlers
@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large errors."""
    return {'error': 'File size exceeds maximum allowed size of 10MB'}, 413


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return {'error': 'Resource not found'}, 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return {'error': 'An internal server error occurred'}, 500


if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='127.0.0.1', port=3000, debug=debug_mode)
