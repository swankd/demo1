
from flask import request

from .app import app
from .db import DB

db = DB()


def request_args(name, func, default):
    try:
        return func(request.args.get(name, default))
    except (ValueError, TypeError):
        return None


@app.route('/')
def root():
    return '<br>\n'.join([f'{db.nnouns} nouns',
                          f'{db.nverbs} verbs',
                          f'{db.nedges} edges'])


@app.route('/noun/')
def nouns():
    nitems = request_args('nitems', int, 20)
    return '<br>\n'.join([f'{key} : {value}' for key, value in db.nouns.items()[:nitems]])


@app.route('/verb/')
def verbs():
    nitems = request_args('nitems', int, 20)
    return '<br>\n'.join([f'{key} : {value}' for key, value in db.verbs.items()[:nitems]])
