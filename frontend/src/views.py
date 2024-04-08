from flask import Blueprint, render_template, request

views = Blueprint('views', __name__)

lender_resources = []
borrower_requests = []

# Home page
@views.route('/')
def home():
    return render_template("home.html")

# Routes for lenders
@views.route('/api/lenders/addResource', methods=['GET', 'POST'])
def add_resource():
    resource_type = request.form.get('type')
    specifications = request.form.get('specifications')
    availability_status = request.form.get('availabilityStatus')
    
    lender_resources.append({
        'type': resource_type,
        'specifications': specifications,
        'availabilityStatus': availability_status
    })
    
    success_message = 'Resource added successfully'
    
    return render_template('lender.html', message=success_message)

# Routes for borrowers
@views.route('/api/borrowers/submitRequest', methods=['GET', 'POST'])
def submit_request():
    required_resources = request.form.get('requiredResources')
    estimated_workload = request.form.get('estimatedWorkload')
    preferred_os = request.form.get('preferredOS')
    
    borrower_requests.append({
        'requiredResources': required_resources,
        'estimatedWorkload': estimated_workload,
        'preferredOS': preferred_os
    })
    
    success_message = 'Request submitted successfully'
    
    return render_template('borrower.html', message=success_message)
