from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import User, UserType, Lender, Borrower
from . import db
from flask import flash

views = Blueprint('views', __name__)

lender_resources = []
borrower_requests = []


@views.route('/', methods=['POST', 'GET'])
@login_required
def home():
    print(f"Current user authenticated: {current_user.is_authenticated}")
    print(f"Current user ID: {getattr(current_user, 'id', 'No user')}")
    if request.method == 'POST':
        if current_user.user_type.name == "Lender":
            return redirect(url_for('views.add_resource'))
        elif current_user.user_type.name == "Borrower":
            return redirect(url_for('views.submit_request'))
    
    user_name = current_user.email if current_user.is_authenticated else "Guest"
    user_type = current_user.user_type.name if current_user.is_authenticated else "Guest"
    
    return render_template("home.html", user=current_user, user_name=user_name, user_type=user_type)
@views.route('/api/lenders/addResource', methods=['GET', 'POST'])
@login_required
def add_resource():
    
    if current_user.user_type_id != 1:
        flash("Unauthorized: Only lenders can add resources", category='error')
        return redirect(url_for('views.home'))
    
    if request.method == 'POST':
        resource_type = request.form.get('resource_type')
        specification=request.form.get('specification')
        availability_status = request.form.get('availabilityStatus')
        
        # Validate input
        if resource_type not in ["High", "Medium", "Low"]:
            flash("Invalid resource type", category='error')
        elif availability_status not in ["Available", "Not available"]:
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
    resources = Lender.query.filter_by(user_id=current_user.id).all()
    return render_template('viewResources.html', user=current_user, resources=resources)


# Routes for borrowers
@views.route('/api/borrowers/submitRequest', methods=['GET','POST'])
def submit_request():
    if current_user.user_type_id != 2:
        flash("Unauthorized: Only borrower can submit request", category='error')
        return redirect(url_for('views.home'))
    if request.method == 'POST':
        required_dependencies = request.form.getlist('requiredDependencies')
        estimated_workload = request.form.get('estimatedWorkload')
        python_version = request.form.get('pythonVersion')
        
        # check 
        if current_user.user_type_id == UserType.BORROWER:
            borrower = current_user.borrower
            
            new_request = Borrower(
                borrower_id = borrower.id,
                required_dependencies = required_dependencies,
                estimated_workload = estimated_workload,
                python_version = python_version
            )
            
            # add new request to the db 
            db.session.add(new_request)
            db.session.commit()
            
            flash("Request submitted success", category='success')
            return redirect(url_for('views.viewRequest'))
        else:
            flash('Failed to submit request. Please make sure you are logged in as a borrower.', category='error')
            return redirect(url_for('views.home'))
    return render_template('borrower.html', user=current_user)


@views.route('/api/borrowers/viewRequests', methods=['GET'])
@login_required
def view_requests():
    if current_user.user_type_id == UserType.BORROWER:
        requests = Borrower.query.filter_by(borrower_id=current_user.borrower.id).all()
        return render_template('viewRequests.html', user=current_user, requests=requests)
    else:
        flash('Unauthorized: Only borrowers can view requests', category='error')
        return redirect(url_for('views.home'))