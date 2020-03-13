from flask_app import db

class DBScore(db.Model):
    __tablename__ = 'scores'
    url = db.Column(db.Text,  primary_key=True)
    # url = db.Column(db.Text, db.ForeignKey("articles.url"),  primary_key=True)
    # article = db.relationship("DBArticle", backref="scores")

    vader = db.Column(db.Float)
    textblob = db.Column(db.Float)
    lstm = db.Column(db.Float)
    bert = db.Column(db.Float)

    vader_14day_avg = db.Column(db.Float)
    textblob_14day_avg = db.Column(db.Float)
    lstm_14day_avg = db.Column(db.Float)
    bert_14day_avg = db.Column(db.Float)

    # Can ignore these columns
    vader_p_pos = db.Column(db.Float)
    vader_p_neg = db.Column(db.Float)
    vader_p_neu = db.Column(db.Float)
    vader_compound = db.Column(db.Float)
    textblob_p_pos = db.Column(db.Float)
    textblob_p_neg = db.Column(db.Float)
    lstm_p_neu = db.Column(db.Float)
    lstm_p_pos = db.Column(db.Float)
    lstm_p_neg = db.Column(db.Float)
    bert_p_neu = db.Column(db.Float)
    bert_p_pos = db.Column(db.Float)
    bert_p_neg = db.Column(db.Float)

class DBArticle(db.Model):
    __tablename__ = 'articles'
    url = db.Column(db.Text, db.ForeignKey("scores.url"), primary_key=True)
    scores = db.relationship("DBScore", backref="scores")

    datetime = db.Column(db.DateTime)
    title = db.Column(db.Text)
    news_co = db.Column(db.String(50))
    text = db.Column(db.Text)
    candidate = db.Column(db.String(15))

descriptions = DBArticle().query.column_descriptions[0]['entity'].__dict__.keys()

# get rid of dunder variables (__tablename__, __module__, etc.)
COLUMN_NAMES = [column_name for column_name in descriptions if column_name[0] != '_']


# class DBScore(db.Model):
#     __tablename__ = 'scores'
#     url = db.Column(db.Text, db.ForeignKey("articles.url"),  primary_key=True)
#     article = db.relationship("DBArticle", backref="scores")
#
#     vader = db.Column(db.Float)
#     textblob = db.Column(db.Float)
#     lstm = db.Column(db.Float)
#     bert = db.Column(db.Float)
#
#     # Can ignore these columns
#     vader_p_pos = db.Column(db.Float)
#     vader_p_neg = db.Column(db.Float)
#     vader_p_neu = db.Column(db.Float)
#     vader_compound = db.Column(db.Float)
#     textblob_p_pos = db.Column(db.Float)
#     textblob_p_neg = db.Column(db.Float)
#     lstm_p_neu = db.Column(db.Float)
#     lstm_p_pos = db.Column(db.Float)
#     lstm_p_neg = db.Column(db.Float)
#     bert_p_neu = db.Column(db.Float)
#     bert_p_pos = db.Column(db.Float)
#     bert_p_neg = db.Column(db.Float)


class Weekly(db.Model):

    index = db.Column(db.BigInteger, primary_key=True)
    candidate = db.Column(db.Text)
    news_co = db.Column(db.Text)
    datetime = db.Column(db.DateTime)
    bert = db.Column(db.Float)
    lstm = db.Column(db.Float)
    vader = db.Column(db.Float)
    textblob = db.Column(db.Float)


class Tabulator(db.Model):

    title = db.Column(db.Text, primary_key=True)
    url = db.Column(db.Text)
    candidate = db.Column(db.Text)
    news_co = db.Column(db.Text)
    datetime = db.Column(db.DateTime)
    bert = db.Column(db.Float)
    lstm = db.Column(db.Float)
    vader = db.Column(db.Float)
    textblob = db.Column(db.Float)
