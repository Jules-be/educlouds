from flask import Flask, request, jsonify
import paramiko
import uuid
from file_verification import run_bandit, run_safety

app = Flask(__name__)

def check_docker_installed(host, username, password):
    try:
        # Create an SSH client
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(host, username=username, password=password)

        # Check if Docker is installed
        stdin, stdout, stderr = ssh_client.exec_command('which docker')
        docker_path = stdout.read().decode().strip()
        if docker_path:
            print(f'Docker is installed at {docker_path}')

            # Check if Docker daemon is running
            stdin, stdout, stderr = ssh_client.exec_command('docker info')
            if not stderr.read().decode().strip():
                print('Docker is running')
            else:
                print('Docker is not running')
        else:
            print('Docker is not installed')

        ssh_client.close()
    except Exception as e:
        print(f'Error: {e}')

def run_in_docker(filepath, ssh_host, ssh_user, ssh_key_path):
    # Set up SSH connection
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ssh_host, username=ssh_user, key_filename=ssh_key_path)

    # Generate a unique image name
    image_name = f'my_python_script_{uuid.uuid4()}'

    # Build and run the Docker container remotely via SSH
    commands = [
        f'docker build -t {image_name} -f Dockerfile .',
        f'docker run --rm {image_name}',
        f'docker rmi {image_name}'
    ]
    output = ""
    for command in commands:
        stdin, stdout, stderr = ssh.exec_command(command)
        output += stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        if error:
            return {'error': error}

    # Close SSH connection
    ssh.close()

    return {'output': output}

if __name__ == '__main__':
    app.run(debug=True)
