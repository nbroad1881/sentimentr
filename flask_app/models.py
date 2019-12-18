from datetime import datetime

from flask_app import db


class Article(db.Model):
    __tablename__ = 'articles'
    url = db.Column(db.Text, primary_key=True)
    datetime = db.Column(db.DateTime)
    title = db.Column(db.Text)
    news_co = db.Column(db.String(50))
    text = db.Column(db.Text)
    vader_positive = db.Column(db.Float)
    vader_negative = db.Column(db.Float)
    vader_neutral = db.Column(db.Float)
    vader_compound = db.Column(db.Float)
    textblob_polarity = db.Column(db.Float)
    textblob_subjectivity = db.Column(db.Float)
    textblob_classification = db.Column(db.String(10))
    textblob_p_pos = db.Column(db.Float)
    textblob_p_neg = db.Column(db.Float)
    lstm_category = db.Column(db.String(15))
    lstm_p_neu = db.Column(db.Float)
    lstm_p_pos = db.Column(db.Float)
    lstm_p_neg = db.Column(db.Float)

    def to_dict(self):
        return {
            'url': self.url,
            'datetime': self.datetime.isoformat(),
            'title': self.title,
            'news_co': self.news_co,
            'text': self.text,
            'vader_positive': self.vader_positive,
            'vader_negative': self.vader_negative,
            'vader_neutral': self.vader_neutral,
            'vader_compound': self.vader_compound,
            'textblob_polarity': self.textblob_polarity,
            'textblob_subjectivity': self.textblob_subjectivity,
            'textblob_classification': self.textblob_classification,
            'textblob_p_pos': self.textblob_p_pos,
            'textblob_p_neg': self.textblob_p_neg,
            'lstm_category': self.lstm_category,
            'lstm_p_neu': self.lstm_p_neu,
            'lstm_p_pos': self.lstm_p_pos,
            'lstm_p_neg': self.lstm_p_neg,
        }


class Score(db.Model):
    __tablename__ = 'scores'
    url = db.Column(db.Text, primary_key=True)
    vader_positive = db.Column(db.Float)
    vader_negative = db.Column(db.Float)
    vader_neutral = db.Column(db.Float)
    vader_compound = db.Column(db.Float)
    textblob_polarity = db.Column(db.Float)
    textblob_subjectivity = db.Column(db.Float)
    textblob_classification = db.Column(db.String(10))
    textblob_p_pos = db.Column(db.Float)
    textblob_p_neg = db.Column(db.Float)
    lstm = db.Column(db.Float)

    def __repr__(self):
        return f'{self.title} from {self.id}'

    def __dict__(self):
        return {
            'url': self.url,
            'vader_positive': self.vader_positive,
            'vader_negative': self.vader_negative,
            'vader_neutral': self.vader_neutral,
            'vader_compound': self.vader_compound,
            'textblob_polarity': self.textblob_polarity,
            'textblob_subjectivity': self.textblob_subjectivity,
            'textblob_classification': self.textblob_classification,
            'textblob_p_pos': self.textblob_p_pos,
            'textblob_p_neg': self.textblob_p_neg,
            'lstm': self.lstm
        }
