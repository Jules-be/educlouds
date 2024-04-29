import pytest
from unittest.mock import patch, MagicMock, mock_open
import paramiko
import os
from flask import Flask
from src.docker_tasks import generate_dockerfile, check_docker_installed, run_in_docker

app = Flask(__name__)

@pytest.mark.celery
@patch('src.docker_tasks.os.makedirs')
@patch('src.docker_tasks.open', new_callable=mock_open)
def test_generate_dockerfile(mock_open, mock_makedirs):
    with app.app_context():
        task = generate_dockerfile.s('3.8', ['flask', 'requests'])
        result = task.apply()
        assert 'Dockerfile generated successfully' in result.result['message']

@pytest.mark.celery
@patch('src.docker_tasks.paramiko.SSHClient')
def test_check_docker_installed(mock_ssh_client):
    with app.app_context():
        mock_ssh = MagicMock()
        mock_ssh_client.return_value = mock_ssh
        mock_ssh.exec_command.return_value = (MagicMock(), MagicMock(), MagicMock())
        mock_ssh.exec_command.return_value[1].read.return_value = b'/usr/bin/docker'
        mock_ssh.exec_command.return_value[2].read.return_value = b''
    
        host_ip = '34.16.200.24'
        user = 'Jules'
        key_path = os.path.expanduser('~/.ssh/gcp')
    
        key = paramiko.RSAKey.from_private_key_file(key_path)
    
        task = check_docker_installed.s(host_ip, user, key_path)
        result = task.apply()
    
        assert result.result is True

@pytest.mark.celery
@patch('src.docker_tasks.paramiko.SSHClient')
def test_run_in_docker(mock_ssh_client):
    with app.app_context():
        mock_ssh = MagicMock()
        mock_ssh_client.return_value = mock_ssh
        mock_ssh.exec_command.return_value = (MagicMock(), MagicMock(), MagicMock())
        mock_ssh.exec_command.return_value[1].read.return_value = b'Successfully built'
        mock_ssh.exec_command.return_value[2].read.return_value = b''
    
        host_ip = '34.16.200.24'
        user = 'Jules'
        key_path = os.path.expanduser('~/.ssh/gcp')
    
        key = paramiko.RSAKey.from_private_key_file(key_path)
    
        task = run_in_docker.s('../../requests/test_request.py', host_ip, user, key_path)
        result = task.apply()
    
        assert 'Successfully built' in result.result['output']
