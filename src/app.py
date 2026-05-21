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

# ─── Auth Routes ─────────────────────────────────────────────────────────────

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password']
        role = request.form.get('role', 'student')

        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'error')
            return render_template('register.html')
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return render_template('register.html')
        if len(password) < 8:
            flash('Password must be at least 8 characters.', 'error')
            return render_template('register.html')

        totp_secret = pyotp.random_base32()
        user = User(username=username, email=email,
                    password_hash=generate_password_hash(password),
                    role=role, totp_secret=totp_secret)
        db.session.add(user)
        db.session.commit()

        totp = pyotp.TOTP(totp_secret)
        uri = totp.provisioning_uri(name=email, issuer_name="CyberAware")
        qr = qrcode.make(uri)
        buf = io.BytesIO()
        qr.save(buf, format='PNG')
        qr_b64 = base64.b64encode(buf.getvalue()).decode()

        flash('Account created! Scan the QR code with your authenticator app.', 'success')
        return render_template('setup_2fa.html', qr_b64=qr_b64, secret=totp_secret, username=username)

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if not user or not check_password_hash(user.password_hash, password):
            flash('Invalid username or password.', 'error')
            return render_template('login.html')

        session['pre_2fa_user_id'] = user.id
        return redirect(url_for('verify_2fa'))

    return render_template('login.html')

@app.route('/verify-2fa', methods=['GET', 'POST'])
def verify_2fa():
    user_id = session.get('pre_2fa_user_id')
    if not user_id:
        return redirect(url_for('login'))

    user = User.query.get(user_id)
    if request.method == 'POST':
        token = request.form['token'].strip()
        totp = pyotp.TOTP(user.totp_secret)
        if totp.verify(token):
            session.pop('pre_2fa_user_id', None)
            login_user(user)
            log = AuditLog(user_id=user.id, action='LOGIN', details='Successful 2FA login',
                           ip_address=request.remote_addr)
            db.session.add(log)
            db.session.commit()
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid 2FA code. Try again.', 'error')

    return render_template('verify_2fa.html', username=user.username)

@app.route('/logout')
@login_required
def logout():
    log_action('LOGOUT')
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))

# ─── Dashboard ────────────────────────────────────────────────────────────────

@app.route('/dashboard')
@login_required
def dashboard():
    # Teachers get a simplified dashboard (no personal progress)
    if current_user.role == 'teacher':
        total_challenges = Challenge.query.count()
        categories = db.session.query(Challenge.category).distinct().all()
        categories = [c[0] for c in categories]
        cat_stats = {}
        for cat in categories:
            cat_stats[cat] = {'total': Challenge.query.filter_by(category=cat).count(), 'done': 0}
        return render_template('dashboard.html', completed=0, total=total_challenges,
                               score=0, badges=[], cat_stats=cat_stats, is_teacher=True)

    progress = UserProgress.query.filter_by(user_id=current_user.id).all()
    completed = [p for p in progress if p.completed]
    total_challenges = Challenge.query.count()
    score = sum(p.score for p in completed)
    badges = Badge.query.filter_by(user_id=current_user.id).all()
    categories = db.session.query(Challenge.category).distinct().all()
    categories = [c[0] for c in categories]

    cat_stats = {}
    for cat in categories:
        cat_challenges = Challenge.query.filter_by(category=cat).all()
        cat_ids = [c.id for c in cat_challenges]
        cat_done = UserProgress.query.filter(
            UserProgress.user_id == current_user.id,
            UserProgress.challenge_id.in_(cat_ids),
            UserProgress.completed == True
        ).count()
        cat_stats[cat] = {'total': len(cat_ids), 'done': cat_done}

    return render_template('dashboard.html', completed=len(completed),
                           total=total_challenges, score=score,
                           badges=badges, cat_stats=cat_stats, is_teacher=False)

# ─── Challenges ───────────────────────────────────────────────────────────────

@app.route('/challenges')
@login_required
def challenges():
    category = request.args.get('category', 'all')
    if category == 'all':
        chals = Challenge.query.all()
    else:
        chals = Challenge.query.filter_by(category=category).all()

    progress_map = {}
    if current_user.role != 'teacher':
        for p in UserProgress.query.filter_by(user_id=current_user.id).all():
            progress_map[p.challenge_id] = p

    categories = db.session.query(Challenge.category).distinct().all()
    categories = ['all'] + [c[0] for c in categories]

    return render_template('challenges.html', challenges=chals,
                           progress_map=progress_map, categories=categories,
                           current_cat=category, is_teacher=(current_user.role == 'teacher'))

@app.route('/challenge/<int:cid>', methods=['GET', 'POST'])
@login_required
def challenge(cid):
    # Teachers can only view, not attempt
    if current_user.role == 'teacher':
        chal = Challenge.query.get_or_404(cid)
        return render_template('challenge.html', challenge=chal, progress=None,
                               options=json.loads(chal.options), is_teacher=True)

    chal = Challenge.query.get_or_404(cid)
    progress = UserProgress.query.filter_by(user_id=current_user.id, challenge_id=cid).first()

    if request.method == 'POST':
        answer = request.form.get('answer', '').strip()
        options = json.loads(chal.options)
        correct = options[chal.correct_index]
        is_correct = (answer == correct)

        if not progress:
            progress = UserProgress(user_id=current_user.id, challenge_id=cid,
                                    attempts=1, completed=is_correct,
                                    score=chal.points if is_correct else 0)
            db.session.add(progress)
        else:
            progress.attempts += 1
            if not progress.completed and is_correct:
                progress.completed = True
                progress.score = max(chal.points - (progress.attempts - 1) * 5, 10)

        db.session.commit()
        check_and_award_badges()
        log_action('CHALLENGE_ATTEMPT', f'Challenge {cid}, correct={is_correct}')

        return jsonify({
            'correct': is_correct,
            'explanation': chal.explanation,
            'score': progress.score,
            'completed': progress.completed
        })

    return render_template('challenge.html', challenge=chal, progress=progress,
                           options=json.loads(chal.options), is_teacher=False)

def check_and_award_badges():
    uid = current_user.id
    completed_count = UserProgress.query.filter_by(user_id=uid, completed=True).count()
    existing = [b.name for b in Badge.query.filter_by(user_id=uid).all()]

    awards = [
        (1,  'First Step',    '🎯', 'Completed your first challenge'),
        (5,  'Getting Started','🔥', 'Completed 5 challenges'),
        (10, 'Cyber Learner', '🛡️', 'Completed 10 challenges'),
        (15, 'Security Pro',  '⭐', 'Completed all 15 challenges'),
    ]
    for threshold, name, icon, desc in awards:
        if completed_count >= threshold and name not in existing:
            badge = Badge(user_id=uid, name=name, icon=icon, description=desc)
            db.session.add(badge)
    db.session.commit()

# ─── Admin / Teacher Routes ───────────────────────────────────────────────────

@app.route('/admin')
@login_required
def admin():
    if current_user.role != 'teacher':
        flash('Access denied.', 'error')
        return redirect(url_for('dashboard'))

    users = User.query.all()
    user_stats = []
    for u in users:
        completed = UserProgress.query.filter_by(user_id=u.id, completed=True).count()
        score = db.session.query(db.func.sum(UserProgress.score)).filter_by(user_id=u.id).scalar() or 0
        user_stats.append({'user': u, 'completed': completed, 'score': score})

    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(50).all()
    all_challenges = Challenge.query.order_by(Challenge.category).all()
    return render_template('admin.html', user_stats=user_stats, logs=logs,
                           all_challenges=all_challenges)

@app.route('/admin/challenge/new', methods=['GET', 'POST'])
@login_required
def create_challenge():
    if current_user.role != 'teacher':
        flash('Access denied.', 'error')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        title      = request.form['title'].strip()
        category   = request.form['category'].strip()
        description= request.form['description'].strip()
        difficulty = request.form['difficulty']
        points     = int(request.form.get('points', 20))
        opt0 = request.form['opt0'].strip()
        opt1 = request.form['opt1'].strip()
        opt2 = request.form['opt2'].strip()
        opt3 = request.form['opt3'].strip()
        correct_index = int(request.form['correct_index'])
        explanation = request.form['explanation'].strip()

        if not all([title, category, description, opt0, opt1, opt2, opt3, explanation]):
            flash('All fields are required.', 'error')
            return render_template('create_challenge.html')

        ch = Challenge(
            title=title, category=category, description=description,
            options=json.dumps([opt0, opt1, opt2, opt3]),
            correct_index=correct_index, explanation=explanation,
            points=points, difficulty=difficulty
        )
        db.session.add(ch)
        db.session.commit()
        log_action('CREATE_CHALLENGE', f'Created challenge: {title}')
        flash(f'Challenge "{title}" created successfully!', 'success')
        return redirect(url_for('admin'))

    return render_template('create_challenge.html')

@app.route('/admin/challenge/delete/<int:cid>', methods=['POST'])
@login_required
def delete_challenge(cid):
    if current_user.role != 'teacher':
        flash('Access denied.', 'error')
        return redirect(url_for('dashboard'))

    ch = Challenge.query.get_or_404(cid)
    # Remove related progress records first
    UserProgress.query.filter_by(challenge_id=cid).delete()
    db.session.delete(ch)
    db.session.commit()
    log_action('DELETE_CHALLENGE', f'Deleted challenge id={cid}')
    flash('Challenge deleted.', 'success')
    return redirect(url_for('admin'))

# ─── Leaderboard ─────────────────────────────────────────────────────────────

@app.route('/leaderboard')
@login_required
def leaderboard():
    results = db.session.query(
        User.username, db.func.sum(UserProgress.score).label('total_score'),
        db.func.count(UserProgress.id).label('completed')
    ).join(UserProgress, User.id == UserProgress.user_id)\
     .filter(UserProgress.completed == True)\
     .group_by(User.id)\
     .order_by(db.desc('total_score')).all()

    return render_template('leaderboard.html', results=results)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        from seed import seed_challenges
        seed_challenges()
    app.run(debug=True)
