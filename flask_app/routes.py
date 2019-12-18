from datetime import datetime, timedelta
import json

from fastai.text import *

from flask_app import app, db
from flask import render_template, url_for, jsonify, request
from flask_app.models import Article, Score
from sentinews.models.vader import VaderAnalyzer
from sentinews.models.textblob import TextBlobAnalyzer
from sentinews.models.lstm import LSTMAnalyzer

DEFAULT_TIME_BACK = timedelta(days=14)
DEFAULT_DATA_POINTS_LIMIT = 50

import os

dirname = os.path.dirname(__file__)
model_path = 'static/lstm_models/'

models = {
    'vader': VaderAnalyzer(),
    'textblob': TextBlobAnalyzer(),
    'lstm': LSTMAnalyzer(model_dir=os.path.join(dirname, model_path))
}


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/about')
def about():
    return render_template('about.html', title='About')


@app.route('/bagofwords')
def bagofwords():
    return render_template('bagofwords.html', title='Bag of Words')


@app.route('/vader')
def vader():
    return render_template('vader.html', title='VADER')


@app.route('/news/<agency>')
def news(agency):
    # For pages about news agencies
    return ''


@app.route('/lstm_models/<model>')
def model_page(model):
    return render_template('model.html', model=model)


# todo: occasionally store data so it doesn't have to load everytime

@app.route('/data/', methods=['GET', 'POST'])
def data():
    """
    Finds the corresponding data requested for the given model.
    :return: JSON
    """

    if request.method == 'POST':
        post_data = request.data  # specifying data range, news agency etc.
    if request.method == 'GET':
        query = [c for c in Article.__table__.c if c.name != 'text']
        results = db.session.query(*query).\
            order_by(Article.datetime.desc()). \
            limit(DEFAULT_DATA_POINTS_LIMIT).all()

        return jsonify([r._asdict() for r in results])


    return ''


@app.route('/analyze/<model>', methods=['POST'])
def analyze(model):

    req = request.form['text']

    if model in models:
        return jsonify(models[model].evaluate(req))


@app.route('/data_test')
def data_test():
    results = db.session.query(Article).order_by(Article.datetime.desc()). \
        limit(DEFAULT_DATA_POINTS_LIMIT).all()
    return jsonify([r.to_dict() for r in results])


@app.route('/vader_data')
def vader_data():
    """
    returns data as json.
    currently gets results one week in the past
    :return:
    """
    info = db.Table('vader_scores', db.metadata, autoload=True, autoload_with=db.engine)
    today = datetime.utcnow()
    other_date = datetime.utcnow() - DEFAULT_TIME_BACK

    # filter(info.c.date.between(other_date, today)).\
    results = db.session.query(info). \
        order_by(info.c.date.desc()). \
        limit(DEFAULT_DATA_POINTS_LIMIT).all()

    return jsonify(results)


@app.route('/textblob')
def textblob():
    return render_template('textblob.html', title='TextBlob')


@app.route('/bert')
def bert():
    return render_template('bert.html', title='BERT')


@app.route('/lstm')
def lstm():
    return render_template('lstm.html', title='LSTM')


@app.route('/comparison')
def comparison():
    return render_template('comparison.html', title='Model Comparison')
