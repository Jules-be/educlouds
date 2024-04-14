from .database import db
from flask_login import UserMixin 
from sqlalchemy.sql import func 

class Lender(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Corrected ForeignKey reference
    compensation_details = db.Column(db.String(255))

class Borrower(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Corrected ForeignKey reference
    project_details = db.Column(db.String(255))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_type = db.Column(db.Enum('lender', 'borrower', name='user_type'))  # Corrected enum definition
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
