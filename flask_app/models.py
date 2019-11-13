from datetime import datetime

from flask_app import db


class Article(db.Model):
    id = db.Column(db.String(50), primary_key=True) #id is just url
    title = db.Column(db.String(120), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    publisher = db.Column(db.String(20), nullable=False)
    content = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'{self.title} from {self.id}'
