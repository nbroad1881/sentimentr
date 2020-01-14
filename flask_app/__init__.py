import logging

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
# todo: utilize migrate
from flask_migrate import Migrate
from celery import Celery
from sentinews.scraping.newsapi_scraper import NewsAPIScraper


from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)


migrate = Migrate(app, db)


def make_celery(app):
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
    return celery

celery = make_celery(app)
napi = NewsAPIScraper(limited=True)

@celery.task(ignore_result=True)
def find_new_articles():
    napi.get_titles()
    napi.db.close_session()

from flask_app import routes, models
