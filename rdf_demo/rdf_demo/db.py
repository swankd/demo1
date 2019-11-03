
from os.path import join

from bdb_tool import open_db, BdbUniqueId

from .config import get_config


class BdbRDFGraph():
    def __init__(self, config=None, log=None):
        self.config = config or get_config()
        self.log = log or print
        dir_ = self.config['db_dir']
        self.nouns = BdbUniqueId(dir_, 'noun', log=self.log)
        self.verbs = BdbUniqueId(dir_, 'verb', log=self.log)

        # inbound edges: (predicate, subject) pairs keyed by object.
        self.in_edges = open_db(join(dir_, 'in_edges.db3'))

        # outbound edges: (predicate, object) pairs keyed by subject.
        self.out_edges = open_db(join(dir_, 'out_edges.db3'))

        self.log(f'number of in edges is {len(self.in_edges)}')
        self.log(f'number of out edges is {len(self.out_edges)}')
