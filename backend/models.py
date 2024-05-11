from enum import Enum
from . import db
from sqlalchemy import ForeignKey
from flask_login import UserMixin
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

class UserType(db.Model):
    __tablename__ = 'user_type'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Corrected ForeignKey reference
    project_details = db.Column(db.String(255))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_type = db.Column(db.Enum('lender', 'borrower', name='user_type'))  # Corrected enum definition
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    name = db.Column(db.String(150), unique=True, nullable=False)
    users = db.relationship("User", order_by="User.id", back_populates="user_type")

    LENDER = 1
    BORROWER = 2


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.String(150), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    user_type_id = db.Column(db.Integer, db.ForeignKey('user_type.id'))
    user_type = db.relationship("UserType", back_populates="users")
    lender = db.relationship("Lender", back_populates="user", uselist=False)
    borrower = db.relationship("Borrower", back_populates="user", uselist=False)


class Lender(db.Model):
    __tablename__ = 'lender'
    id = db.Column(db.Integer, primary_key=True)
    resource_type = db.Column(db.Enum("High", "Medium", "Low", name="resource_type_enum"), nullable=False)
    specification = db.Column(db.String(150), nullable=False)
    availability_status = db.Column(db.Enum('Available', 'Unavailable', name='availability_status_enum'), nullable=False)
    user_id = db.Column(db.String(150), db.ForeignKey('user.id'))
    user = db.relationship("User", back_populates="lender")


class Borrower(db.Model):
    __tablename__ = 'borrower'
    id = db.Column(db.Integer, primary_key=True)
    python_version = db.Column(db.String(20), nullable=False)
    required_dependencies = db.Column(db.Text, nullable=False)
    estimated_workload=db.Column(db.Enum("High", "Medium", "Low", name="estimated_workload", nullable=False))
    user_id = db.Column(db.String(150), db.ForeignKey('user.id'))
    user = db.relationship("User", back_populates="borrower")
