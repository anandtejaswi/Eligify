"""Main Flask application with MVC architecture and security features."""
from flask import Flask
from controllers.api_controller import api_bp
from controllers.web_controller import web_bp
from middleware.security import setup_security_headers
import os

# Initialize Flask app
app = Flask(__name__, template_folder='templates', static_folder='static')

# Security Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max file size
app.config['WTF_CSRF_ENABLED'] = True  # Enable CSRF protection (if using Flask-WTF forms)

# Register blueprints
app.register_blueprint(web_bp)
app.register_blueprint(api_bp)

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
    # In production, use a proper WSGI server like Gunicorn
    # and set debug=False
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=3000, debug=debug_mode)
