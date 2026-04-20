import os
from flask import Flask, current_app 
from flask_login import LoginManager 

from config import Config
from .database import db
from .models import User
from .api.views import views
from .api.auth import auth
from .api.list import list
from .api.requests import req_blueprint
from .celery_app import make_celery


DB_NAME = "database.db"
celery = None

def create_app(config_class=Config):
    global celery

    app = Flask(
        __name__,
        template_folder=get_template_dir(),
        static_folder=get_static_dir(),
    )

    app.config.from_object(config_class)

    ensure_directories(app)
    db.init_app(app)
    register_blueprints(app)
    configure_login_manager(app)
    create_database(app)
    celery = make_celery(app)

    return app


def get_static_dir():
    backend_dir = os.path.abspath(os.path.dirname(__file__))
    project_root = os.path.abspath(os.path.join(backend_dir, os.pardir))
    return os.path.join(project_root, "static")



def get_template_dir():
    backend_dir = os.path.abspath(os.path.dirname(__file__))
    project_root = os.path.abspath(os.path.join(backend_dir, os.pardir))
    return os.path.join(project_root, "templates")

def ensure_directories(app):
    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

def register_blueprints(app):
    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")
    app.register_blueprint(list, url_prefix="/")
    app.register_blueprint(req_blueprint, url_prefix="/request")

def configure_login_manager(app):
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

def create_database(app):
    db_path = os.path.join(app.instance_path, DB_NAME)

    if not os.path.exists(db_path):
        try:
            with app.app_context():
                db.create_all()
            app.logger.info("Created database")
        except Exception as exc:
            app.logger.error(f"Failed to create database: {exc}")
    else:
        app.logger.info("Database already exists")
