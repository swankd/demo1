
from flask import request

from .app import app
from .db import BdbRDFGraph

graph = BdbRDFGraph()


def request_args(name, func, default):
    try:
        return func(request.args.get(name, default))
    except (ValueError, TypeError):
        return None


@app.route('/')
def root():
    return '<br>\n'.join([f'{graph.nnouns} nouns',
                          f'{graph.nverbs} verbs',
                          f'{graph.nedges} edges'])


@app.route('/noun/')
def nouns():
    nitems = request_args('nitems', int, 20)
    return '<br>\n'.join([f'{key} : {value}'
                          for key, value in graph.nouns.items()[:nitems]])


@app.route('/verb/')
def verbs():
    nitems = request_args('nitems', int, 20)
    return '<br>\n'.join([f'{key} : {value}'
                          for key, value in graph.verbs.items()[:nitems]])
