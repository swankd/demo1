
from os.path import join

from bdb_tool import open_db, BdbUniqueId


class BdbRDFGraph():
    def __init__(self, dir_, log=None):
        self.log = log or print
        self.nouns = BdbUniqueId(dir_, 'noun', log=self.log)
        self.verbs = BdbUniqueId(dir_, 'verb', log=self.log)

        # inbound edges: (predicate, subject) pairs keyed by object.
        self.in_edges = open_db(join(dir_, 'in_edges.db3'))

        # outbound edges: (predicate, object) pairs keyed by subject.
        self.out_edges = open_db(join(dir_, 'out_edges.db3'))

        self.log(f'number of in edges is {len(self.in_edges)}')
        self.log(f'number of out edges is {len(self.out_edges)}')
