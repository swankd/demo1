
from bsddb3 import db as bdb
from os.path import isfile, join


def dev_null(msg):
    pass


def open_db(path):
    db = bdb.DB()
    if isfile(path):
        open_args = tuple()
    else:
        open_args = (None, bdb.DB_HASH, bdb.DB_CREATE)
    db.open(path, *open_args)
    return db


def db_nkeys(db, label, log=dev_null):
    log(f'reading {label} file (this may take a while) ...')
    return db.stat()['nkeys']


class BdbUniqueId(object):
    '''
    A pair of berkeley dbs: a map of strings to unique ids, and its inverse.
    '''
    def __init__(self, dir_, name, suffix="s.db3", log=dev_null):
        self.log = log
        self.elements = open_db(join(dir_, f'{name}{suffix}'))
        self.ids = open_db(join(dir_, f'{name}id{suffix}'))
        self.n_elements = db_nkeys(self.elements, name, log)
        n_ids = db_nkeys(self.ids, name + 'id', log)
        assert self.n_elements == n_ids, (self.n_elements, n_ids, dir_, name, suffix)
        self.log(f'number of {name}s is {n_ids}')

    def element_id(self, str_):
        id_ = self.elements.get(str_)
        if not id_:
            self.n_elements += 1
            id_ = str(self.n_elements).encode('ascii')
            self.elements.put(str_, id_)
            self.ids.put(id_, str_)
        return id_

    def element(self, id_):
        return self.ids.get(id_)

    def compact(self):
        self.elements.compact()
        self.ids.compact()
