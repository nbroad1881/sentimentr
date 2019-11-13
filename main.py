from flask_app import app, db
from flask_app.models import Article


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Article': Article}


if __name__ == '__main__':
    app.run(debug=True)
