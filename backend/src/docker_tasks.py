from celery.utils.log import get_task_logger
from flask import current_app
import paramiko
import os

logger = get_task_logger(__name__)

def check_docker_installed(host, user, keypath):
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(host, username=user, key_filename=keypath)

        stdin, stdout, stderr = ssh_client.exec_command('which docker')
        docker_path = stdout.read().decode().strip()

        if docker_path:
            logger.info(f'Docker is installed at {docker_path}')

            stdin, stdout, stderr = ssh_client.exec_command('docker info')
            if not stderr.read().decode().strip():
                logger.info('Docker is running')
            else:
                logger.info('Docker is not running')
            ssh_client.close()
            return True
        else:
            logger.info('Docker is not installed')
            ssh_client.close()
            return False
    except Exception as e:
        logger.error(f'Error: {e}')
        return False

def generate_dockerfile(request_id, required_python_version, additional_packages):
    # Set the relative path to the instance requests directory
    request_dir = os.path.join(current_app.instance_path, 'requests', f'request_{request_id}')
    os.makedirs(request_dir, exist_ok=True)

    # Script filename based on the request ID
    script_filename = os.path.join(f"/tmp/request_{request_id}", f"{request_id}.py")

    # Define the path for the Dockerfile within the new directory
    dockerfile_path = os.path.join(request_dir, 'Dockerfile')

    # Content of the Dockerfile
    dockerfile_content = f"""
    FROM python:{required_python_version}
    WORKDIR /app
    COPY . /app
    RUN pip install --no-cache-dir {' '.join(additional_packages)}
    CMD ["python", "{script_filename}"]
    """

    # Write the Dockerfile
    with open(dockerfile_path, 'w') as dockerfile:
        dockerfile.write(dockerfile_content)
    logger.info(f"Dockerfile generated at {dockerfile_path}")
    return {"message": "Dockerfile generated successfully", "path": dockerfile_path}

def transfer_files_to_remote(request_id, host, username, keypath):
    try:
        local_request_dir = os.path.join(current_app.instance_path, 'requests', f'request_{request_id}')
        local_script_path = os.path.join(local_request_dir, f"{request_id}.py")
        local_dockerfile_path = os.path.join(local_request_dir, 'Dockerfile')

        if not os.path.exists(local_script_path) or not os.path.exists(local_dockerfile_path):
            raise FileNotFoundError("Script file or Dockerfile not found")

        remote_dir = f"/tmp/request_{request_id}"

        # Establish SSH connection
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=username, key_filename=keypath)

        # Create remote directory
        stdin, stdout, stderr = ssh.exec_command(f"mkdir -p {remote_dir}")
        stdout.channel.recv_exit_status()

        # Transfer files using SFTP
        sftp = ssh.open_sftp()
        sftp.mkdir(remote_dir, mode=511)  # Ensure the directory is created with correct permissions
        sftp.put(local_script_path, os.path.join(remote_dir, f"{request_id}.py"))
        sftp.put(local_dockerfile_path, os.path.join(remote_dir, 'Dockerfile'))
        sftp.close()

        ssh.close()
        logger.info(f"Files transferred successfully to {remote_dir}")
        return {"status": "success", "message": f"Files transferred to {remote_dir}"}
    except Exception as e:
        logger.error(f"Failed to transfer files: {e}")
        return {"status": "error", "message": str(e)}

def run_docker_script(request_id, host, username, keypath):
    try:
        # Establish SSH connection
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=username, key_filename=keypath)

        remote_dir = f"/tmp/request_{request_id}"
        remote_script_path = os.path.join(remote_dir, f"{request_id}.py")
        image_name = f"image_{request_id}"
        output_prefix = remote_dir

        # Commands to execute in the remote Docker
        commands = [
            f"cd {remote_dir} && docker build -t {image_name} -f Dockerfile . > {output_prefix}_build_output.txt 2> {output_prefix}_build_error.txt",
            f"docker run --rm {image_name} python {remote_script_path} > {output_prefix}_run_output.txt 2> {output_prefix}_run_error.txt",
            f"docker rmi {image_name}"
        ]

        # Execute each command and redirect outputs to files in the remote directory
        for command in commands:
            stdin, stdout, stderr = ssh.exec_command(command)
            # Wait for the command to complete
            exit_status = stdout.channel.recv_exit_status()
            if exit_status != 0:
                print(f"Command '{command}' failed with exit status {exit_status}")

        ssh.close()
        return {"status": "success", "message": "Docker script executed successfully"}
    except Exception as e:
        logger.error(f"Exception during Docker run: {e}")
        return {"status": "error", "message": str(e)}

def check_docker_status(request_id, host, username, keypath):
    from ..models import Request
    from ..database import db
    with current_app.app_context():

        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(host, username=username, key_filename=keypath)

            output_prefix = f"/tmp/{request_id}"
            output_files = {
                'build_output': f'{output_prefix}_build_output.txt',
                'build_error': f'{output_prefix}_build_error.txt',
                'run_output': f'{output_prefix}_run_output.txt',
                'run_error': f'{output_prefix}_run_error.txt'
            }

            results = {}
            errors_detected = False
            sftp = ssh.open_sftp()
            for key, file_path in output_files.items():
                try:
                    with sftp.open(file_path, 'r') as file_handle:
                        content = file_handle.read()
                        if 'error' in key and content.strip():
                            logger.error(f"{key} contains errors: {content}")
                            errors_detected = True
                        elif content.strip():
                            results[key] = content
                            logger.info(f"{key} output: {content}")
                        else:
                            logger.info(f"{key} is empty.")
                except IOError:
                    logger.error(f"Could not read {key} at {file_path}, assuming error.")
                    errors_detected = True

            if not errors_detected:
                # Transfer files back to the local server for user download
                local_dir = os.path.join(current_app.instance_path, 'downloads', f'request_{request_id}')
                os.makedirs(local_dir, exist_ok=True)
                for key, content in results.items():
                    local_file_path = os.path.join(local_dir, os.path.basename(output_files[key]))
                    with open(local_file_path, 'w') as file:
                        file.write(content)
                    logger.info(f"File {local_file_path} ready for download")

            sftp.close()
            ssh.close()

            # Update request status in the database
            request = Request.query.get(request_id)
            if request:
                new_status = 'done' if not errors_detected else 'error'
                request.status = new_status
                db.session.commit()
                return {'status': new_status, 'download_path': local_dir if not errors_detected else None}
            else:
                logger.error(f"Request with ID {request_id} not found.")
                return {'status': 'error'}

        except Exception as e:
            logger.error(f"Exception in checking Docker status: {e}")
            return {'status': 'error', 'message': str(e)}
