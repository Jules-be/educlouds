from flask import Blueprint, jsonify
from ..models import Lender, Request, User
from ..database import db

list = Blueprint('list', __name__)

@list.route('/lenders', methods=['GET'])
def get_lenders():
    lenders = Lender.query.all()
    return jsonify([{
        'id': lender.id,
        'user_id': lender.user_id,
        'resource_type': lender.resource_type,
        'specification': lender.specification,
        'availability_status': lender.availability_status
    } for lender in lenders])


@list.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{
        'id': user.id,
        'email': user.email,
        'user_type': user.user_type
    } for user in users])


