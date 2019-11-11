
from hdt import HDTDocument, IdentifierPosition as IP


class HDTGraph():
    Subject = IP.Subject
    Predicate = IP.Predicate
    Object = IP.Object

    def __init__(self, path):
        self.graph = HDTDocument(path)

    @property
    def total_triples(self):
        return self.graph.total_triples

    @property
    def nb_subjects(self):
        return self.graph.nb_subjects

    @property
    def nb_predicates(self):
        return self.graph.nb_predicates

    @property
    def nb_objects(self):
        return self.graph.nb_objects

    @property
    def nb_s_p_o(self):
        return self.graph.nb_subjects, self.graph.nb_predicates, self.graph.nb_objects

    def term(self, id_, position):
        return self.graph.convert_id(id_, position)

    def out_edges(self, sid):
        triples, _ = self.graph.search_triples_ids(sid, 0, 0)
        return ((pid, oid) for _, pid, oid in triples)

    def in_edges(self, oid):
        triples, _ = self.graph.search_triples_ids(0, 0, oid)
        return ((sid, pid) for sid, pid, _ in triples)
