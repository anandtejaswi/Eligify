"""Web controller for handling web page requests."""
from flask import Blueprint, render_template
from services.exam_repository import ExamRepository
from services.eligibility_service import EligibilityService

web_bp = Blueprint('web', __name__)


@web_bp.get('/')
def index():
    """Render the main index page."""
    # Get all exams for the frontend (if needed)
    exams = ExamRepository.get_all_exams()
    # Convert to dict for JSON serialization in template
    exams_data = [exam.to_dict() for exam in exams]
    return render_template('index.html', exams=exams_data)
