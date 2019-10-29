
import json

from pygit2 import GitError, Repository, init_repository, GIT_OBJ_BLOB


def cmp(a, b):
    return (a > b) - (a < b)


class BadPage(Exception):
    pass


class BadPageSize(BadPage):
    pass


class BadWidth(ValueError):
    pass


def find_in_page(page, oid, width):
    '''
    Binary search for ``oid`` in ``page``.  ``width`` may be 18 or 38.  len(``oid``) must
    be 18.  len(``page``) must be multiple of ``width``.

    Return value is None if ``oid`` is not found in ``page``.

    If ``oid`` is found, return value is the 20 bytes following the occurrence of ``oid``
    in ``page`` if ``width`` is 38, or True if ``width`` is 18.
    '''
    def compare_entry(k):
        pos = k * width
        entry = page[pos:pos + width]
        result = cmp(oid, entry[:18])
        if result == 0 and width == 38:
            return entry[18:]
        else:
            return result

    if width not in (18, 38):
        raise BadWidth(width)

    if len(page) % width:
        raise BadPageSize((len(page), width))

    nentries = len(page) // width
    k0 = 0
    k1 = nentries - 1
    while True:
        assert k1 >= k0
        kmid = (k0 + k1) // 2
        result = compare_entry(kmid)
        if result == 0 or isinstance(result, bytes):
            break

        if k0 == k1:
            break
        if k1 - k0 == 1:
            result = compare_entry(k1)
            break

        if result < 0:
            k1 = kmid - 1
        else:
            k0 = kmid + 1

    if result == 0:
        return True
    elif isinstance(result, bytes):
        return result
    else:
        return None


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
