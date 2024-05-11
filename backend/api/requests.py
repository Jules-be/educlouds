from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from database import db
from backend.celery_worker import celery
from backend.src.docker_tasks import generate_dockerfile, check_docker_installed, run_in_docker
from ..models import Request
import os

app = Flask(__name__)

@app.route('/new_request', methods=['POST'])
def new_request():
    data = request.json
    filepath = data['filepath']
    host = '34.16.200.24'
    user = 'Jules'
    key_path = os.path.expanduser('~/.ssh/gcp')
    required_python_version = data.get('python_version', '3.8')
    additional_packages = data.get('additional_packages', [])
    dependencies = data.get('dependencies', [])
    
    # Create a new Request entry in the database
    new_request = Request(
        request_file=filepath,
        python_version=required_python_version,
        status="initiated"
    )
    new_request.set_dependencies(dependencies)
    db.session.add(new_request)
    db.session.commit()

    # Check if Docker is installed on the remote machine using SSH key for authentication
    docker_check = check_docker_installed.delay(host, user, key_path)
    is_docker_installed = docker_check.get(timeout=10)

    if not is_docker_installed:
        new_request.status = "failed"
        db.session.commit()
        return jsonify({'error': 'Docker is not installed on the specified host'}), 500

    # Generate Dockerfile based on the Python version and dependencies
    dockerfile_task = generate_dockerfile.delay(new_request.id, required_python_version, additional_packages)
    dockerfile_result = dockerfile_task.get(timeout=10)

    if 'error' in dockerfile_result:
        new_request.status = "failed"
        db.session.commit()
        return jsonify({'error': 'Failed to generate Dockerfile'}), 500

    # Run the Docker process using SSH key for authentication
    run_task = run_in_docker.delay(new_request.id, filepath, host, user, key_path)
    new_request.status = "running"
    db.session.commit()

    return jsonify({'request_id': new_request.id, 'task_id': run_task.id}), 202

@app.route('/check_request/<request_id>', methods=['GET'])
def check_request(request_id):
    request_instance = Request.query.get(request_id)
    if not request_instance:
        return jsonify({'error': 'Request not found'}), 404

    task = celery.AsyncResult(request_instance.task_id)
    return jsonify({
        'request_id': request_id,
        'status': request_instance.status,
        'task_status': task.state,
        'task_result': task.result if task.state == 'SUCCESS' else str(task.info)
    })

if __name__ == '__main__':
    app.run(debug=True)
