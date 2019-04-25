import psycopg2

from flask import current_app, g
from flask.cli import with_appcontext

def get_db():
    if 'db' not in g:
        g.db = psycopg2.connect(**current_app.config['DATABASE'])

    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()
