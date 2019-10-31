

def cmp(a, b):
    return (a > b) - (a < b)


class SearchPage():
    '''
    Collection of uniformly-sized byte strings stored as a single byte string to support
    binary search.
    '''
    def __init__(self, data, key_width, value_width):
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
        k0 = 0
        k1 = nentries - 1
        while True:
            assert k1 >= k0
            kmid = (k0 + k1) // 2
            result = compare_entry(kmid)
            if isinstance(result, bytes):
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

        return result

    def get(self, key, default=None):
        entry = self.get_entry(key)
        if isinstance(entry, bytes):
            return entry[self.key_width:]
        else:
            return default
