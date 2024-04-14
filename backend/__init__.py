from flask import Flask
from config import Config
from .api.views import views
from .api.auth import auth
from .database import db
from flask import current_app
import os

DB_NAME = "database.db"

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    create_database(app)

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
            print('Created Database!')
        except Exception as e:
            current_app.logger.error(f'Failed to create database: {e}')
    else:
        print('Database already exists!')