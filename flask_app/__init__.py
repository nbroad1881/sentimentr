import os
from celery import Celery
from datetime import datetime, timedelta, timezone
import logging

from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

from sentinews.title_finder import NEWSAPI

load_dotenv()
logging.basicConfig(level=logging.DEBUG)
HOURS_AGO = 8  # how many hours back should it check for recent articles

app = Flask(__name__)

# For local testing
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['LOCAL_DB_URL']

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DB_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['RABBITMQ_URL'] = os.environ['RABBITMQ_URL']


#  todo: make app load from config file

def make_celery(app):
    celery = Celery(
        app.import_name,
        broker=os.environ['RABBITMQ_URL'],
        backend=os.environ['RABBITMQ_URL'],
        include="flask_app"
    )
    celery.conf.update(app.config)

    # Arrange for tasks to have access to the Flask app
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask

    return celery


celery = make_celery(app)
db = SQLAlchemy(app)
ma = Marshmallow(app)

from flask_app import routes, db_models, schemas


@celery.task
def get_recent_articles():
    """
    Looks back a certain number of hours and finds the recent articles and then logs to database.
    To be used with celery and called periodically.
    :return: None
    :rtype: None
    """
    start_date = datetime.now(tz=timezone.utc) - timedelta(hours=HOURS_AGO)
    logging.info(start_date)
    num_steps = 4
    end_date = datetime.now(tz=timezone.utc)

    news_api = NEWSAPI(start_date=start_date, end_date=end_date, num_steps=num_steps)
    news_api.start()
    logging.info(news_api.get_articles_logged())


# Set up scheduler. Amount of time is 1 hour less than HOURS_AGO
# to ensure it covers the whole time period between calls.
celery.conf.beat_schedule = {
    "get-recent-articles": {
        "task": "flask_app.get_recent_articles",
        "schedule": timedelta(hours=HOURS_AGO - 1),
    },
}
