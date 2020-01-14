from datetime import datetime, timedelta, date

from flask_app import app, db
from flask_app.results import Result, get_most_recent, df_to_dict, filter_by, sort_by, average_by_day
from flask import render_template, jsonify, request
from flask_app.models import Article

from fastai.text import *
from sentinews.models import VaderAnalyzer
from sentinews.models import TextBlobAnalyzer
from sentinews.models import LSTMAnalyzer

DEFAULT_TIME_BACK = timedelta(days=14)
DEFAULT_DATA_POINTS_LIMIT = 50

import os
from dotenv import load_dotenv

load_dotenv()

dirname = os.path.dirname(__file__)
model_path = 'static/lstm_models/'

models = {
    'vader': VaderAnalyzer(),
    'textblob': TextBlobAnalyzer(),
    'lstm': LSTMAnalyzer(model_dir=os.environ.get('LSTM_PKL_MODEL_DIR'), model_name=os.environ.get('LSTM_PKL_FILENAME'))
}

db_results = Result()

# all_results = results.get_all_results(db)


@app.route('/')
def home():
    return render_template('home.html')


# todo: occasionally store data so it doesn't have to load everytime

@app.route('/data/', methods=['GET', 'POST'])
def data():
    """
    Finds the corresponding data requested for the given model.
    :return: JSON
    """

    # if request.method == 'POST':
    #     post_data = request.form  # specifying data range, news agency etc.
    # if 'num_days_back' in post_data:
    #     # todo: make it actually listen to the post request
    #     start = datetime.utcnow().date()
    #     first_index = get_date_index(start, all_results['dates_array'])
    #     if first_index is None:
    #         return None
    #     if first_index + int(post_data['num_days_back']) >= len(all_results['dates_array']):
    #         second_index = len(all_results['dates_array']) - 1
    #     else:
    #         second_index = first_index + int(post_data['num_days_back'])
    #
    #     return jsonify({
    #         'first_index': first_index,
    #         'second_index': second_index,
    #     })

    if request.method == 'GET':
        return jsonify(all_results)

    return ''


@app.route('/analyze/<model>', methods=['POST'])
def analyze(model):
    req = request.form['text']

    if model in models:
        return jsonify(models[model].evaluate(req))


@app.route('/data_test')
def data_test():
    return jsonify(df_to_dict(get_most_recent(db_results.df)))

@app.route('/cnn')
def cnn():
    return jsonify(df_to_dict(average_by_day(filter_by(db_results.df, 'news_co', 'cnn'))))

@app.route('/fox')
def fox():
    return jsonify(df_to_dict(average_by_day(filter_by(db_results.df, 'news_co', 'fox'))))

@app.route('/nyt')
def nyt():
    return jsonify(df_to_dict(average_by_day(filter_by(db_results.df, 'news_co', 'new york times'))))
