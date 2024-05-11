from frontend.src.models import UserType, User
def test_login_page(client):
    response = client.get('/api/users/login')
    assert response.status_code == 200
    assert b"Login" in response.data  # Check for some expected content in the login page.
    
def test_login(client):
    login_data = {
        'username': ' leila1@gmail.com',
        'password': '123456789'
    }
    response = client.post('/api/users/login', data=login_data)
    assert response.status_code == 200  

def test_registeration(client):
    response = client.get('/api/users/register')
    assert response.status_code == 200
    assert b"Register" in response.data

def test_valid_registeration(client):
    response = client.post('/api/users/register', data={
        'user_type_id': UserType.BORROWER,  # Use actual UserType values
        'email': 'newuser@example.com',
        'password': 'strongpassword'
    })
    assert response.status_code == 200

def test_registeration2(client, app):
    response = client.post('/api/users/register', data={
        "user_type_id":UserType.BORROWER,
        "email":"leila1@gmail.com",
        "password":"123456789"
    })
    with app.app_context():
        user_count = len( User.query.all())
        assert user_count == 2