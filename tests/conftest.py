import pytest
from frontend.src import create_app, create_database


@pytest.fixture()
def app():
    app = create_app()
    with app.app_context():
        create_database(app)
    yield app

@pytest.fixture()
def client(app):
    return app.test_client()
