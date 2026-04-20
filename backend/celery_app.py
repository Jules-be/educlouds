from celery import Celery 
import os 

def make_celery(app):
    
    """
     Connects Celery to the Flask app so tasks can access
     the database and app config inside a worker.
    """
    celery = Celery(
        app.import_name,
        broker=app.config["CELERY_BROKER_URL"],
        backend=app.config["CELERY_RESULT_BACKEND"]
    )

    # This makes every Celery task run inside Flask's app context
    # so db.session, current_app, etc. all work inside tasks
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery


