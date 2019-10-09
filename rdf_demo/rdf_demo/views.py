
import json

from flask import jsonify, request, url_for

from .app import app
from .db import BdbRDFGraph

graph = BdbRDFGraph()


def request_args(name, func, default):
    try:
        return func(request.args.get(name, default))
    except (ValueError, TypeError):
        return None


def noun_reference(id_):
    return {'value': graph.nouns.element_str(id_), 'href': url_for('noun', id_=id_)}


def verb_reference(id_):
    return graph.verbs.element_str(id_)


def in_edge(pid, sid):
    return {'predicate': verb_reference(pid), 'subject': noun_reference(sid)}


def out_edge(pid, oid):
    return {'predicate': verb_reference(pid), 'object': noun_reference(oid)}


def _edges(db_, id_):
    return set([tuple(edge) for edge in json.loads(db_.get(id_.encode('ascii')) or '[]')])


@app.route('/')
def root():
    return '<br>\n'.join([f'{graph.nnouns} nouns',
                          f'{graph.nverbs} verbs',
                          f'{graph.n_in_edges} inbound edges',
                          f'{graph.n_out_edges} outbound edges'])


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


@app.route('/noun/<id_>')
def noun(id_):
    return jsonify({'noun': noun_reference(id_),
                    'in_edges': [in_edge(pid, sid)
                                 for pid, sid in _edges(graph.in_edges, id_)],
                    'out_edges': [out_edge(pid, oid)
                                  for pid, oid in _edges(graph.out_edges, id_)]})
