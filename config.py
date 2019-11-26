import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    in_heroku = os.environ.get('IN_HEROKU', None)
    if in_heroku:
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
        LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
        SQLALCHEMY_TRACK_MODIFICATIONS = False
    else:
        ENDPOINT = os.environ.get('ENDPOINT')
        PORT = os.environ.get('PORT')
        USER = os.environ.get('USERNAME')
        PW = os.environ.get('PASSWORD')
        DBNAME = os.environ.get('DBNAME')
        SQLALCHEMY_DATABASE_URI = f"postgres://{USER}:{PW}@{ENDPOINT}:{PORT}/{DBNAME}"
        LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        SECRET_KEY = 'will-change-one-day'
        MAIL_SERVER = os.environ.get('MAIL_SERVER')
        MAIL_PORT = 465
        MAIL_USE_SSL = True
        MAIL_USE_TLS = False
        MAIL_USERNAME = os.environ.get('USERNAME')
        MAIL_PASSWORD = os.environ.get('PASSWORD')
        ADMINS = os.environ.get('ADMIN')


