import os
import json

from dotenv import load_dotenv

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))

DB_TABLE_NAME = os.environ.get('DB_TABLE_NAME')
DB_SELECT_COLUMNS = json.loads(os.environ.get('DB_SELECT_COLUMNS'))
DB_PARSE_COLUMNS = json.loads(os.environ.get('DB_PARSE_COLUMNS'))
DB_DATETIME_COLUMN_NAME = os.environ.get('DB_DATETIME_COLUMN_NAME')

DB_ENDPOINT = os.environ.get('DB_ENDPOINT')
DB_USERNAME = os.environ.get('DB_USERNAME')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_NAME = os.environ.get('DB_NAME')
DB_PORT = os.environ.get('DB_PORT')
DB_URI = f"postgres://{DB_USERNAME}:{DB_PASSWORD}@{DB_ENDPOINT}:{DB_PORT}/{DB_NAME}"

class Config(object):
    in_dev = os.environ.get('IN_DEV', None)

    CELERY_BROKER_URL = os.environ.get('RABBITMQ_URL', '')
    CELERY_RESULT_BACKEND = CELERY_BROKER_URL

    CELERY_IMPORTS = ("get_recent_articles")

    SQLALCHEMY_DATABASE_URI = DB_URI
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ADMINS = os.environ.get('ADMIN')

    DB_SELECT_COLUMNS = os.environ.get('DB_SELECT_COLUMNS')


