from flask import Blueprint, render_template, request, jsonify, redirect, url_for, current_app as app
import os 
import uuid
from ..src.docker_tasks import generate_dockerfile, check_docker_installed, run_in_docker
from ..src.file_verification import run_bandit, run_safety

views = Blueprint('views', __name__)

lender_resources = []
borrower_requests = []

UPLOAD_FOLDER = '../../requests/'

# Home page
@views.route('/')
def home():
    return render_template("home.html")

# Routes for lenders
@views.route('/api/lenders/addResource', methods=['POST'])
def add_resource():
    resource_type = request.form.get('type')
    specifications = request.form.getlist('specifications')  # Use getlist to get multiple values
    availability_status = request.form.get('availabilityStatus')

    lender_resources.append({
        'type': resource_type,
        'specifications': specifications,
        'availabilityStatus': availability_status
    })
    return redirect(url_for('views.view_resources'))

@views.route('/api/lenders/viewResources', methods=['GET'])
def view_resources():
    return render_template('viewResources.html', resources=lender_resources)

# Routes for borrowers
from flask import request, jsonify
import os
import uuid

@views.route('/api/borrowers/submitRequest', methods=['POST'])
def submit_request():
    # Check if 'file' is present in the request files
        if 'file' not in request.files:
            return 'No file part', 400
        
        file = request.files['file']
        
        # Check if file is selected
        if file.filename == '':
            return 'No selected file', 400
        
        # Save the uploaded Python file 
        filename = str(uuid.uuid4()) + '.py' 
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Check if dependencies, python version, and resources are provided in the request 
        required_dependencies = request.form.getlist('dependencies')
        python_version = request.form.get('pythonVersion')
        required_resources = request.form.get('requiredResources')
        
        # Perform security checks 
        bandit_output = run_bandit(filepath)
        safety_output = run_safety('requirement.txt')
        
        # Check for security issues 
        if "ERROR" in bandit_output or "ERROR" in safety_output:
            return jsonify({'error': 'Security check failed', 'bandit': bandit_output, 'safety': safety_output}), 400 
        
        # Generate Dockerfile asynchronously
        task_chain = (generate_dockerfile.s(python_version, required_dependencies, required_resources) | 
                    check_docker_installed.s(host='example_host', username='user', password='pass') | 
                    run_in_docker.s(filepath=filepath, ssh_host='ssh_host', ssh_user='ssh_user', ssh_key_path='path_to_ssh_key'))
        
        # Apply the task asynchronously
        result = task_chain.apply_async()

    # Return the response with a message and task ID
        return jsonify({"message": "Processing started", "task_id": result.id}), 202

@views.route('/api/borrowers/viewRequests', methods=['GET'])
def view_requests():
    return render_template('viewRequest.html', requests=borrower_requests)
