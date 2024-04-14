from celery import Celery
from flask import Flask
from config import Config

# Assuming 'Config' or the actual Flask 'app' has the necessary CELERY configurations
app = Flask(__name__)
app.config.from_object(Config)

celery = Celery(
    app.import_name,
    backend=app.config['CELERY_RESULT_BACKEND'],
    broker=app.config['CELERY_BROKER_URL']
)
celery.conf.update(app.config)

class ContextTask(celery.Task):
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return self.run(*args, **kwargs)

celery.Task = ContextTask

# Use this if 'make_celery' still needs to be a function for other reasons
def make_celery():
    return celery
