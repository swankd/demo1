
import json

from pygit2 import (GitError, Repository, init_repository, hash as pyghash,
                    GIT_OBJ_BLOB)


class PageTable():
    EMPTY_PAGE_ID = pyghash(b'').raw
    TABLE_SIZE = 65536

    def __init__(self, data=None):
        self.data = data or self.EMPTY_PAGE_ID * self.TABLE_SIZE

    def __getitem__(self, k):
        pos = (k % self.TABLE_SIZE) * 20
        return self.data[pos:pos + 20]

    def __setitem__(self, k, value):
        if len(value) != 20 or not isinstance(value, bytes):
            raise ValueError(value)
        pos = (k % self.TABLE_SIZE) * 20
        self.data = b'%s%s%s' % (self.data[:pos], value, self.data[pos + 20:])

    @property
    def entries(self):
        entries = []
        for k in range(self.TABLE_SIZE):
            pos = k * 20
            entries.append(self.data[pos:pos + 20])
        return entries

    @entries.setter
    def entries(self, entries):
        self.data = b''.join(entries)

    def setitems(self, items):
        entries = self.entries
        for position, entry in items:
            entries[position] = entry
        self.entries = entries


class GitDict():
    def __init__(self, dir_, name, log=None, do_create=False, refs_ns='tags'):
        self.dir_ = dir_
        self.name = name
        self.nname = 'n' + name
        self.log = log or print
        self.refs_ns = refs_ns
        try:
            self.repo = Repository(dir_)
        except GitError as e:
            if do_create:
                self.repo = init_repository(dir_, bare=True)
            else:
                raise e
        self.none = self.repo.write(GIT_OBJ_BLOB, '')
        self._init()

    def __repr__(self):
        return f'GitDict("{self.dir_}", "{self.name}")'

    def _lookup_reference(self, name):
        return self.repo.lookup_reference(f'refs/{self.refs_ns}/{name}')

    def _set_reference(self, name, target):
        try:
            self._lookup_reference(name).set_target(target)
        except KeyError:
            self.repo.references.create(f'refs/{self.refs_ns}/{name}', target)

    def _init(self):
        self._set_reference(self.nname, self.repo.write(GIT_OBJ_BLOB, '0'))
        self._set_reference(self.name, self.none)

    def __len__(self):
        return int(self.repo[self._lookup_reference(self.nname).target])

    def __contains__(self, key):
        id_ = self._lookup_reference(self.name).target
        while id_ != self.none:
            element, id_ = json.loads(self.repo[id_].data)  # it's a linked list!
            if element == key:
                return True
        return False

    def add(self, element):
        old_head = self._lookup_reference(self.name).target
        new_head = self.repo.write(GIT_OBJ_BLOB, json.dumps([element, str(old_head)]))
        self._set_reference(self.name, new_head)
        new_size = self.repo.write(GIT_OBJ_BLOB, str(len(self) + 1))
        self._set_reference(self.nname, new_size)

    def report(self):
        self.log(f'{repr(self)}: contains {len(self)} elements.')
