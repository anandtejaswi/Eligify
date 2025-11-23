"""Web controller for handling web page requests."""
from flask import Blueprint, render_template, session, redirect, url_for
from services.exam_repository import ExamRepository
from services.eligibility_service import EligibilityService

web_bp = Blueprint('web', __name__)


@web_bp.get('/')
def index():
    exams = ExamRepository.get_all_exams()
    exams_data = [exam.to_dict() for exam in exams]
    from flask import current_app
    client_id = current_app.config.get('GOOGLE_CLIENT_ID')
    return render_template('index.html', exams=exams_data, user=session.get('user'), google_client_id=client_id)
