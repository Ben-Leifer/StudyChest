from flask import Blueprint, render_template, request, jsonify, session, url_for, redirect, flash
from flask_login import login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from webapp import db
from webapp.models import StudySession, EarnedBadge, MILESTONES, User
from datetime import datetime
import uuid

main = Blueprint('main', __name__)
bcrypt = Bcrypt()

def get_session_key():
    """Return (or create) a persistent anonymous session key stored in the browser session."""
    if 'session_key' not in session:
        session['session_key'] = str(uuid.uuid4())
    return session['session_key']


# ── Pages ──────────────────────────────────────────────────────────────────────

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/register')
def register():
    return render_template('register.html')

@main.route('/login')
def login():
    return render_template('login.html')

@main.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

# ── API ────────────────────────────────────────────────────────────────────────

@main.route('/api/session/start', methods=['POST'])
def start_session():
    key = get_session_key()
    study = StudySession(session_key=key)
    db.session.add(study)
    db.session.commit()
    return jsonify({"session_id": study.id, "started_at": study.started_at.isoformat()})


@main.route('/api/session/end', methods=['POST'])
def end_session():
    key = get_session_key()
    data = request.get_json()
    session_id = data.get('session_id')
    elapsed_seconds = data.get('elapsed_seconds', 0)

    study = StudySession.query.filter_by(id=session_id, session_key=key).first()
    if not study:
        return jsonify({"error": "Session not found"}), 404

    study.ended_at = datetime.utcnow()
    study.duration_seconds = elapsed_seconds
    db.session.commit()

    # Check for new milestone badges
    new_badges = _check_milestones(key, elapsed_seconds)

    return jsonify({
        "session": study.to_dict(),
        "new_badges": new_badges,
    })

@main.route('/api/stats', methods=['GET'])
def stats():
    key = get_session_key()

    sessions = StudySession.query.filter_by(session_key=key).filter(
        StudySession.duration_seconds.isnot(None)
    ).all()

    total_seconds = sum(s.duration_seconds for s in sessions)
    total_minutes = total_seconds // 60

    badges = EarnedBadge.query.filter_by(session_key=key).all()
    earned_milestones = {b.milestone_minutes for b in badges}

    milestone_data = []
    for m in MILESTONES:
        milestone_data.append({
            **m,
            "earned": m["minutes"] <= total_minutes,
        })

    return jsonify({
        "total_seconds": total_seconds,
        "total_minutes": total_minutes,
        "session_count": len(sessions),
        "milestones": milestone_data,
    })

# ── Register ────────────────────────────────────────────────────────────────────

@main.route('/register', methods=["GET", "POST"])
def register_session():
    if request.method == 'GET':
        return render_template('register.html')

    # POST request — process the form
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')

    #check fields are filled
    if not username or not email or not password:
        return render_template('register.html', error="All fields are required.")
    
    #check if email already exists
    existing_user = User.query.filter_by(email=email).first() 
    if existing_user:
        flash('An account with that email already exists')
        return render_template('register.html')
    
    #hash password
    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    #add new user
    new_user = User(username=username, email=email, password_hash=password_hash)
    db.session.add(new_user)
    db.session.commit()

    #redirect to login
    flash('Account created! Please log in.')
    return redirect(url_for('main.login'))


#### TODO : Add login post route and functionality, including password verification and session management.
#### TODO : Add logout route and functionality, including session termination and redirect to home page.
# ── Helpers ────────────────────────────────────────────────────────────────────

def _check_milestones(session_key: str, new_session_seconds: int) -> list:
    """Award any newly crossed milestone badges and return them."""
    sessions = StudySession.query.filter_by(session_key=session_key).filter(
        StudySession.duration_seconds.isnot(None)
    ).all()
    total_minutes = sum(s.duration_seconds for s in sessions) // 60

    already_earned = {
        b.milestone_minutes
        for b in EarnedBadge.query.filter_by(session_key=session_key).all()
    }

    new_badges = []
    for m in MILESTONES:
        if m["minutes"] <= total_minutes and m["minutes"] not in already_earned:
            badge = EarnedBadge(session_key=session_key, milestone_minutes=m["minutes"])
            db.session.add(badge)
            new_badges.append(m)

    db.session.commit()
    return new_badges