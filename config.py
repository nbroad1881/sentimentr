import os
import json


basedir = os.path.abspath(os.path.dirname(__file__))

with open('info.json', 'r') as json_file:
    user_info = json.load(json_file)


class Config(object):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'will-change-one-day'
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USE_TLS = False
    MAIL_USERNAME = user_info['gmail_username']
    MAIL_PASSWORD = user_info['gmail_password']
    ADMINS = user_info['admins']
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')