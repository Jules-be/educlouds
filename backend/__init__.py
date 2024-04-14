from flask import Flask
from config import Config, DevelopmentConfig, ProductionConfig
from flask_sqlalchemy import SQLAlchemy
from .api.views import views
from .api.auth import auth
from .models import Borrower, Lender, User
from os import path

# Define the DB
db = SQLAlchemy()
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

# Script that checks db 
def create_database(app):
    if not path.exists('src/' + DB_NAME):
        with app.app_context():
            db.create_all()
        print('Created Database!')
    else:
        print('Database already exists!')