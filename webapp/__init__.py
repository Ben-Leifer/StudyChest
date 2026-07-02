from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy import inspect, text

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='../static')
    app.config['SECRET_KEY'] = 'dev-secret-change-in-production'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///StudyChest.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    from webapp.routes import main
    app.register_blueprint(main)

    login_manager.init_app(app)
    login_manager.login_view = 'main.login_session'

    from webapp.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    with app.app_context():
        db.create_all()
        _ensure_dev_schema()

    return app


def _ensure_dev_schema():
    inspector = inspect(db.engine)

    if 'study_session' in inspector.get_table_names():
        columns = {column['name'] for column in inspector.get_columns('study_session')}
        if 'user_id' not in columns:
            db.session.execute(text('ALTER TABLE study_session ADD COLUMN user_id INTEGER'))

    if 'earned_badge' in inspector.get_table_names():
        columns = {column['name'] for column in inspector.get_columns('earned_badge')}
        if 'user_id' not in columns:
            db.session.execute(text('ALTER TABLE earned_badge ADD COLUMN user_id INTEGER'))

    db.session.commit()
