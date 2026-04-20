from .database import db
from flask_login import UserMixin
from datetime import datetime
import json
import uuid


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.String(150), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    user_type = db.Column(db.Enum('Lender', 'Borrower', name='user_type'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    lender = db.relationship("Lender", back_populates="user", uselist=False)
    requests = db.relationship("Request", back_populates="owner")


class Lender(db.Model):
    __tablename__ = 'lender'
    id = db.Column(db.Integer, primary_key=True)
    resource_type = db.Column(db.Enum('High', 'Medium', 'Low', name='resource_type_enum'), nullable=False)
    specification = db.Column(db.String(150), nullable=False)
    availability_status = db.Column(db.Enum('Available', 'Unavailable', name='availability_status_enum'), nullable=False)
    user_id = db.Column(db.String(150), db.ForeignKey('user.id'), nullable=False)

    user = db.relationship("User", back_populates="lender")
    requests = db.relationship("Request", back_populates="lender")


class Request(db.Model):
    __tablename__ = 'request'
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.String(150), db.ForeignKey('user.id'), nullable=False)
    lender_id = db.Column(db.Integer, db.ForeignKey('lender.id'), nullable=True)
    request_file = db.Column(db.String(255), nullable=True)
    dependencies = db.Column(db.String(500), default=json.dumps([]))
    python_version = db.Column(db.String(10), default="3.8")
    estimated_workload = db.Column(db.Enum('High', 'Medium', 'Low', name='workload_levels'), nullable=False)
    status = db.Column(db.Enum('initiated', 'running', 'done', 'error', name='request_status'), default='initiated')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    owner = db.relationship("User", back_populates="requests")
    lender = db.relationship("Lender", back_populates="requests")

    def get_dependencies(self):
        return json.loads(self.dependencies)

    def set_dependencies(self, dependencies_list):
        self.dependencies = json.dumps(dependencies_list)
