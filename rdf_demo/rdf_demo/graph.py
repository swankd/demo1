
from hdt import HDTDocument, IdentifierPosition as IP


class HDTGraph(HDTDocument):
    Subject = IP.Subject
    Predicate = IP.Predicate
    Object = IP.Object

    def __init__(self, *args, **kwargs):
        HDTDocument.__init__(self, *args, **kwargs)

    @property
    def nb_s_p_o(self):
        return self.nb_subjects, self.nb_predicates, self.nb_objects

    def out_edges(self, sid):
        triples, _ = self.search_triples_ids(sid, 0, 0)
        return ((pid, oid) for _, pid, oid in triples)

    def in_edges(self, oid):
        triples, _ = self.search_triples_ids(0, 0, oid)
        return ((sid, pid) for sid, pid, _ in triples)
