from flask_app.db_models import DBArticle, DBScore, Weekly, Tabulator
from flask_app import ma
from marshmallow import fields


class ScoreSchema(ma.SQLAlchemySchema):
    class Meta:
        model = DBScore

    bert = fields.Float()
    lstm = fields.Float()
    vader = fields.Float()
    textblob = fields.Float()


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


class TabulatorSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Tabulator

    title = ma.auto_field()
    url = ma.auto_field()
    candidate = ma.auto_field()
    news_co = ma.auto_field()
    datetime = ma.auto_field()

    bert = ma.auto_field()
    lstm = ma.auto_field()
    vader = ma.auto_field()
    textblob = ma.auto_field()