from celery.utils.log import get_task_logger
import paramiko
import uuid
import os
from ..celery_worker import celery

logger = get_task_logger(__name__)

@celery.task(bind=True)
def generate_dockerfile(self, required_python_version, additional_packages):
    # Set the relative path to the requests directory
    requests_dir = '../../requests/'
    # Create a unique directory for this task within the requests directory
    request_dir = os.path.join(requests_dir, f'request_{self.request.id}')
    os.makedirs(request_dir, exist_ok=True)

    # Define the path for the Dockerfile within the new directory
    dockerfile_path = os.path.join(request_dir, 'Dockerfile')

    # Content of the Dockerfile
    dockerfile_content = f"""
    FROM python:{required_python_version}
    WORKDIR /app
    COPY . /app
    RUN pip install --no-cache-dir {' '.join(additional_packages)}
    CMD ["python", "your_script.py"]
    """

    # Write the Dockerfile
    with open(dockerfile_path, 'w') as dockerfile:
        dockerfile.write(dockerfile_content)

    logger.info(f"Dockerfile generated at {dockerfile_path}")
    return {"message": "Dockerfile generated successfully", "path": dockerfile_path}


@celery.task(bind=True)
def check_docker_installed(self, host, user, password):
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(host, username=user, password=password)

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

@celery.task(bind=True)
def run_in_docker(self, filepath, host, user, password):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=user, password=password)

        image_name = f'my_python_script_{uuid.uuid4()}'
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
                ssh.close()
                return {'error': error}

        ssh.close()
        return {'output': output}
    except Exception as e:
        logger.error(f'Exception during Docker run: {e}')
        return {'error': str(e)}
