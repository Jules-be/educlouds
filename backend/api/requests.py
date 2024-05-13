from flask import Blueprint, request, render_template, send_from_directory, jsonify, redirect, url_for, flash, current_app
from backend.src.docker_tasks import generate_dockerfile, check_docker_installed, run_docker_script, transfer_files_to_remote, transfer_files_from_remote
from flask_login import login_required, current_user
from ..models import Request
from ..database import db
import json
import os

req_blueprint = Blueprint('request', __name__)

ALLOWED_EXTENSIONS = {'py'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@req_blueprint.route('/new', methods= ['GET', 'POST'])
def new_request():
    if request.method == 'POST':
        if current_user.user_type_id != 2:
            flash("Unauthorized: Only borrowers can submit requests", category='error')
            return redirect(url_for('views.home'))

        # Ensure a file is present and is of allowed type
        file = request.files['file']
        if not file or not allowed_file(file.filename):
            flash("Invalid or no file uploaded", category='error')
            return redirect(url_for('requests.new_request'))
        
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
            new_request.status = "error"
            db.session.commit()
            flash("Docker is not installed on the specified host", category='error')
            return redirect(url_for('requests.new_request'))
        
        # Generate Dockerfile based on the Python version and dependencies
        dockerfile_task = generate_dockerfile(new_request.id, new_request.python_version, new_request.dependencies)
        if 'error' in dockerfile_task:
            new_request.status = "error"
            db.session.commit()
            flash("Failed to generate Dockerfile", category='error')
            return redirect(url_for('requests.new_request'))

        transfer_task = transfer_files_to_remote(new_request.id, host, user, key_path)
        if 'error' in transfer_task:
            new_request.status = "error"
            db.session.commit()
            flash("Failed to transfer files to remote host", category='error')
            return redirect(url_for('requests.new_request'))

        run_docker_task = run_docker_script(new_request.id, host, user, key_path)
        if 'error' in run_docker_task:
            new_request.status = "error"
            db.session.commit()
            transfer_files_from_remote(request_id, host, user, key_path)
            flash("Failed to run the script in Docker container", category='error')
            return redirect(url_for('requests.view_requests'))

        flash("Request submitted successfully", category='success')
        new_request.status = "done"
        db.session.commit()
        transfer_files_from_remote(request_id, host, user, key_path)
        return redirect(url_for('request.view_requests'))
    return render_template('request.html')

@login_required
@req_blueprint.route('/view_requests', methods=['GET'])
def view_requests():
    if current_user.user_type_id != 2:
        flash('Unauthorized: Only borrowers can view requests', category='error')
        return redirect(url_for('views.home'))

    requests = Request.query.filter_by(owner_id=current_user.id).all()
    return render_template('view_request.html', requests=requests)

@req_blueprint.route('/result/<int:request_id>', methods=['GET'])
@login_required
def download_result(request_id):
    req = Request.query.get(request_id)
    if not req:
        return jsonify({"error": "Request not found"}), 404

    if req.owner_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    # Define the directory where results are stored
    results_dir = os.path.join(current_app.instance_path, 'requests', f'request_{request_id}')

    # Determine which file to serve based on the status of the request
    if req.status == 'done':
        output_file = 'output.txt'
    elif req.status == 'error':
        output_file = 'error.txt'
    else:
        return jsonify({"message": "Request is still running"}), 202

    # Check if the file exists
    file_path = os.path.join(results_dir, output_file)
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    # Attempt to read the file and return its contents
    try:
        with open(file_path, 'r') as file:
            file_contents = file.read()
        return jsonify({"filename": output_file, "contents": file_contents})
    except IOError as e:
        # If an error occurred during file reading
        return jsonify({"error": "Failed to read file", "exception": str(e)}), 500