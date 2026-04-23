import pytest
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


def login(client, email, password):
    return client.post('/api/users/login', data={
        'email' : email,
        'password' : password
    }, follow_redirects=True)

@pytest.fixture
def borrower_with_job(app):
    user = User(
        name = "Test Borrower",
        email = 'borrower@test.com',
        password = generate_password_hash('password123'),
        user_type = 'Borrower'
    )

    _db.session.add(user)
    _db.session.commit()

    job = Request(
        owner_id = user.id,
        estimated_workload = 'High',
        python_version = '3.9',
        status = 'initiated'
    )

    _db.session.add(job)
    _db.session.commit()
    return user, job

def test_status_return_job_status(client, borrower_with_job):
    user, job = borrower_with_job
    login(client=client, email='borrower@test.com', password='password123')

    response = client.get(f'/request/status/{job.id}')
    assert response.status_code == 200
    assert b'initiated' in response.data


def test_status_returns_404_for_unknown_job(client, borrower_with_job):                                                                                                                                         
      login(client, 'borrower@test.com', 'password123')                                                                                                                                                           
                                                                                                                                                                                                                  
      response = client.get('/request/status/9999')                                                                                                                                                             
      assert response.status_code == 404 

def test_status_rejects_wrong_user(client, app, borrower_with_job):                                                                                                                                             
      user, job = borrower_with_job                                                                                                                                                                               
                                                                                                                                                                                                                  
      other_user = User(                                                                                                                                                                                        
          name='Other User',                                                                                                                                                                                      
          email='other@test.com',                                                                                                                                                                               
          password=generate_password_hash('password123'),
          user_type='Borrower'
      )
      _db.session.add(other_user)                                                                                                                                                                                 
      _db.session.commit()
                                                                                                                                                                                                                  
      login(client, 'other@test.com', 'password123')                                                                                                                                                            

      response = client.get(f'/request/status/{job.id}')
      assert response.status_code == 403