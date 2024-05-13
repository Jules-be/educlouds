from flask import Flask
from flask_login import LoginManager
from config import Config
from .api.views import views
from .api.auth import auth
from .api.list import list
from .api.requests import req_blueprint
from .database import db
from flask import current_app
from .models import User
import os

DB_NAME = "database.db"

def create_app(config_class=Config):
    name = __name__
    app_dir = os.path.abspath(os.path.dirname(__file__))
    parent_dir = os.path.abspath(os.path.join(app_dir, os.pardir))
    template_dir = os.path.join(parent_dir, 'templates')
    upload_folder = os.getenv('UPLOAD_FOLDER', 'requests')
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    app = Flask(name, template_folder=template_dir)
    app.config['UPLOAD_FOLDER'] = upload_folder
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    app.config.from_object(config_class)
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(list, url_prefix='/')
    app.register_blueprint(req_blueprint, url_prefix='/request')

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    @login_manager.user_loader
    
    def load_user(user_id):
        return User.query.get(user_id)

    return app

def create_database(app):
    # Build the path for the database
    db_path = os.path.join(app.instance_path, DB_NAME)
    
    # Ensure the instance folder exists
    if not os.path.exists(app.instance_path):
        os.makedirs(app.instance_path)
    
    # Check if the database file already exists
    if not os.path.exists(db_path):
        try:
            with app.app_context():
                db.create_all()
                populate_user_type()
            print('Created Database!')
        except Exception as e:
            current_app.logger.error(f'Failed to create database: {e}')
    else:
        print('Database already exists!')

def populate_user_type():
    from .models import UserType
    
    if UserType.query.get(UserType.LENDER) is None:
        lender = UserType(id=UserType.LENDER, name='Lender')
        db.session.add(lender)
    
    if UserType.query.get(UserType.BORROWER) is None:
        borrower = UserType(id=UserType.BORROWER, name='Borrower')
        db.session.add(borrower)
    
    db.session.commit()
