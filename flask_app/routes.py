from datetime import datetime, timedelta, date
import json

from fastai.text import *

from sqlalchemy import and_
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

CANDIDATES = ['TRUMP', 'BIDEN', 'SANDERS', 'WARREN', 'HARRIS', 'BUTTIGIEG']
NEWS_COMPANIES = ['CNN', 'NEW YORK TIMES', 'FOX NEWS']


def custom_average(scores, dates, return_dates=False):

    window_size = 1
    end_date = dates[-1]

    start_date = dates[0]
    future_date = start_date - timedelta(days=window_size)

    averaged_scores = []
    new_dates = [start_date]
    index = 0
    temp_sum = 0
    counter = 0
    while start_date > end_date and index < len(scores):
        # Sum up scores when in time window
        if start_date >= dates[index] > future_date:
            temp_sum += scores[index]
            counter += 1
        #     When out of window, append average, reset counters, shift dates
        else:
            if counter == 0:
                average = 0
            else:
                average = temp_sum / counter
            averaged_scores.append(average)

            temp_sum = 0
            counter = 0
            new_dates.append(future_date)
            start_date = future_date
            future_date = start_date - timedelta(days=window_size)

        index += 1

    if return_dates:
        return averaged_scores, new_dates
    return averaged_scores


"""
Return as dictionary of lists
"""


def organize_lists(titles, vader_scores, textblob_scores, lstm_scores, news_co, dates):
    return {
        'titles': titles,
        'vader': vader_scores,
        'textblob': textblob_scores,
        'lstm': lstm_scores,
        'news_co': news_co,
        'dates': dates
    }


def sort_by_date(date1, num_days, content):

    date2 = date1 + timedelta(days=num_days)
    # new_titles = [content['titles'][i] for i, date in enumerate(content['dates']) if date1 <= date < date2]
    # new_vader = [content['vader_scores'][i] for i, date in enumerate(content['dates']) if date1 <= date < date2]
    # new_vader_avg = [content['vader_averaged'][i] for i, date in enumerate(content['dates']) if date1 <= date < date2]
    # new_textblob = [content['textblob_scores'][i] for i, date in enumerate(content['dates']) if date1 <= date < date2]
    # new_textblob_avg = [content['textblob_averaged'][i] for i, date in enumerate(content['dates']) if date1 <= date < date2]
    # new_lstm = [content['lstm_scores'][i] for i, date in enumerate(content['dates']) if date1 <= date < date2]
    # new_lstm_avg = [content['lstm_averaged'][i] for i, date in enumerate(content['dates']) if date1 <= date < date2]
    # new_news_co = [content['news_co'][i] for i, date in enumerate(content['dates']) if date1 <= date < date2]
    # new_dates = [content['dates'][i] for i, date in enumerate(content['dates']) if date1 <= date < date2]
    # new_dates_avg = [content['dates_averaged'][i] for i, date in enumerate(content['dates']) if date1 <= date < date2]
    new_titles = []
    new_vader = []
    new_vader_avg = []
    new_textblob = []
    new_textblob_avg = []
    new_lstm = []
    new_lstm_avg = []
    new_news_co = []
    new_dates = []
    new_dates_avg = []
# todo: averaged dates array is shorter than all dates array
    for index, date in enumerate(content['dates']):
        if date1 <= date < date2:
            new_titles.append(content['titles'][index]),
            new_vader.append(content['vader'][index]),
            new_vader_avg.append(content['vader_averaged'][index]),
            new_textblob.append(content['textblob'][index]),
            new_textblob_avg.append(content['textblob_averaged'][index]),
            new_lstm.append(content['lstm'][index]),
            new_lstm_avg.append(content['lstm_averaged'][index]),
            new_news_co.append(content['news_co'][index]),
            new_dates.append(content['dates'][index]),
            new_dates_avg.append(content['dates_averaged'][index]),

    return {
        'titles': new_titles,
        'vader': new_vader,
        'textblob': new_textblob,
        'lstm': new_lstm,
        'news_co': new_news_co,
        'dates': new_dates,
        'vader_averaged': new_vader_avg,
        'textblob_averaged': new_textblob_avg,
        'lstm_averaged': new_lstm_avg,
        'dates_averaged': new_dates_avg
    }


def sort_by_candidate(candidates, titles, vader_scores, textblob_scores, lstm_scores, news_co, dates):
    results = {}
    for candidate in candidates:
        results[candidate] = []
        for index, title in enumerate(titles):
            if candidate in title.upper():
                results[candidate].append((title,
                                           vader_scores[index],
                                           textblob_scores[index],
                                           lstm_scores[index],
                                           news_co[index],
                                           dates[index]))
    return results


# todo: don't forget about news_co
def sort_by_news_co(news_companies, titles, vader_scores, textblob_scores, lstm_scores, news_co, dates):
    results = {}
    for news_name in news_companies:
        results[news_name] = []
        for index, title in enumerate(titles):
            if news_name in title.upper():
                results[news_name].append((title,
                                           vader_scores[index],
                                           textblob_scores[index],
                                           lstm_scores[index],
                                           news_co[index],
                                           dates[index]))
    return results


def lists_from_results(results):
    """
    Go from list of dictionaries to list of lists.
    Each sub-list is a category e.g. 'title'
    :param results:
    :return:
    """
    joined = [
        (
            res['title'],
            res['vader_positive'] - res['vader_negative'],
            res['textblob_p_pos'] - res['textblob_p_neg'],
            res['lstm_p_pos'] - res['lstm_p_neg'],
            res['news_co'],
            res['datetime']
        )
        for res in results
    ]
    return list(zip(*joined))

def organize_results(results):
    titles = [res['title'] for res in results]
    vader_scores = [res['vader_positive'] - res['vader_negative'] for res in results]
    textblob_scores = [res['textblob_p_pos'] - res['textblob_p_neg'] for res in results]
    lstm_scores = [res['lstm_p_pos'] - res['lstm_p_neg'] for res in results]
    news_co = [res['news_co'] for res in results]
    dates = [res['datetime'] for res in results]
    vader_averaged, dates_averaged = custom_average(vader_scores, dates, return_dates=True)

    return {
        'titles': titles,
        'vader': vader_scores,
        'textblob': textblob_scores,
        'lstm': lstm_scores,
        'news_co': news_co,
        'dates': dates,
        'vader_averaged': vader_averaged,
        'textblob_averaged': custom_average(textblob_scores, dates),
        'lstm_averaged': custom_average(lstm_scores, dates),
        'dates_averaged': dates_averaged
    }


query = [c for c in Article.__table__.c if c.name != 'text']

six_months_ago = date.today() - timedelta(days=180)
up_to = date.today()

queried_results = db.session.query(*query). \
    order_by(Article.datetime.desc()). \
    filter(Article.datetime >= six_months_ago). \
    filter(Article.datetime <= up_to)

dict_results = [r._asdict() for r in queried_results.all()]
all_content = organize_results(dict_results)

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
        post_data = request.form  # specifying data range, news agency etc.
        if 'num_days' in post_data:
            start = datetime.fromisoformat('2019-12-01')
        return jsonify(sort_by_date(start, int(post_data['num_days']), all_content))

    if request.method == 'GET':
        return jsonify(all_content)

    return ''


@app.route('/analyze/<model>', methods=['POST'])
def analyze(model):
    req = request.form['text']

    if model in models:
        return jsonify(models[model].evaluate(req))


@app.route('/data_test')
def data_test():
    return jsonify(all_content)


@app.route('/vader_data')
def vader_data():
    """
    returns data as json.
    currently gets results one week in the past
    :return:
    """

    return jsonify([one_day,
                    two_day_avg_vader,
                    three_day_avg_vader,
                    four_day_avg_vader,
                    five_day_avg_vader,
                    six_day_avg_vader,
                    seven_day_avg_vader])


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
