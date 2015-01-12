class Config(object):
    CSRF_ENABLED = True
    SECRET_KEY = 'secret key'
    SECURITY_PASSWORD_SALT = 'secret key'
    MAIL_FROM = 'info@example.com'
    BROKER_URL = 'amqp://guest:guest@localhost:5672//'
    AWS_ACCESS = None
    AWS_SECRET = None
    BABEL_DEFAULT_TIMEZONE = 'US/Eastern'
    CELERY_BROKER_URL = "amqp://guest:guest@localhost:5672//"

class ProdConfig(Config):
    DEBUG = False
    SECRET_KEY = None
    SECURITY_PASSWORD_SALT = None
    SQLALCHEMY_DATABASE_URI = None
    SQLALCHEMY_ECHO = False
    S3_BUCKET = 'slides'

class DevConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://dev:dev@localhost/dev'
    SQLALCHEMY_ECHO = True
    ASSETS_DEBUG = True
    S3_BUCKET = 'slides-dev'
