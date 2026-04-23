import pytest
import json
from io import BytesIO
from backend import create_app
from backend.database import db as _db
from backend.models import User, Lender, Request
from config import TestingConfig
from werkzeug.security import generate_password_hash


@pytest.fixture
def app():
    app = create_app(TestingConfig)
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def borrower(app):
    user = User(
        name='Test Borrower',
        email='borrower@test.com',
        password=generate_password_hash('password123'),
        user_type='Borrower'
    )
    _db.session.add(user)
    _db.session.commit()
    return user


@pytest.fixture
def lender_resource(app):
    user = User(
        name='Test Lender',
        email='lender@test.com',
        password=generate_password_hash('password123'),
        user_type='Lender'
    )
    _db.session.add(user)
    _db.session.commit()

    resource = Lender(
        resource_type='High',
        specification='16GB RAM',
        availability_status='Available',
        user_id=user.id
    )
    _db.session.add(resource)
    _db.session.commit()
    return resource


def login(client, email, password):
    return client.post('/api/users/login', data={
        'email': email,
        'password': password
    }, follow_redirects=True)


# --- Job submission tests ---

def test_submit_job_success(client, borrower, lender_resource):
    login(client, 'borrower@test.com', 'password123')

    data = {
        'python_version': '3.9',
        'dependencies': 'numpy',
        'estimated_workload': 'High',
        'file': (BytesIO(b"print('hello')"), 'test.py')
    }
    response = client.post('/request/new',
        data=data,
        content_type='multipart/form-data',
        follow_redirects=True
    )
    assert response.status_code == 200
    assert Request.query.count() == 1


def test_submit_job_requires_login(client):
    response = client.post('/request/new', follow_redirects=True)
    assert b'login' in response.data.lower()


def test_submit_job_lender_cannot_submit(client, lender_resource):
    login(client, 'lender@test.com', 'password123')

    data = {
        'python_version': '3.9',
        'dependencies': '',
        'estimated_workload': 'High',
        'file': (BytesIO(b"print('hello')"), 'test.py')
    }
    response = client.post('/request/new',
        data=data,
        content_type='multipart/form-data',
        follow_redirects=True
    )
    assert b'Only borrowers' in response.data
