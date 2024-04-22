from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import User, Lender, Borrower, ComputationalResources, LendingRequests
from . import db
from flask import flash



views = Blueprint('views', __name__)

lender_resources = []
borrower_requests = []

# Home page
@views.route('/', methods=['POST', 'GET'])
@login_required
def home():
    if request.method == 'POST':
        role = request.form.get('role')
        if role == 'lender':
            return redirect(url_for('views.add_resource'))
        elif role == 'borrower':
            return redirect(url_for('views.submit_request'))
    return render_template("home.html", user=current_user)

@views.route('/api/lenders/addResource', methods=['GET', 'POST'])
@login_required
def add_resource():
    if request.method == 'POST':
        resource_type = request.form.get('resource_type')
        availability_status = request.form.get('availabilityStatus')

        # Get the current user (lender)
        lender = current_user.lender.lender_id

        # Create a new computational resource associated with the lender
        new_resource = ComputationalResources(
            lender_id=lender,
            resource_type=resource_type,
            availability_status=availability_status
        )

        # Add the new resource to the database session and commit
        db.session.add(new_resource)
        db.session.commit()

        return redirect(url_for('views.view_resources'))

    else:
        return render_template('lender.html', user=current_user)

@views.route('/api/lenders/viewResources', methods=['GET'])
@login_required
def view_resources():
    # Ensure we're getting the lender object and its ID correctly
    lender_id = current_user.lender.lender_id  # Use the primary key field name of the Lender model
    
    # Retrieve all resources associated with the current lender from the database
    resources = ComputationalResources.query.filter_by(lender_id=lender_id).all()

    return render_template('viewResources.html', resources=resources, user=current_user)


# Routes for borrowers
@views.route('/api/borrowers/submitRequest', methods=['POST'])
def submit_request():
    if request.method == 'POST':
        required_resources = request.form.get('requiredResources')
        estimated_workload = request.form.get('estimatedWorkload')
        preferred_os = request.form.get('preferredOS')

        # Check if the current user is authenticated and has a borrower associated with it
        if current_user.is_authenticated and current_user.borrower:
            borrower = current_user.borrower

            # Create a new lending request associated with the borrower
            new_request = LendingRequests(
                borrower_id=borrower,
                required_dependencies=required_resources,
                estimated_workload=estimated_workload,
                python_version=preferred_os
            )

            # Add the new request to the database session and commit
            db.session.add(new_request)
            db.session.commit()

            return redirect(url_for('views.view_requests'))
        else:
            flash('Failed to submit request. Please make sure you are logged in as a borrower.', category='error')
            return redirect(url_for('views.home'))

    else:
        return render_template('borrower.html', user=current_user)
    

@views.route('/api/borrowers/viewRequests', methods=['GET'])
@login_required
def view_requests():
    # Get the current user (borrower)
    borrower = current_user.borrower

    # Retrieve all requests associated with the current borrower from the database
    requests = LendingRequests.query.filter_by(borrower_id=borrower.id).all()

    return render_template('viewRequest.html', requests=requests, user=current_user)