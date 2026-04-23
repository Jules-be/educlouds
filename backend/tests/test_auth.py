import pytest
from backend import create_app
from backend.database import db as _db
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


# --- Registration tests ---

def test_register_success(client):
    response = client.post('/api/users/register', data={
        'name': 'Test Lender',
        'email': 'lender@test.com',
        'password': 'password123',
        'user_type': 'Lender'
    }, follow_redirects=True)
    assert response.status_code == 200


def test_register_duplicate_email(client):
    data = {
        'name': 'Test User',
        'email': 'duplicate@test.com',
        'password': 'password123',
        'user_type': 'Lender'
    }
    client.post('/api/users/register', data=data, follow_redirects=True)
    response = client.post('/api/users/register', data=data, follow_redirects=True)
    assert b'Email already exists' in response.data


def test_register_invalid_user_type(client):
    response = client.post('/api/users/register', data={
        'name': 'Test User',
        'email': 'test@test.com',
        'password': 'password123',
        'user_type': 'Admin'
    }, follow_redirects=True)
    assert b'Invalid user type' in response.data


# --- Login tests ---

def test_login_success(client):
    # Register first
    client.post('/api/users/register', data={
        'name': 'Test User',
        'email': 'user@test.com',
        'password': 'password123',
        'user_type': 'Borrower'
    }, follow_redirects=True)
    # Then login
    response = client.post('/api/users/login', data={
        'email': 'user@test.com',
        'password': 'password123'
    }, follow_redirects=True)
    assert response.status_code == 200


def test_login_wrong_password(client):
    client.post('/api/users/register', data={
        'name': 'Test User',
        'email': 'user2@test.com',
        'password': 'password123',
        'user_type': 'Borrower'
    }, follow_redirects=True)
    response = client.post('/api/users/login', data={
        'email': 'user2@test.com',
        'password': 'wrongpassword'
    }, follow_redirects=True)
    assert b'Invalid email or password' in response.data


def test_login_unknown_email(client):
    response = client.post('/api/users/login', data={
        'email': 'nobody@test.com',
        'password': 'password123'
    }, follow_redirects=True)
    assert b'Invalid email or password' in response.data
