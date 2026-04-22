from backend import create_app
from backend.celery_app import celery

flask_app = create_app()
