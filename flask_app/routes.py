from datetime import datetime, timedelta

from flask_app import app, mail, db
from flask import render_template, url_for, jsonify
from flask_app.models import Article
from flask_mail import Message

DEFAULT_TIME_BACK = timedelta(days=14)
DEFAULT_DATA_POINTS_LIMIT = 50


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
    results = db.session.query(info).\
        order_by(info.c.date.desc()).\
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
