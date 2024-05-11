from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os 

db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('../config.py')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///src/' + DB_NAME
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        create_database()
    return app

def create_database():
    if not os.path.exists(DB_NAME):
        db.create_all()
        populate_user_type()
        print('Created Database!')
    else:
        print('Database already exists!')

def populate_user_type():
    from .models import UserType
    if UserType.query.get(1) is None:
        lender = UserType(id=1, name='Lender')
        db.session.add(lender)
    if UserType.query.get(2) is None:
        borrower = UserType(id=2, name='Borrower')
        db.session.add(borrower)
    db.session.commit()