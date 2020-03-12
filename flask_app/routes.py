import os
import logging
from datetime import datetime as dt, timezone, timedelta

from dateutil.parser import isoparse
from flask import request, render_template, jsonify
from dotenv import load_dotenv
from sqlalchemy.exc import IntegrityError

from flask_app import app, db
from flask_app.db_models import DBArticle, DBScore, COLUMN_NAMES, Weekly
from flask_app.schemas import ArticleSchema, ScoreSchema, WeeklySchema
from sentinews.models import (VaderAnalyzer,
                              LSTMAnalyzer,
                              TextBlobAnalyzer,
                              BERTAnalyzer)

articleSchema = ArticleSchema()
articlesSchema = ArticleSchema(many=True)
weeklySchema = WeeklySchema(many=True)

scoresSchemas = ScoreSchema(many=True)

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

COLUMNS_TO_QUERY = [
    DBArticle.url,
    DBArticle.datetime,
    DBArticle.title,
    DBArticle.news_co,
    DBArticle.vader_p_pos,
    DBArticle.vader_p_neg,
    DBArticle.textblob_p_pos,
    DBArticle.textblob_p_neg,
    DBArticle.lstm_p_pos,
    DBArticle.lstm_p_neg,
    DBArticle.bert_p_pos,
    DBArticle.bert_p_neg,
]

DEFAULT_NUM_TO_QUERY = 20


# todo: add validation and verification for requests

# todo: make table object to avoid update error (table.c)
@app.route("/")
def home():
    return render_template("home.html", title='home'), 200


@app.route("/models")
def models():
    return render_template("models.html", title='models'), 200


@app.route("/urls", methods=["GET"])
def urls():
    """
    Get all the urls in the database
    :return:
    :rtype:
    """
    if check_password(request.headers) is False:
        return "Unauthorized", 401
    articles = DBArticle.query.with_entities(DBArticle.url, DBArticle.title).all()
    return articlesSchema.jsonify(articles, many=True), 200


@app.route("/article/", methods=['GET', 'POST', 'PUT'])
def article_route():
    """
    Get, post, and put to retrieve, modify, or insert a single article or many articles.
    Requests must specify in parameters the desired candidate, news company, and whether
    the article is an opinion piece or not.
    Possible parameters
    candidate: string of candidate's name (e.g. Biden, Harris)
    news: string of news company (e.g. New York, Fox, CNN)
    opinion: True/False
    :return:
    :rtype:
    """
    args = request.args.to_dict()
    if args is None:
        logging.debug(f"No parameters given: {args}")
        return "No parameters given", 400

    if check_password(request.headers) is False:
        return "Unauthorized", 401

    # Pull one article from the database by finding matching url
    if request.method == 'GET':

        # make sure url parameter passed
        if 'url' in args:
            # returns None if not in database
            article = DBArticle.query.filter_by(url=args['url']).first()
            if article:
                return articleSchema.dump(article), 200
            return 'Url not found', 404

        query_results = query_database(candidate=args.get('candidate'),
                                       news=args.get('news'),
                                       opinion=args.get('opinion'))
        # If the query finds anything
        if query_results:
            return articlesSchema.jsonify(query_results, many=True), 200
        return 'Invalid parameters', 400

    # Create new article in database
    if request.method == 'POST':

        parameters = {}
        # Make sure they include the right parameters
        for col in COLUMN_NAMES:
            if col not in args:
                logging.debug(f"Invalid parameters to post request: {args}")
                return 'Invalid parameters', 400
            parameters[col] = args[col]

        # Check if the article is already in the database
        if DBArticle.query.filter_by(url=args['url']).first():
            return 'Already exists, use PUT to update', 409

        # All validations passed, create article and add to database
        article = articleSchema.load(args)
        db.session.add(article)
        db.session.commit()
        return 'Article added successfully', 201

    if request.method == 'PUT':
        # returns None if not in database
        article = DBArticle.query.filter_by(url=args['url']).first()
        if article is None:
            return "Use POST to add a new article", 403
        update_article_fields(article, **args)
        db.session.commit()
        return "Article successfully updated", 200

    # todo: Probably a bad idea to make this publicly available.
    # if request.method == 'DELETE':
    #     result = DBArticle.query.filter_by(url=args['url']).delete()
    #     db.session.commit()
    #     if result:
    #         return "Successfully deleted", 200
    #     return "Nothing to delete with specified url.", 204

    logging.debug(f"Invalid request: {args}")
    return "Invalid request. Use GET, POST, PUT with good parameters.", 400


@app.route("/analyze/<model>", methods=["GET", "POST"])
def analyze(model):
    if request.method == "POST":
        if model == 'all':
            args = request.args.to_dict()

            if check_password(request.headers) is False:
                return "Unauthorized", 401

            title = args['title']
            va_scores = va.evaluate(title)
            tb_scores = tb.evaluate(title)
            lstm_scores = lstm.evaluate(title)

            # todo: consider using dict unpacking **dict
            # create article object
            article = DBArticle(
                url=args['url'],
                datetime=isoparse(args['datetime']),
                title=args['title'],
                news_co=args['news_co'],
                text=args['text'],
                vader_p_pos=va_scores['p_pos'],
                vader_p_neg=va_scores['p_neg'],
                vader_p_neu=va_scores['p_neu'],
                vader_compound=va_scores['compound'],
                textblob_p_pos=tb_scores['p_pos'],
                textblob_p_neg=tb_scores['p_neg'],
                lstm_p_neu=lstm_scores['p_neu'],
                lstm_p_pos=lstm_scores['p_pos'],
                lstm_p_neg=lstm_scores['p_neg'])

            # Log to db, will fail if there is already an article with the same url.
            try:
                db.session.add(article)
            except IntegrityError as e:
                logging.info(f"Could not add to database error: {e}")
            db.session.commit()
            return articleSchema.dump(article), 200


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


@app.route('/candidate/<name>', methods=['GET'])
def candidate(name):
    # todo: might need another http code
    all_results = {}
    args = request.args.to_dict()
    for news, key in [('CNN', 'cnn'), ('Times', 'the new york times'), ('Fox', 'fox news')]:
        query_results = query_database(candidate=name,
                                       news=news,
                                       opinion=args.get('opinion'))
        all_results[key] = articlesSchema.dump(query_results, many=True)
    if all_results:
        return all_results, 200
    return "No results found", 400


@app.route('/everything/<candidate>')
def everything(candidate):
    if check_password(request.headers) is False:
        return "Unauthorized", 401
    else:
        query = DBArticle.query

        return articlesSchema.jsonify(query.filter(DBArticle.title.ilike(f"%{candidate}%")).all(), many=True)


@app.route('/news/<name>', methods=['GET'])
def news_co(name):
    """
    Get resutls
    :param name:
    :type name:
    :return:
    :rtype:
    """
    all_results = {}
    for news, key in [('CNN', 'cnn'), ('Times', 'the new york times'), ('Fox', 'fox news')]:
        query_results = query_database(candidate=None, news=news, opinion=None)
        all_results[key] = articlesSchema.dump(query_results, many=True)

    if all_results:
        return all_results, 200
    return "No results found", 400


@app.errorhandler(404)
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

    # .with_entities(*COLUMNS_TO_QUERY).limit(100). \
    #         filter(DBArticle.datetime > dt.now(timezone.utc) - timedelta(days=90)).all()
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


@app.route('/update', methods=['PATCH'])
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


@app.route('/join')
def join():
    results = DBArticle.query. \
        limit(10).all()
    return articlesSchema.jsonify(results)


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


@app.route('/new_avg')
def avg():
    with profiled():
        args = request.args.to_dict()

        news_co = args.get('news_co', None)
        candidate = args.get('candidate', None)

        if news_co is None:
            return "Please specify a news company", 400
        if candidate is None:
            return "Please specify a candidate", 400

        today = dt.now(tz=timezone.utc)
        past_limit = today - timedelta(days=90)
        # Filter by date range, news group, and candidate
        results = DBArticle.query. \
            filter(DBArticle.datetime.between(past_limit, today)). \
            filter(DBArticle.news_co.ilike(f"%{news_co}%")). \
            filter(DBArticle.candidate.ilike(f"%{candidate}%")).all()

        return articlesSchema.jsonify(results, many=True)


@app.route('/avg_test')
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


@app.route('/averages')
def lookup():

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


