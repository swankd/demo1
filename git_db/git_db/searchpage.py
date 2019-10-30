
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
