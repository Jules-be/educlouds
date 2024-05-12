class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "973b8d7253c024d2cb6d0055c1472935d74d8fcfbe5e9620ed31c267da038b25"
    SQLALCHEMY_DATABASE_URI = "sqlite:///database.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = 86400
    ALLOWED_EXTENSIONS = {'py'}    

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

class CeleryConfig:
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'