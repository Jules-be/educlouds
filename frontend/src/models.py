from . import db
from flask_login import UserMixin 
from sqlalchemy.sql import func 

class Lender(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_id'), nullable = False)
    compensation_details = db.Column(db.String(255))

class Borrower(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    project_details = db.Column(db.String(255))
    

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    userType = db.Column(db.Enum('lender', 'borrower'))
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
