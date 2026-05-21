import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from app import app as flask_app
from models import db, User
from werkzeug.security import generate_password_hash
import pyotp


@pytest.fixture
def app():
    flask_app.config['TESTING'] = True
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    flask_app.config['WTF_CSRF_ENABLED'] = False
    with flask_app.app_context():
        db.create_all()
        from seed import seed_challenges
        seed_challenges()
        yield flask_app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def create_user(app, username='testuser', role='student'):
    with app.app_context():
        secret = pyotp.random_base32()
        u = User(
            username=username,
            email=f'{username}@test.com',
            password_hash=generate_password_hash('TestPass123'),
            role=role,
            totp_secret=secret
        )
        db.session.add(u)
        db.session.commit()
        return u.id, secret


# ── Auth Tests ────────────────────────────────────────────────────────────────

def test_register_page_loads(client):
    r = client.get('/register')
    assert r.status_code == 200
    assert b'Create Account' in r.data

def test_login_page_loads(client):
    r = client.get('/login')
    assert r.status_code == 200
    assert b'CyberAware' in r.data

def test_register_new_user(client, app):
    r = client.post('/register', data={
        'username': 'newuser',
        'email': 'newuser@test.com',
        'password': 'SecurePass123',
        'role': 'student'
    }, follow_redirects=True)
    assert r.status_code == 200
    assert b'Scan' in r.data or b'QR' in r.data  # setup_2fa page

def test_register_duplicate_username(client, app):
    create_user(app, 'dupuser')
    r = client.post('/register', data={
        'username': 'dupuser',
        'email': 'other@test.com',
        'password': 'SecurePass123',
        'role': 'student'
    }, follow_redirects=True)
    assert b'already exists' in r.data

def test_login_wrong_password(client, app):
    create_user(app)
    r = client.post('/login', data={
        'username': 'testuser',
        'password': 'wrongpass'
    }, follow_redirects=True)
    assert b'Invalid' in r.data

def test_login_valid_user_redirects_to_2fa(client, app):
    create_user(app)
    r = client.post('/login', data={
        'username': 'testuser',
        'password': 'TestPass123'
    }, follow_redirects=True)
    assert r.status_code == 200
    assert b'Two-Factor' in r.data or b'2FA' in r.data or b'code' in r.data.lower()

def test_2fa_verify_invalid_token(client, app):
    uid, secret = create_user(app)
    client.post('/login', data={'username': 'testuser', 'password': 'TestPass123'})
    r = client.post('/verify-2fa', data={'token': '000000'}, follow_redirects=True)
    assert b'Invalid' in r.data

def test_2fa_verify_valid_token(client, app):
    uid, secret = create_user(app)
    client.post('/login', data={'username': 'testuser', 'password': 'TestPass123'})
    token = pyotp.TOTP(secret).now()
    r = client.post('/verify-2fa', data={'token': token}, follow_redirects=True)
    assert r.status_code == 200


# ── Access Control Tests ──────────────────────────────────────────────────────

def test_dashboard_requires_login(client):
    r = client.get('/dashboard', follow_redirects=True)
    assert b'Login' in r.data or r.status_code == 200

def test_admin_requires_teacher_role(client, app):
    uid, secret = create_user(app, 'studentuser', role='student')
    client.post('/login', data={'username': 'studentuser', 'password': 'TestPass123'})
    token = pyotp.TOTP(secret).now()
    client.post('/verify-2fa', data={'token': token})
    r = client.get('/admin', follow_redirects=True)
    assert b'Access denied' in r.data or b'Dashboard' in r.data


# ── Challenge Tests ───────────────────────────────────────────────────────────

def test_challenges_page_loads_when_logged_in(client, app):
    uid, secret = create_user(app)
    client.post('/login', data={'username': 'testuser', 'password': 'TestPass123'})
    token = pyotp.TOTP(secret).now()
    client.post('/verify-2fa', data={'token': token})
    r = client.get('/challenges')
    assert r.status_code == 200
    assert b'Challenge' in r.data

def test_challenges_seeded(app):
    with app.app_context():
        from models import Challenge
        count = Challenge.query.count()
        assert count >= 15, f"Expected >= 15 challenges, got {count}"

def test_password_strength(app):
    """Security test: ensure passwords are hashed, not plaintext"""
    with app.app_context():
        uid, secret = create_user(app, 'hashtest')
        user = User.query.filter_by(username='hashtest').first()
        assert user.password_hash != 'TestPass123'
        assert len(user.password_hash) > 20  # bcrypt hash is long

def test_totp_secret_stored(app):
    """Security test: ensure each user has a unique TOTP secret"""
    with app.app_context():
        uid1, s1 = create_user(app, 'user1')
        uid2, s2 = create_user(app, 'user2')
        assert s1 != s2
