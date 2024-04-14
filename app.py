from backend import create_app
from backend.celery_worker import celery

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
