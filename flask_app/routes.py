import os
import logging
from datetime import datetime as dt, timezone, timedelta

from dateutil.parser import isoparse
from flask import request, render_template, jsonify
from dotenv import load_dotenv
from sqlalchemy.exc import IntegrityError

from flask_app import application, db
from flask_app.db_models import DBArticle, DBScore, COLUMN_NAMES, Weekly, Tabulator
from flask_app.schemas import ScoreSchema, WeeklySchema, TabulatorSchema
from sentinews.models import (VaderAnalyzer,
                              LSTMAnalyzer,
                              TextBlobAnalyzer,
                              BERTAnalyzer)

# articleSchema = ArticleSchema()
# articlesSchema = ArticleSchema(many=True)
weeklySchema = WeeklySchema(many=True)

scoresSchemas = ScoreSchema(many=True)
tabulatorSchema = TabulatorSchema(many=True)

load_dotenv()
logging.basicConfig(level=logging.DEBUG)

DB_TABLE_NAME = os.environ['DB_TABLE_NAME']
DB_URL = os.environ['DB_URL']
DB_PARSE_COLUMNS = os.environ['DB_PARSE_COLUMNS']
DB_SELECT_COLUMNS = os.environ['DB_SELECT_COLUMNS']

# va = VaderAnalyzer()
# tb = TextBlobAnalyzer()
# lstm = LSTMAnalyzer()
# bert = BERTAnalyzer()

DEFAULT_NUM_TO_QUERY = 20


# todo: add validation and verification for requests

# todo: make table object to avoid update error (table.c)
@application.route("/")
def home():
    return render_template("home.html", title='home'), 200


@application.route("/models")
def models():
    return render_template("models.html", title='models'), 200




def update_article_fields(article, **kwargs):
    keys = kwargs.keys()
    if 'datetime' in keys: article.datetime = kwargs['datetime']
    if 'title' in keys: article.title = kwargs['title']
    if 'news_co' in keys: article.news_co = kwargs['news_co']
    if 'text' in keys: article.text = kwargs['text']
    if 'vader_p_pos' in keys: article.vader_p_pos = kwargs['vader_p_pos']
    if 'vader_p_neg' in keys: article.vader_p_neg = kwargs['vader_p_neg']
    if 'vader_p_neu' in keys: article.vader_p_neu = kwargs['vader_p_neu']
    if 'vader_compound' in keys: article.vader_compound = kwargs['vader_compound']
    if 'textblob_p_pos' in keys: article.textblob_p_pos = kwargs['textblob_p_pos']
    if 'textblob_p_neg' in keys: article.textblob_p_neg = kwargs['textblob_p_neg']
    if 'lstm_p_pos' in keys: article.lstm_p_pos = kwargs['lstm_p_pos']
    if 'lstm_p_neu' in keys: article.lstm_p_neu = kwargs['lstm_p_neu']
    if 'lstm_p_neg' in keys: article.lstm_p_neg = kwargs['lstm_p_neg']


@application.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return "Page not found! Error 404", 404


def query_database(candidate, news, opinion, all=False):
    """
    Query the database with a specified candidate, news company, and whether opinion articles are wanted.
    :param candidate:
    :type candidate: str
    :param news:
    :type news: str
    :param opinion: True if opinion articles are wanted, False for no opinion articles
    :type opinion: bool
    :return:
    :rtype:
    """
    # todo: check that candidate and news are valid
    query = DBArticle.query
    if news:
        query = query.filter(DBArticle.news_co.ilike(f"%{news}%"))
    if candidate:
        query = query.filter(DBArticle.candidate.ilike(f"%{candidate}%"))
    if opinion:
        query = query.filter(DBArticle.url.contains('opinion'))
    if all:
        results = query.all()

    results = query.order_by(DBArticle.datetime.desc()). \
        limit(100).all()
    if results:
        results = results[::-1]
    return results


def check_password(headers):
    pw = headers.get('password')
    if pw:
        logging.info(pw + '\n' + os.environ['AUTH_PASSWORD'])
        logging.info(pw == os.environ['AUTH_PASSWORD'])
        return pw == os.environ['AUTH_PASSWORD']


@application.route('/update', methods=['PATCH'])
def update_all_rows():
    if request.method != 'PATCH':
        return 'Invalid method type', 405
    args = request.args.to_dict()
    for res in load_in_chunks():
        for article in res:
            title = article.title
            if 'vader' in args:
                va_scores = va.evaluate(title)
                article.vader_p_pos = va_scores['p_pos']
                article.vader_p_neg = va_scores['p_neg']
                article.vader_p_neu = va_scores['p_neu']
                article.vader_compound = va_scores['compound']
            if 'textblob' in args:
                tb_scores = tb.evaluate(title)
                article.p_pos = tb_scores['p_pos']
                article.p_neg = tb_scores['p_neg']
            if 'lstm' in args:
                lstm_scores = lstm.evaluate(title)
                article.lstm_p_pos = lstm_scores['p_pos']
                article.lstm_p_neg = lstm_scores['p_neg']
                article.lstm_p_neu = lstm_scores['p_neu']
            if 'bert' in args:
                bert_scores = bert.evaluate(title)
                article.bert_p_pos = bert_scores['p_pos']
                article.bert_p_neg = bert_scores['p_neg']
                article.bert_p_neu = bert_scores['p_neu']

    db.session.commit()

    return "Success", 200


def load_in_chunks():
    offset = 0
    chunk_size = 500

    while True:

        results = db.session.query(DBArticle). \
            filter(DBArticle.bert_p_pos == None). \
            limit(chunk_size).offset(offset).all()
        if results:
            yield results
        else:
            break
        offset += chunk_size


@application.route('/avg_test')
def avg_test():
    return jsonify(average_by_dates('trump', 'cnn'))


def average_by_dates(candidate, news_co):
    """
    # todo: add functionality to choose window size
    Starting at a designated date, this function will step 1 week at a time and calculate
    the average score for each model for the given candidate and news group.
    The function looks half the window size backwards in time and half the window size forwards in time
    to form the whole window that will be averaged.
    :param candidate: Name of candidate to filter by, e.g. Warren
    :type candidate:  str
    :param news_co: Name of news group to filter by, e.g. CNN
    :type news_co: str
    :return: List of dictionaries with date, bert_avg, lstm_avg, vader_avg, and textblob_avg as keys
    :rtype: list of dict
    """
    import time
    starting_date = dt.fromisoformat("2019-01-01 00:00+00:00")
    window_size = 3  # in weeks
    time_diff = dt.now(tz=timezone.utc) - starting_date
    num_weeks = time_diff / timedelta(days=7)
    to_return = []

    # focus_date is the date for the middle of the window
    focus_date = starting_date

    # Filter by date range, news group, and candidate
    results = DBArticle.query. \
        filter(DBArticle.news_co.ilike(f"%{news_co}%")). \
        filter(DBArticle.candidate.ilike(f"%{candidate}%")).all()

    t5 = time.perf_counter()
    for i in range(round(num_weeks)):
        t1 = time.perf_counter()
        temp_start = focus_date - timedelta(weeks=window_size / 2)
        temp_end = focus_date + timedelta(weeks=window_size / 2)

        t2 = time.perf_counter()

        b_sum, l_sum, v_sum, t_sum = 0, 0, 0, 0
        num_samples = len(results)

        for sample in results:
            b_sum += sample.scores.bert
            l_sum += sample.scores.lstm
            v_sum += sample.scores.vader
            t_sum += sample.scores.textblob

        bert_avg = b_sum / num_samples
        lstm_avg = l_sum / num_samples
        vader_avg = v_sum / num_samples
        textblob_avg = t_sum / num_samples
        #
        # # Calculate averages for each model type
        # num_elements = len(results)
        # bert_avg = round(sum([sample.scores.bert for sample in results])/num_elements, 3)
        # lstm_avg = round(sum([sample.scores.lstm for sample in results])/num_elements, 3)
        # vader_avg = round(sum([sample.scores.vader for sample in results])/num_elements, 3)
        # textblob_avg = round(sum([sample.scores.textblob for sample in results])/num_elements, 3)

        t3 = time.perf_counter()

        to_return.append({
            'date': focus_date,
            'bert_avg': bert_avg,
            'lstm_avg': lstm_avg,
            'vader_avg': vader_avg,
            'textblob_avg': textblob_avg,
        })

        focus_date += timedelta(weeks=1)

        t4 = time.perf_counter()

        print(f"1-2: {t2 - t1}", f"2-3: {t3 - t2}", f"3-4: {t4 - t3}", f"5-1: {t1 - t5}")

        t5 = time.perf_counter()

    return to_return


@application.route('/weekly')
def weekly():

    args = request.args.to_dict()
    news = args.get('news_co', None)
    candidate = args.get('candidate', None)

    if news is None or candidate is None:
        return "Please add candidate and news group", 400

    results = Weekly.query. \
        filter(Weekly.news_co.ilike(f"%{news}%")). \
        filter(Weekly.candidate.ilike(f"%{candidate}%")). \
        filter(Weekly.datetime > "2019-06-01").\
        order_by(Weekly.datetime.asc()).all()
    bert = []
    lstm = []
    vader = []
    textblob = []
    datetime = []
    for row in results:
        bert.append(row.bert)
        lstm.append(row.lstm)
        vader.append(row.vader)
        textblob.append(row.textblob)
        datetime.append(row.datetime)

    return jsonify({
        'bert': bert,
        'lstm': lstm,
        'vader': vader,
        'textblob': textblob,
        'datetime': datetime,
    }), 200


@application.route("/table")
def candidate_table():
    all_data = []
    for candidate in ['trump', 'biden', 'warren', 'harris', 'sanders', 'buttigieg']:
        results = Tabulator.query.\
            filter(Tabulator.candidate.ilike(f"%{candidate}%")).\
            order_by(Tabulator.datetime.desc()).\
            limit(5).all()
        all_data.extend(tabulatorSchema.jsonify(results, many=True).json)

    return jsonify(all_data)




