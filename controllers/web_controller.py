"""Web controller for handling web page requests."""
from flask import Blueprint, render_template, session, redirect, url_for
import os, glob, json
from services.exam_repository import ExamRepository
from services.eligibility_service import EligibilityService

web_bp = Blueprint('web', __name__)


@web_bp.get('/')
def index():
    exams = ExamRepository.get_all_exams()
    exams_data = [exam.to_dict() for exam in exams]
    from flask import current_app
    client_id = current_app.config.get('GOOGLE_CLIENT_ID')
    if not client_id:
        try:
            files = []
            files.extend(glob.glob(os.path.join(os.path.dirname(current_app.root_path), 'client_secret_*.json')))
            files.extend(glob.glob(os.path.join(current_app.root_path, 'client_secret_*.json')))
            files.extend(glob.glob(os.path.join(os.getcwd(), 'client_secret_*.json')))
            for p in files:
                with open(p, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    client_id = (data.get('web') or {}).get('client_id')
                    if client_id:
                        break
        except Exception:
            client_id = None
    return render_template('index.html', exams=exams_data, user=session.get('user'), google_client_id=client_id)
