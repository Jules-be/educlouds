from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path 
from flask_login import LoginManager
from datetime import timedelta

# Define the DB
db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')
    db.init_app(app)
    
    
    from .views import views
    from .auth import auth
    from .models import User, UserType
    
    # Register blueprints
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    
    create_database(app)
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)
    
    @app.shell_context_processor
    def make_shell_context():
        return {
            'db': db,
            'User': User,
            'UserType': UserType,
        }
    
    return app

# Script that checks db 
def create_database(app):
    if not path.exists('src/' + DB_NAME):
        with app.app_context():
            db.create_all()
            populate_user_type()
        print('Created Database!')
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
    
    db.session.commit()  # Make sure to commit changes only if new data is added
