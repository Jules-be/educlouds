from celery.utils.log import get_task_logger
from flask import current_app
import paramiko
import os

from ..celery_app import celery

logger = get_task_logger(__name__)

@celery.task
def run_job_pipeline(request_id, python_version, dependencies, host, user, key_path):
    """
    Celery task: runs the full Docker pipeline for a submitted job.
    Called with .delay() so it runs in the background.
    Steps:
    1. Check Docker is installed on remote host
    2. Generate Dockerfile
    3. Transfer files to remote via SFTP
    4. Run script inside Docker container
    5. Download results back
    6. Update job status in DB
    """

    from ..models import Request
    from ..database import db

    req = Request.query.get(request_id)
    if not req:
        logger.error(f"Request {request_id} not found")
        return

    try:
        req.status = "running"
        db.session.commit()

        if not check_docker_installed(host, user, key_path):
            req.status = "error"
            db.session.commit()
            return

        result = generate_dockerfile(request_id=request_id, python_version=python_version, dependencies=dependencies)
        if "error" in result:
            req.status = "error"
            db.session.commit()
            return

        result = transfer_files_to_remote(request_id=request_id, host=host, username=user, keypath=key_path)
        if "error" in result:
            req.status = "error"
            db.session.commit()
            return

        result = run_docker_script(request_id=request_id, host=host, username=user, keypath=key_path)
        if result.get("status") == "error":
            req.status = "error"
            db.session.commit()
            transfer_files_from_remote(request_id, host, username=user, keypath=key_path)
            return

        transfer_files_from_remote(request_id=request_id, host=host, username=user, keypath=key_path)
        req.status = "done"
        db.session.commit()
        logger.info(f"Job {request_id} completed successfully")

    except Exception as e:
        logger.error(f"Job {request_id} failed: {e}")
        req.status = "error"
        db.session.commit()


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


def generate_dockerfile(request_id, python_version, dependencies):
    # Set the relative path to the instance requests directory
    request_dir = os.path.join(current_app.instance_path, 'requests', f'request_{request_id}')
    os.makedirs(request_dir, exist_ok=True)

    # Define the path for the Dockerfile within the new directory
    dockerfile_path = os.path.join(request_dir, 'Dockerfile')

    import json
    deps = json.loads(dependencies) if isinstance(dependencies, str) else dependencies

    dockerfile_content = f"FROM python:{python_version}\n"
    dockerfile_content += "WORKDIR /app\n"
    dockerfile_content += "COPY . /app\n"
    if deps:
        pip_packages = " ".join(deps)
        dockerfile_content += f"RUN pip install {pip_packages}\n"
    dockerfile_content += f'CMD ["python", "{request_id}.py"]\n'

    # Write the Dockerfile
    with open(dockerfile_path, 'w') as dockerfile:
        dockerfile.write(dockerfile_content)
    logger.info(f"Dockerfile generated at {dockerfile_path}")
    return {"message": "Dockerfile generated successfully", "path": dockerfile_path}


def transfer_files_to_remote(request_id, host, username, keypath):
    local_request_dir = os.path.join(current_app.instance_path, 'requests', f'request_{request_id}')
    local_script_path = os.path.join(local_request_dir, f"{request_id}.py")
    local_dockerfile_path = os.path.join(local_request_dir, 'Dockerfile')

    if not os.path.exists(local_script_path) or not os.path.exists(local_dockerfile_path):
        raise FileNotFoundError("Script file or Dockerfile not found")

    # Establish SSH connection
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=username, key_filename=keypath)

    # Transfer files using SFTP
    sftp = ssh.open_sftp()

    # Define the remote directory path where files will be uploaded
    remote_dir = f"/home/Jules/requests/request_{request_id}"

    try:
        sftp.mkdir(remote_dir)
    except IOError as e:
        print(f"Failed to create directory {remote_dir}: {e}")

    sftp.put(local_script_path, os.path.join(remote_dir, f"{request_id}.py"))
    sftp.put(local_dockerfile_path, os.path.join(remote_dir, 'Dockerfile'))
    sftp.close()

    ssh.close()
    logger.info(f"Files transferred successfully to {remote_dir}")
    return {"status": "success", "message": f"Files transferred to {remote_dir}"}


def run_docker_script(request_id, host, username, keypath):
    try:
        # Establish SSH connection
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=username, key_filename=keypath)

        remote_dir = f"/home/Jules/requests/request_{request_id}"
        image_name = f"image_{request_id}"
        output_prefix = os.path.join(remote_dir, f"request_{request_id}")

        # Commands to execute in the remote Docker
        commands = [
            f"cd {remote_dir} && docker build -t {image_name} -f Dockerfile . > {output_prefix}_build_output.txt 2> {output_prefix}_build_error.txt",
            f"docker run --rm {image_name} python {request_id}.py > {output_prefix}_run_output.txt 2> {output_prefix}_run_error.txt",
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


def transfer_files_from_remote(request_id, host, username, keypath):
    local_request_dir = os.path.join(current_app.instance_path, 'requests', f'request_{request_id}')

    if not os.path.exists(local_request_dir):
        raise FileNotFoundError("Script file or Dockerfile not found")

    # Establish SSH connection
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=username, key_filename=keypath)

    # Transfer files using SFTP
    sftp = ssh.open_sftp()

    # Define the remote directory path where files will be uploaded
    remote_dir = f"/home/Jules/requests/request_{request_id}"

    try:
        sftp.mkdir(remote_dir)
    except IOError as e:
        print(f"Failed to create directory {remote_dir}: {e}")

    sftp.get(os.path.join(remote_dir, f"request_{request_id}_run_error.txt"), os.path.join(local_request_dir, "error.txt"))
    sftp.get(os.path.join(remote_dir, f"request_{request_id}_run_output.txt"), os.path.join(local_request_dir, "output.txt"))
    sftp.close()
    ssh.close()
    logger.info(f"Files transferred successfully to {local_request_dir}")
    return {"status": "success", "message": f"Files transferred to {local_request_dir}"}
