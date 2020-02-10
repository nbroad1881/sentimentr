import os
import logging

from dateutil.parser import isoparse
from flask import request, render_template
from dotenv import load_dotenv
from sqlalchemy.exc import IntegrityError

from flask_app import app, db
from flask_app.db_models import DBArticle, COLUMN_NAMES
from flask_app.schemas import ArticleSchema
from sentinews.models import VaderAnalyzer, LSTMAnalyzer, TextBlobAnalyzer

articleSchema = ArticleSchema()
articlesSchema = ArticleSchema(many=True)
load_dotenv()
logging.basicConfig(level=logging.DEBUG)

DB_TABLE_NAME = os.environ['DB_TABLE_NAME']
DB_URL = os.environ['DB_URL']
DB_PARSE_COLUMNS = os.environ['DB_PARSE_COLUMNS']
DB_SELECT_COLUMNS = os.environ['DB_SELECT_COLUMNS']

va = VaderAnalyzer()
tb = TextBlobAnalyzer()
lstm = LSTMAnalyzer()

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
    DBArticle.lstm_p_neg, ]

DEFAULT_NUM_TO_QUERY = 100


# todo: add validation and verification for requests

# todo: make table object to avoid update error (table.c)
@app.route("/")
def home():
    return render_template("home.html"), 200


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


def query_database(candidate, news, opinion):
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
        query = query.filter(DBArticle.title.ilike(f"%{candidate}%"))
    if opinion:
        query = query.filter(DBArticle.url.contains('opinion'))
    results = query.order_by(DBArticle.datetime.desc()) \
        .with_entities(*COLUMNS_TO_QUERY) \
        .limit(DEFAULT_NUM_TO_QUERY).all()
    if results:
        results = results[::-1]
    return results


def check_password(headers):
    pw = headers.get('password')
    if pw != -1:
        logging.info(pw + '\n' + os.environ['AUTH_PASSWORD'])
        logging.info(pw == os.environ['AUTH_PASSWORD'])
        return pw == os.environ['AUTH_PASSWORD']