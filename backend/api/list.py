from flask import Blueprint, jsonify
from ..models import Lender, Borrower, User
from ..database import db

list = Blueprint('list', __name__)

@list.route('/lenders', methods=['GET'])
def get_lenders():
    lenders = Lender.query.all()
    return jsonify([{
        'id': lender.id, 
        'user_id': lender.user_id, 
        'resource_type': lender.resource_type,
        'specification' : lender.specification,
        'availability_status': lender.availability_status
    } for lender in lenders])


@list.route('/borrowers', methods=['GET'])
def get_borrowers():
    borrowers = Borrower.query.all()
    return jsonify([{
        'id': borrower.id,
        'user_id': borrower.user_id,
        'python_version': borrower.python_version,
        'required_dependencies': borrower.required_dependencies,
        'estimated_workload': borrower.estimated_workload
    } for borrower in borrowers])



@list.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{
        'id': user.id, 
        'email' : user.email,
        'user_type' : user.user_type.name
    } for user in users])


