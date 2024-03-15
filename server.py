from flask import Flask, request, jsonify
import subprocess
import os
import uuid

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    if file:
        filename = str(uuid.uuid4()) + '.py'
        filepath = os.path.join('./uploads', filename)
        file.save(filepath)

        # Run the script in a Docker container
        result = run_in_docker(filepath)

        # Clean up the uploaded file
        os.remove(filepath)

        return jsonify(result), 200

def run_in_docker(filepath):
    # Generate a unique image name
    image_name = f'my_python_script_{uuid.uuid4()}'

    # Build the Docker image
    build_command = f'docker build -t {image_name} -f Dockerfile .'
    subprocess.run(build_command, shell=True, check=True)

    # Run the Docker container
    run_command = f'docker run --rm {image_name}'
    process = subprocess.Popen(run_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = process.communicate()

    # Remove the Docker image
    remove_command = f'docker rmi {image_name}'
    subprocess.run(remove_command, shell=True, check=True)

    if stderr:
        return {'error': stderr.decode('utf-8')}
    return {'output': stdout.decode('utf-8')}

if __name__ == '__main__':
    app.run(debug=True)
