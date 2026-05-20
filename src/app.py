from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import pyotp
import qrcode
import io
import base64
from datetime import datetime
from models import db, User, Challenge, UserProgress, Badge, AuditLog
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cybersec-awareness-secret-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cyberaware.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def log_action(action, details=""):
    if current_user.is_authenticated:
        log = AuditLog(user_id=current_user.id, action=action, details=details,
                       ip_address=request.remote_addr)
        db.session.add(log)
        db.session.commit()

# ─── Auth Routes ────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

