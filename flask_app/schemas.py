from flask_app.db_models import DBArticle
from flask_app import ma


class ArticleSchema(ma.ModelSchema):
    class Meta:
        model = DBArticle


