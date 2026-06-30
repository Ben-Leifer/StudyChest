from webapp import db
from datetime import datetime

MILESTONES = [
    {"minutes": 25,    "label": "First Focus",    "prize_eligible": False, "icon": "🔥"},
    {"minutes": 60,    "label": "One Hour Hero",  "prize_eligible": False, "icon": "⚡"},
    {"minutes": 180,   "label": "Deep Work",      "prize_eligible": False, "icon": "🧠"},
    {"minutes": 300,   "label": "Iron Mind",      "prize_eligible": False, "icon": "💎"},
    {"minutes": 600,   "label": "Scholar",        "prize_eligible": True,  "icon": "🏆"},  # 10 hrs total - prize eligible
    {"minutes": 1500,  "label": "Grind King",     "prize_eligible": True,  "icon": "👑"},  # 25 hrs total
    {"minutes": 3000,  "label": "Legend",         "prize_eligible": True,  "icon": "🌟"},  # 50 hrs total
]

class StudySession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # In Phase 3 this will link to a User; for now we use a cookie-based session_id
    session_key = db.Column(db.String(64), nullable=False, index=True)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    ended_at = db.Column(db.DateTime, nullable=True)
    duration_seconds = db.Column(db.Integer, nullable=True)  # filled on end

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
