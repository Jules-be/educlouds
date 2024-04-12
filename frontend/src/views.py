from flask import Blueprint, render_template, request, jsonify, redirect, url_for

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
    if request.method == 'POST':
        resource_type = request.form.get('type')
        specifications = request.form.get('specifications')
        availability_status = request.form.get('availabilityStatus')

        lender_resources.append({
            'type': resource_type,
            'specifications': specifications,
            'availabilityStatus': availability_status
        })
        return redirect(url_for('views.view_resources'))
    else:
        return render_template('lender.html')

@views.route('/api/lenders/viewResources', methods=['GET'])
def view_resources():
    return render_template('viewResources.html', resources=lender_resources)

# Routes for borrowers
@views.route('/api/borrowers/submitRequest', methods=['GET', 'POST'])
def submit_request():
    if request.method == 'POST':
        required_resources = request.form.get('requiredResources')
        estimated_workload = request.form.get('estimatedWorkload')
        preferred_os = request.form.get('preferredOS')

        borrower_requests.append({
            'requiredResources': required_resources,
            'estimatedWorkload': estimated_workload,
            'preferredOS': preferred_os
        })
        return redirect(url_for('views.view_requests'))
    else:
        return render_template('borrower.html')

@views.route('/api/borrowers/viewRequests', methods=['GET'])
def view_requests():
    return render_template('viewRequest.html', requests=borrower_requests)
