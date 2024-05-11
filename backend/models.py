from .database import db
from flask_login import UserMixin 
from sqlalchemy.sql import func 
import json

class Lender(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    compensation_details = db.Column(db.String(255))

class Borrower(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    project_details = db.Column(db.String(255))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_type = db.Column(db.Enum('lender', 'borrower', name='user_type'))
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))

class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    request_file = db.Column(db.String(255), nullable=False)
    dependencies = db.Column(db.String(500), default=json.dumps([]))
    python_version = db.Column(db.String(10), default="3.8")
    status = db.Column(db.Enum('initiated', 'running', 'done', name='request_status'), default='initiated')
    
    def get_dependencies(self):
        return json.loads(self.dependencies)
    
    def set_dependencies(self, dependencies_list):
        self.dependencies = json.dumps(dependencies_list)

class Ressource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    resource_type = db.Column(db.Enum('low', 'medium', 'high', name='resource_types'), default='medium')
    available = db.Column(db.Boolean, default=True)
