
from os.path import join

from bdb_tool import open_db, db_nkeys, BdbUniqueId

from .config import get_config


class DB():
    def __init__(self, config=None, log=None):
        self.config = config or get_config()
        self.log = log or print
        dir_ = self.config['db_dir']
        self.nouns = BdbUniqueId(dir_, 'noun', log=self.log)
        self.verbs = BdbUniqueId(dir_, 'verb', log=self.log)
        self.edges = open_db(join(dir_, 'edges.db3'))
        self.log(f'number of edges is {self.nedges}')

    @property
    def nnouns(self):
        return db_nkeys(self.nouns.elements, 'noun')

    @property
    def nverbs(self):
        return db_nkeys(self.verbs.elements, 'verb')

    @property
    def nedges(self):
        return db_nkeys(self.edges, 'edge')
