
from pygit2 import hash as pyghash


def cmp(a, b):
    return (a > b) - (a < b)


class SearchPage():
    '''
    Collection of uniformly-sized byte strings stored as a single byte string to support
    binary search.
    '''
    def __init__(self, data, key_width, value_width):
        if not isinstance(data, bytes):
            raise ValueError(data)
        self.data = data
        self.key_width = key_width
        self.value_width = value_width
        self.width = key_width + value_width
        if key_width < 0:
            raise ValueError(key_width)
        if value_width < 0:
            raise ValueError(value_width)
        if len(data) % self.width:
            raise ValueError((data, key_width, value_width))

    def __len__(self):
        return len(self.data) // self.width

    def get_entry(self, key):

        def compare_entry(k):
            pos = k * self.width
            kth_entry = self.data[pos:pos + self.width]
            result = cmp(key, kth_entry[:self.key_width])
            if result == 0:
                return kth_entry
            else:
                return result

        if len(key) != self.key_width:
            raise ValueError(key)

        nentries = len(self)
        if not nentries:
            return 1, 0

        k0 = 0
        k1 = nentries - 1
        while True:
            assert k1 >= k0
            kmid = (k0 + k1) // 2
            result = compare_entry(kmid)
            if isinstance(result, bytes):
                k1 = kmid
                break

            if k0 == k1:
                break
            if k1 - k0 == 1:
                if result > 0:
                    result = compare_entry(k1)
                else:
                    k1 = k0
                break

            if result < 0:
                k1 = kmid - 1
            else:
                k0 = kmid + 1

        return result, k1

    def get(self, key, default=None):
        entry, k = self.get_entry(key)
        if isinstance(entry, bytes):
            return entry[self.key_width:]
        else:
            return default

    def _elements(self, a, b):
        elements = []
        for k in range(len(self)):
            pos = k * self.width
            elements.append(self.data[pos + a:pos + b])
        return elements

    def items(self):
        return self._elements(0, self.width)

    def keys(self):
        return self._elements(0, self.key_width)

    def values(self):
        return self._elements(self.key_width, self.width)

    def __contains__(self, key):
        return self.get(key) is not None

    def __getitem__(self, key):
        value = self.get(key)
        if value is None:
            raise KeyError(key)
        return value

    def __setitem__(self, key, value):
        if len(value) != self.value_width:
            raise ValueError(value)

        entry, k = self.get_entry(key)

        if isinstance(entry, bytes):
            assert entry[:self.key_width] == key
            offset = self.width
        else:
            offset = 0
            k = max(0, k)
            if entry == 1:
                k += 1

        entry_pos = k * self.width
        new_entry = b'%s%s' % (key, value)
        self.data = b'%s%s%s' % (self.data[:entry_pos], new_entry,
                                 self.data[entry_pos + offset:])


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
