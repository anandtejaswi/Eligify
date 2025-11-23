from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, current_app
from services.db import SessionLocal
from models.db_models import User
from google.oauth2 import id_token
from google.auth.transport import requests as grequests

auth_bp = Blueprint('auth', __name__)

@auth_bp.get('/login')
def login():
    client_id = current_app.config.get('GOOGLE_CLIENT_ID')
    return render_template('login.html', google_client_id=client_id)

@auth_bp.post('/auth/google')
def auth_google():
    token = request.json.get('credential')
    client_id = current_app.config.get('GOOGLE_CLIENT_ID')
    if not token or not client_id:
        return jsonify({'error': 'Missing credential or client id'}), 400
    try:
        idinfo = id_token.verify_oauth2_token(token, grequests.Request(), client_id)
        user = {
            'sub': idinfo.get('sub'),
            'email': idinfo.get('email'),
            'name': idinfo.get('name'),
            'picture': idinfo.get('picture'),
        }
        session['user'] = user
        db = SessionLocal()
        existing = db.get(User, user['sub'])
        if existing:
            existing.email = user['email']
            existing.name = user['name']
            existing.picture = user['picture']
        else:
            db.add(User(sub=user['sub'], email=user['email'], name=user['name'], picture=user['picture']))
        db.commit()
        db.close()
        return jsonify({'ok': True})
    except Exception:
        return jsonify({'error': 'Invalid Google token'}), 401

@auth_bp.post('/logout')
def logout():
    session.clear()
    resp = redirect(url_for('web.index'))
    resp.headers['Clear-Site-Data'] = '"cookies", "storage"'
    return resp

@auth_bp.get('/logout')
def logout_get():
    session.clear()
    resp = redirect(url_for('web.index'))
    resp.headers['Clear-Site-Data'] = '"cookies", "storage"'
    return resp