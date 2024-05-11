from flask import Blueprint, jsonify
from ..models import Lender, Borrower, User
from ..database import db

list = Blueprint('list', __name__)

@list.route('/lenders', methods=['GET'])
def get_lenders():
    lenders = Lender.query.all()
    return jsonify([{'id': lender.id, 'user_id': lender.user_id, 'compensation_details': lender.compensation_details} for lender in lenders])

@list.route('/borrowers', methods=['GET'])
def get_borrowers():
    borrowers = Borrower.query.all()
    return jsonify([{'id': borrower.id, 'user_id': borrower.user_id, 'project_details': borrower.project_details} for borrower in borrowers])

@list.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{'id': user.id, 'user_type': user.user_type.value, 'email': user.email} for user in users])
