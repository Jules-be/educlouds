from flask import Blueprint, request, send_from_directory, jsonify, redirect, url_for, flash, current_app
from backend.src.docker_tasks import generate_dockerfile, check_docker_installed, run_docker_script, transfer_files_to_remote
from flask_login import login_required, current_user
from ..models import Request
from ..database import db
import json
import os

req_blueprint = Blueprint('request', __name__)

ALLOWED_EXTENSIONS = {'py'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@req_blueprint.route('/new', methods=['POST'])
def new_request():
    # Ensure a file is present and is of allowed type
    file = request.files['file']
    if not file or not allowed_file(file.filename):
        flash("Invalid or no file uploaded", category='error')
        return redirect(url_for('home'))
    
    # Get dependencies from the form as a comma-separated string
    dependencies = request.form.get('dependencies', '').strip()

    # Convert the comma-separated string to a list, trimming spaces around names
    dependencies_list = [dep.strip() for dep in dependencies.split(',') if dep.strip()]

    # Save the initial request to the database to obtain an ID
    new_request = Request(
        owner_id=current_user.id,
        dependencies=json.dumps(dependencies_list),
        estimated_workload=request.form.get('estimated_workload', 'Low'),
        python_version=request.form.get('python_version', '3.8'),
        status="initiated"
    )
    db.session.add(new_request)
    db.session.commit()

    # Construct file path using the request ID
    request_id = new_request.id
    
    # Construct file path using the request ID
    request_id = new_request.id
    requests_dir = os.path.join(current_app.instance_path, 'requests', f'request_{request_id}')
    os.makedirs(requests_dir, exist_ok=True)

    filename = f"{request_id}.py"
    upload_path = os.path.join(requests_dir, filename)
    file.save(upload_path)

    # Update the database with the file path
    new_request.request_file = upload_path
    db.session.commit()
    flash("Request submitted successfully", category='success')

    # Perform Docker operations using Celery tasks
    host = '34.16.200.24'
    user = 'Jules'
    key_path = os.path.expanduser('~/.ssh/gcp')

    # Trigger Docker operations asynchronously
    docker_check = check_docker_installed(host, user, key_path)
    if not docker_check:
        new_request.status = "failed"
        db.session.commit()
        return jsonify({'error': 'Docker is not installed on the specified host'}), 500
    print('\nDocker checked\n')

    # Generate Dockerfile based on the Python version and dependencies
    dockerfile_task = generate_dockerfile(new_request.id, new_request.python_version, new_request.dependencies)
    if 'error' in dockerfile_task:
        new_request.status = "failed"
        db.session.commit()
        return jsonify({'error': 'Failed to generate Dockerfile'}), 500
    print('\nDockerfile generated\n')

    transfer_task = transfer_files_to_remote(new_request.id, host, user, key_path)
    if 'error' in transfer_task:
        new_request.status = "failed"
        db.session.commit()
        return jsonify({'error': 'Failed to transfer files to remote host'}), 500
    print('\nFiles transferred\n')

    run_docker_task = run_docker_script(new_request.id, host, user, key_path)
    if 'error' in run_docker_task:
        new_request.status = "failed"
        db.session.commit()
        return jsonify({'error': 'Failed to run the script in Docker container'}), 500
    print('\nRun in docker\n')

    return jsonify({'request_id': new_request.id}), 202

# @req_blueprint.route('/check_request/<int:request_id>', methods=['GET'])
# @login_required
# def check_request(request_id):
#     request_instance = Request.query.get(request_id)
#     if not request_instance:
#         return jsonify({'error': 'Request not found'}), 404

#     # Check the current status and provide appropriate user feedback
#     if request_instance.status in ['running', 'done', 'error']:
#         return jsonify({
#             'request_id': request_id,
#             'status': request_instance.status,
#             'task_status': task.state,
#             'task_result': task.result if task.state == 'SUCCESS' else str(task.info)
#         })
#     else:
#         return jsonify({"error": "Invalid request status"}), 400

@req_blueprint.route('/result/<int:request_id>', methods=['GET'])
@login_required
def download_result(request_id):
    req = Request.query.get(request_id)
    if not req:
        return jsonify({"error": "Request not found"}), 404

    if req.owner_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    # Define the directory where results are stored
    results_dir = os.path.join(current_app.instance_path, 'downloads', f'request_{request_id}')

    # Determine which file to serve based on the status of the request
    if req.status == 'done':
        output_file = 'run_output.txt'
    elif req.status == 'error':
        output_file = 'run_error.txt'
    else:
        return jsonify({"message": "Request is still running"}), 202

    # Check if the file exists
    file_path = os.path.join(results_dir, output_file)
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    # Send the file from the directory
    try:
        return send_from_directory(directory=results_dir, filename=output_file, as_attachment=True, download_name=output_file)
    except Exception as e:
        return jsonify({"error": "Failed to serve file"}), 500