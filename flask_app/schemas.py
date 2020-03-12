from flask_app.db_models import DBArticle, DBScore, Weekly
from flask_app import ma
from marshmallow import fields


class ScoreSchema(ma.SQLAlchemySchema):
    class Meta:
        model = DBScore

    bert = fields.Float()
    lstm = fields.Float()
    vader = fields.Float()
    textblob = fields.Float()

    bert_14day_avg = fields.Float()
    lstm_14day_avg = fields.Float()
    vader_14day_avg = fields.Float()
    textblob_14day_avg = fields.Float()


class ArticleSchema(ma.SQLAlchemySchema):
    class Meta:
        model = DBArticle

    url = ma.auto_field()
    title = ma.auto_field()
    datetime = ma.auto_field()
    # candidate = ma.auto_field()
    # news_co = ma.auto_field()

    bert_14day_avg = ma.auto_field()
    lstm_14day_avg = ma.auto_field()
    vader_14day_avg = ma.auto_field()
    textblob_14day_avg = ma.auto_field()

    # scores = fields.Nested(ScoreSchema)

class WeeklySchema(ma.SQLAlchemySchema):
    class Meta:
        model = Weekly

    index = ma.auto_field()
    candidate = ma.auto_field()
    news_co = ma.auto_field()
    datetime = ma.auto_field()
    bert = ma.auto_field()
    lstm = ma.auto_field()
    vader = ma.auto_field()
    textblob = ma.auto_field()
