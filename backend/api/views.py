from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from ..models import Lender, Borrower
from ..database import db
from flask import flash
from werkzeug.utils import secure_filename
import os 
from flask import current_app

views = Blueprint('views', __name__)

ALLOWED_EXTENSIONS = {'py'}

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
    if current_user.user_type_id != 1:
        flash("Unauthorized: Only lenders can view resources", category='error')
        return redirect(url_for('views.home'))
    resources = Lender.query.filter_by(user_id=current_user.id).all()
    return render_template('viewResources.html', user=current_user, resources=resources)


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@views.route('/api/borrowers/submitRequest', methods=['GET', 'POST'])
@login_required
def submit_request():
    # Return the form page if the method is GET
       # Check user permissions
    if current_user.user_type_id != 2:  # Assuming 2 is the ID for 'borrower'
        flash("Unauthorized: Only borrowers can submit requests", category='error')
        return redirect(url_for('views.home'))
    
    if request.method != 'POST':
        return render_template('borrower.html', user=current_user)
    
    # File handling
    if 'file' not in request.files:
        flash("No file part", category='error')
        return redirect(url_for('views.home'))
    
    file = request.files['file']
    if file.filename == '':
        flash("No selected file", category='error')
        return redirect(url_for('views.home'))
    
    if not allowed_file(file.filename):
        flash("Invalid file type", category='error')
        return redirect(url_for('views.home'))

    # Save the file
    filename = secure_filename(file.filename)
    upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(upload_path), exist_ok=True)
    file.save(upload_path)
    
    # Form data processing
    python_version = request.form.get('pythonVersion')
    required_dependencies = request.form.get('requiredDependencies')
    estimated_workload = request.form.get('estimatedWorkload')
    
    # Database record creation
    new_request = Borrower(
        required_dependencies=required_dependencies,
        estimated_workload=estimated_workload,
        python_version=python_version,
        user_id = current_user.id
    )
    db.session.add(new_request)
    db.session.commit()
    
    flash("Request submitted successfully", category='success')
    return redirect(url_for('views.view_requests'))

@views.route('/api/borrowers/viewRequests', methods=['GET'])
@login_required
def view_requests():
    if current_user.user_type_id != 2:
        flash('Unauthorized: Only borrowers can view requests', category='error')
        return redirect(url_for('views.home'))
    requests = Borrower.query.filter_by(user_id=current_user.id).all()
    return render_template('viewRequest.html', requests=requests)