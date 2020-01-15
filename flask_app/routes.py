from datetime import datetime, timedelta, date

from flask_app import app, db
from flask_app.results import Result, get_most_recent, df_to_dict, filter_by, get_data_for_chart, average_by_day, reverse_all
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

NEWS_COL_NAME = 'news_co'
CANDIDATE_COL_NAME = 'title'
CNN = 'cnn'
NYT = 'the new york times'
FOX = 'fox news'

TRUMP = 'trump'
BIDEN = 'biden'
WARREN = 'warren'
SANDERS = 'sanders'
HARRIS = 'harris'
BUTTIGIEG = 'buttigieg'

CANDIDATES = [TRUMP, BIDEN, WARREN, SANDERS, HARRIS, BUTTIGIEG]
NEWS_COMPANIES= [CNN, FOX, NYT]

db_results = Result()
all_recent = get_most_recent(db_results.df, num_entries=100)

# all means you want the most recent from each category, not the most recent all together
# all should be a list the length of the number of categories and each should have a length of
# whatever was specified in the parameters of get_most_recent
news_co_recent = {
    'all': []
}
for news_co in NEWS_COMPANIES:
    temp_df = get_most_recent(filter_by(db_results.df, NEWS_COL_NAME, news_co))
    news_co_recent[news_co] = reverse_all(temp_df)
    news_co_recent['all'].append(reverse_all(temp_df))

candidates_recent = {
}

for candidate in CANDIDATES:
    candidate_scores = {}
    temp_df = filter_by(db_results.df, CANDIDATE_COL_NAME, candidate)
    candidate_scores['all'] = reverse_all(get_most_recent(temp_df))

    for news_co in NEWS_COMPANIES:
        candidate_scores[news_co] = reverse_all(get_most_recent(filter_by(temp_df, NEWS_COL_NAME, news_co)))
    candidates_recent[candidate] = candidate_scores


# all_results = results.get_all_results(db)

# todo: maybe send data with return statement for home route

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
    return jsonify(df_to_dict(get_data_for_chart(get_most_recent(db_results.df))))

@app.route('/cnn')
def cnn():
    return jsonify(df_to_dict(cnn_recent))

@app.route('/fox')
def fox():
    return jsonify(df_to_dict(average_by_day(filter_by(db_results.df, 'news_co', 'fox'))))

@app.route('/nyt')
def nyt():
    return jsonify(df_to_dict(average_by_day(filter_by(db_results.df, 'news_co', 'new york times'))))


@app.route('/candidate/<name>')
def candidate(name):
    to_return = {}
    if name == 'all':
        for cand in CANDIDATES:
            to_return[cand] = {
                'all': df_to_dict(get_data_for_chart(candidates_recent[cand]['all']))
            }

            for news_co in NEWS_COMPANIES:
                to_return[cand][news_co] = df_to_dict(get_data_for_chart(candidates_recent[cand][news_co]))
        return jsonify(to_return)
    return jsonify({
            name: df_to_dict(get_data_for_chart(candidates_recent[name]))
        })


@app.route('/news_company/<name>')
def news_co(name):
    to_return = {}
    if name == 'all':
        for news in NEWS_COMPANIES:
            to_return[news] = df_to_dict(get_data_for_chart(news_co_recent[news]))

        return jsonify(to_return)
    return jsonify({
        name: df_to_dict(get_data_for_chart(news_co_recent[name]))
    })

# @app.route('/trump')
# def trump():
#     return jsonify(df_to_dict(candidates_recent[TRUMP]))
#
# @app.route('/biden')
# def biden():
#     return jsonify(df_to_dict(candidates_recent[BIDEN]))
#
# @app.route('/warren')
# def warren():
#     return jsonify(df_to_dict(candidates_recent[WARREN]))
#
# @app.route('/sanders')
# def trump():
#     return jsonify(df_to_dict(candidates_recent[SANDERS]))
#
# @app.route('/harris')
# def trump():
#     return jsonify(df_to_dict(candidates_recent[HARRIS]))
#
# @app.route('/buttigieg')
# def trump():
#     return jsonify(df_to_dict(candidates_recent[BUTTIGIEG]))