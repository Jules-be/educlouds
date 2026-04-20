from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from ..models import Lender, Request
from ..database import db
import os

views = Blueprint('views', __name__)

ALLOWED_EXTENSIONS = {'py'}





@views.route('/', methods=['POST', 'GET'])
@login_required
def home():
    print(f"Current user authenticated: {current_user.is_authenticated}")
    print(f"Current user ID: {getattr(current_user, 'id', 'No user')}")
    if request.method == 'POST':
        if current_user.user_type == "Lender":
            return redirect(url_for('views.add_resource'))
        elif current_user.user_type == "Borrower":
            return redirect(url_for('request.new_request'))

    user_name = current_user.name if current_user.is_authenticated else "Guest"
    user_type = current_user.user_type if current_user.is_authenticated else "Guest"
    
    return render_template("home.html", user=current_user, user_name=user_name, user_type=user_type)
@views.route('/api/lenders/addResource', methods=['GET', 'POST'])
@login_required
def add_resource():
    
    if current_user.user_type != "Lender":
        flash("Unauthorized: Only lenders can add resources", category='error')
        return redirect(url_for('views.home'))
    
    if request.method == 'POST':
        resource_type = request.form.get('type')
        specification=request.form.get('specification')
        availability_status = request.form.get('availabilityStatus')
        
        # Validate input
        if resource_type not in ["High", "Medium", "Low"]:
            flash("Invalid resource type", category='error')
        elif availability_status not in ["Available", "Unavailable"]:
            flash("Invalid availability status", category='error')
        elif not specification:
            flash("Specification is required", category='error')
        else:
            new_resource = Lender(
                resource_type=resource_type,
                specification=specification,
                availability_status=availability_status,
                user_id = current_user.id 
            )
            db.session.add(new_resource)
            db.session.commit()
            flash("Resource added successfully", category='success')
            return redirect(url_for('views.view_resources'))
    return render_template('lender.html', user=current_user)
           

@views.route('/api/lenders/viewResources', methods=['GET'])
@login_required
def view_resources():
    if current_user.user_type != "Lender":
        flash("Unauthorized: Only lenders can view resources", category='error')
        return redirect(url_for('views.home'))
    resources = Lender.query.filter_by(user_id=current_user.id).all()
    return render_template('viewResources.html', user=current_user, resources=resources)


@views.route('/api/lenders/dashboard', methods=['GET'])
@login_required
def lender_dashboard():
    if current_user.user_type != "Lender":
        flash("Unauthorized: Only lenders can view this dashboard", category='error')
        return redirect(url_for('views.home'))

    lender = Lender.query.filter_by(user_id=current_user.id).first()
    if not lender:
        flash("No resource registered. Please add a resource first.", category='error')
        return redirect(url_for('views.add_resource'))

    assigned_jobs = Request.query.filter_by(lender_id=lender.id).order_by(Request.created_at.desc()).all()
    return render_template('dashboard.html', user=current_user, lender=lender, jobs=assigned_jobs)