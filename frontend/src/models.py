from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_type = db.Column(db.Enum('lender', 'borrower', name='user_type'))
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    lender = db.relationship('Lender', uselist=False, backref='user')
    borrower = db.relationship('Borrower', uselist=False, backref='user')

class Lender(db.Model):
    lender_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    compensation_details = db.Column(db.String(255))
    computational_resources = db.relationship('ComputationalResources', back_populates='lender')

class Borrower(db.Model):
    borrower_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    project_details = db.Column(db.String(255))
    lending_requests = db.relationship('LendingRequests', back_populates='borrower')

class ComputationalResources(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lender_id = db.Column(db.Integer, db.ForeignKey('lender.lender_id'))
    resource_type = db.Column(db.Enum('low', 'medium', 'high', name='resource_type'))
    availability_status = db.Column(db.Enum('Available', 'Unavailable'), name='availabilityStatus')
    lender = db.relationship('Lender', back_populates='computational_resources')

class LendingRequests(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    borrower_id = db.Column(db.Integer, db.ForeignKey('borrower.borrower_id'))
    python_version = db.Column(db.String(255))
    required_dependencies = db.Column(db.String(255))
    estimated_workload = db.Column(db.Enum('low', 'medium', 'high', name='estimated_workload'))
    borrower = db.relationship('Borrower', back_populates='lending_requests')
