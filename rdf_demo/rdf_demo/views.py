
from flask import abort, jsonify, render_template, request, url_for

from .app import app

graph = app.graph
ROUTE_FOR_POSITION = ('subject', 'predicate', 'object_')


def request_args(name, func, default):
    try:
        return func(request.args.get(name, default))
    except (ValueError, TypeError):
        return None


def _reference(id_, position):
    return {'term': graph.convert_id(id_, position),
            'href': url_for(ROUTE_FOR_POSITION[int(position) - 1], id_=id_)}


def _reference_list(position):
    limit = request_args('limit', int, 20)
    offset = request_args('offset', int, 1)  # ids are 1-based
    max_offset = graph.nb_s_p_o[int(position) - 1]
    if offset > max_offset:
        abort(404)

    refs = []
    for id_ in range(min(1000, limit)):
        ref = _reference(id_ + offset, position)
        if ref:
            refs.append(ref)
    return refs


@app.route('/')
def root():
    return render_template('root.html',
                           dataset_description=app.description,
                           ntriples=graph.total_triples,
                           nsubjects=graph.nb_subjects,
                           npredicates=graph.nb_predicates,
                           nobjects=graph.nb_objects)


@app.route('/subject/')
def subjects():
    return jsonify(subjects=_reference_list(graph.Subject),
                   nb_subjects=graph.nb_subjects)


@app.route('/predicate/')
def predicates():
    return jsonify(predicates=_reference_list(graph.Predicate),
                   nb_predicates=graph.nb_predicates)


@app.route('/object/')
def objects():
    return jsonify(objects=_reference_list(graph.Object),
                   nb_objects=graph.nb_objects)


@app.route('/subject/<int:id_>')
def subject(id_):
    def out_edge(pid, oid):
        return {'predicate': _reference(pid, graph.Predicate),
                'object': _reference(oid, graph.Object)}

    if id_ < 1 or id_ > graph.nb_subjects:
        abort(404)
    return jsonify(subject=_reference(id_, graph.Subject),
                   out_edges=[out_edge(*edge) for edge in graph.out_edges(id_)])


@app.route('/predicate/<int:id_>')
def predicate(id_):
    if id_ < 1 or id_ > graph.nb_predicates:
        abort(404)
    return jsonify(predicate=_reference(id_, graph.Predicate))


@app.route('/object/<int:id_>')
def object_(id_):
    def in_edge(sid, pid):
        return {'subject': _reference(sid, graph.Subject),
                'predicate': _reference(pid, graph.Predicate)}

    if id_ < 1 or id_ > graph.nb_objects:
        abort(404)
    return jsonify(object=_reference(id_, graph.Object),
                   in_edges=[in_edge(*edge) for edge in graph.in_edges(id_)])
