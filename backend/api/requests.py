from flask import Blueprint, request, render_template, send_from_directory, jsonify, redirect, url_for, flash, current_app
from backend.src.docker_tasks import run_job_pipeline
from flask_login import login_required, current_user
from ..models import Request
from ..database import db
from ..src.matching import find_best_lender
import json
import os

req_blueprint = Blueprint('request', __name__)

ALLOWED_EXTENSIONS = {'py'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@req_blueprint.route('/new', methods= ['GET', 'POST'])
def new_request():
    if request.method == 'POST':
        if current_user.user_type != "Borrower":
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

        # Match the request to the best available lender
        matched_lender = find_best_lender(new_request.estimated_workload)
        if not matched_lender:
            flash("No available lenders at the moment. Please try again later.", category='error')
            return redirect(url_for('request.new_request'))

        new_request.lender_id = matched_lender.id
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

        # Hand off Docker pipeline to Celery worker (runs in background)
        host = current_app.config['SSH_HOST']
        user = current_app.config['SSH_USER']
        key_path = current_app.config['SSH_KEY_PATH']

        run_job_pipeline.delay(
            new_request.id,
            new_request.python_version,
            new_request.dependencies,
            host,
            user,
            key_path
        )

        flash("Job submitted! Check your requests page for status updates.", category='success')
        return redirect(url_for('request.view_requests'))
    return render_template('request.html')


@login_required
@req_blueprint.route('/view_requests', methods=['GET'])
def view_requests():
    if current_user.user_type != "Borrower":
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


@req_blueprint.route('/status/<int:request_id>', methods=['GET'])
@login_required
def job_status(request_id):
    req = Request.query.get(request_id)
    if not req:
        return jsonify({"error": "Request not found"}), 404
    if req.owner_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
    return jsonify({"status": req.status})