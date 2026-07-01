from webapp import db
from datetime import datetime

MILESTONES = [
  { "minutes": 25,   "label": "Prisoner",      "prize_eligible": "false", "icon": "⛓️" },
  { "minutes": 60,   "label": "Swabbie",       "prize_eligible": "false", "icon": "☠️" },
  { "minutes": 180,  "label": "Cook",          "prize_eligible": "false", "icon": "👨‍🍳" },
  { "minutes": 300,  "label": "Bosun",         "prize_eligible": "false", "icon": "⚓" },
  { "minutes": 600,  "label": "First Mate",    "prize_eligible": "true",  "icon": "🏴‍☠️" },
  { "minutes": 1500, "label": "Quatermaster",  "prize_eligible": "true",  "icon": "🧭" },
  { "minutes": 3000, "label": "Captain",       "prize_eligible": "true",  "icon": "🦜" },
]

class StudySession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # In Phase 3 this will link to a User; for now we use a cookie-based session_id
    session_key = db.Column(db.String(64), nullable=False, index=True)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    ended_at = db.Column(db.DateTime, nullable=True)
    duration_seconds = db.Column(db.Integer, nullable=True)  # filled on end
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) 

    def to_dict(self):
        return {
            "id": self.id,
            "started_at": self.started_at.isoformat(),
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "duration_seconds": self.duration_seconds,
        }


class EarnedBadge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_key = db.Column(db.String(64), nullable=False, index=True)
    milestone_minutes = db.Column(db.Integer, nullable=False)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)
    prize_claimed = db.Column(db.Boolean, default=False)
    shipping_info = db.Column(db.Text, nullable=True)  # JSON in Phase 3+

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    sessions = db.relationship('StudySession', backref='user', lazy=True)
    badges = db.relationship('EarnedBadge', backref='user', lazy=True)