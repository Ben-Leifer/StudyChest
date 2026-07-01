from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='../static')
    app.config['SECRET_KEY'] = 'dev-secret-change-in-production'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///StudyChest.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    from webapp.routes import main
    app.register_blueprint(main)

    with app.app_context():
        db.create_all()

    return app
