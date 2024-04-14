from celery import Celery
from flask import current_app
from config import CeleryConfig as Config

celery = Celery(
    __name__,
    backend=Config.CELERY_RESULT_BACKEND,
    broker=Config.CELERY_BROKER_URL
)

celery.conf.update(Config.__dict__)  # Assuming all necessary configurations are in Config class

class ContextTask(celery.Task):
    def __call__(self, *args, **kwargs):
        with current_app.app_context():
            return self.run(*args, **kwargs)

celery.Task = ContextTask
