
import json

from pygit2 import GitError, Oid, Repository, init_repository, GIT_OBJ_BLOB

from .searchpage import SearchPage, PageTable, pyghash


class ItemPage(SearchPage):
    def __init__(self, data=b''):
        SearchPage.__init__(self, data, 20, 20)


class GitDict():
    '''
    A python dict, stored in git so it can be larger than memory and yet accessed for
    reading and writing efficiently.  Keys and values are git objects.  The collection of
    key-value pairs is stored in a one level hierarchy of pages (git objects) that are
    indexed by a page table (also a git object).
    '''
    def __init__(self, dir_, name, log=None, do_create=False, refs_ns='tags'):
        self.dir_ = dir_
        self.name = name
        self.name_size = name + '.size'
        self.name_items = name + '.items'
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
        self._set_reference(self.name_size, self.repo.write(GIT_OBJ_BLOB, '0'))
        self.items_table = PageTable()

    @property
    def items_table(self):
        return PageTable(self.repo[self._lookup_reference(self.name_items).target].data)

    @items_table.setter
    def items_table(self, table):
        self._set_reference(self.name_items, self.repo.write(GIT_OBJ_BLOB, table.data))

    def __len__(self):
        return int(self.repo[self._lookup_reference(self.name_size).target])

    def _inc_size(self):
        new_size = self.repo.write(GIT_OBJ_BLOB, str(len(self) + 1))
        self._set_reference(self.name_size, new_size)

    def __contains__(self, key):
        try:
            return self[key] and True
        except KeyError:
            return False

    def _get_page(self, key_oid, table=None):
        table = table or self.items_table
        entry_no = key_oid[0] * 256 + key_oid[1]
        try:
            return ItemPage(self.repo[Oid(table[entry_no])].data)
        except TypeError:
            return ItemPage()

    def __getitem__(self, key):
        key_oid = pyghash(key).raw
        page = self._get_page(key_oid)
        value_oid = page[key_oid]
        return self.repo[Oid(value_oid)].data

    def __setitem__(self, key, value):
        key_oid = self.repo.write(GIT_OBJ_BLOB, key).raw
        value_oid = self.repo.write(GIT_OBJ_BLOB, value).raw

        table = self.items_table
        page = self._get_page(key_oid, table)
        if key_oid in page:
            return

        page[key_oid] = value_oid
        page_oid = self.repo.write(GIT_OBJ_BLOB, page.data).raw
        entry_no = key_oid[0] * 256 + key_oid[1]
        table[entry_no] = page_oid
        self.items_table = table
        self._inc_size()

    def report(self):
        self.log(f'{repr(self)}: contains {len(self)} elements.')

    def keys(self):
        table = self.items_table
        keys = []
        for k in range(table.TABLE_SIZE):
            if table[k] != table.EMPTY_PAGE_ID:
                page = ItemPage(self.repo[Oid(table[k])].data)
                for key in page.keys():
                    keys.append(self.repo[Oid(key)].data)
        return keys
