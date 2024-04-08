from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path 

# Define the DB
db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'Educloud_Abdoul'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'  # Remove the space
    db.init_app(app)
    
    from .views import views
    from .auth import auth
    #from .models import models 
    # Register blueprints
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    
    #create_database(app)

    return app


# Script that checks db 
'''def create_database(app):
        if not path.exists(DB_NAME):
            db.create_all(app=app)
            print('Created Database!')
        else:
            print('Database already exists.') '''

