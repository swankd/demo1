
import random
import tempfile
import unittest

from git_db import GitDict, SearchPage


class TestGitDict(unittest.TestCase):
    def test1(self):
        with tempfile.TemporaryDirectory() as dir_:
            gd = GitDict(dir_, 'stuff', do_create=True)
            self.assertNotIn('xyz', gd)
            self.assertEqual(len(gd), 0)
            gd.report()

            gd.add('xyz')
            self.assertIn('xyz', gd)
            self.assertEqual(len(gd), 1)

            gd.add('abc')
            self.assertIn('xyz', gd)
            self.assertIn('abc', gd)
            self.assertEqual(len(gd), 2)

            gd.add('def')
            self.assertIn('xyz', gd)
            self.assertIn('abc', gd)
            self.assertIn('def', gd)
            self.assertEqual(len(gd), 3)


class TestSearchPage(unittest.TestCase):
    def make_page_entry(self, width):
        return bytes([random.randint(97, 122) for x in range(width)])

    def make_page(self, width, nentries, include_entry=None):
        if include_entry:
            assert len(include_entry) == width, (include_entry, width)
        entries = [self.make_page_entry(width) for _ in range(nentries)]
        if include_entry:
            entries += [include_entry]
        for entry in sorted(entries):
            print(entry)
        return SearchPage(b''.join(sorted(entries)),
                          *((18, 0) if width == 18 else (18, 20)))

    def test18_missing(self):
        for _ in range(10):
            entry = self.make_page_entry(18)
            page = self.make_page(18, random.randint(1, 20))
            self.assertIsNone(page.get(entry))

    def test18_present(self):
        for _ in range(100):
            entry = self.make_page_entry(18)
            page = self.make_page(18, random.randint(1, 20), entry)
            self.assertEqual(page.get(entry), b'')

    def test38_missing(self):
        for _ in range(10):
            entry = self.make_page_entry(38)
            page = self.make_page(38, random.randint(1, 20))
            self.assertIsNone(page.get(entry[:18]))

    def test38_present(self):
        for _ in range(100):
            entry = self.make_page_entry(38)
            page = self.make_page(38, random.randint(1, 20), entry)
            self.assertEqual(page.get(entry[:18]), entry[18:])

    def test_items(self):
        for _ in range(100):
            page = self.make_page(38, random.randint(1, 20))
            self.assertEqual(page.data, b''.join(page.items()))

    def test_keys_and_values(self):
        for _ in range(100):
            page = self.make_page(38, random.randint(1, 20))
            items = [b''.join([key, value])
                     for key, value in zip(page.keys(), page.values())]
            self.assertEqual(page.data, b''.join(items))

    def test_contains(self):
        for _ in range(100):
            entry = self.make_page_entry(38)
            page = self.make_page(38, random.randint(1, 20), entry)
            self.assertIn(entry[:18], page)

    def test_getitem1(self):
        page = SearchPage(b'abc', 1, 0)
        with self.assertRaises(KeyError):
            x = page[b'd']
        self.assertEqual(page[b'a'], b'')

    def test_getitem2(self):
        page = SearchPage(b'abcd', 1, 1)
        with self.assertRaises(KeyError):
            x = page[b'd']
        self.assertEqual(page[b'a'], b'b')

    def test_setitem1(self):
        page = SearchPage(b'abcd', 1, 1)
        page[b'a'] = b'x'
        self.assertEqual(page.data, b'axcd')

    def test_setitem2(self):
        page = SearchPage(b'abcd', 1, 1)
        page[b'e'] = b'x'
        self.assertEqual(page.data, b'abcdex')

    def test_setitem20(self):
        page = SearchPage(b'abcd', 1, 1)
        page[b'b'] = b'x'
        self.assertEqual(page.data, b'abbxcd')

    def test_setitem21(self):
        page = SearchPage(b'abcdef', 1, 1)
        page[b'd'] = b'x'
        self.assertEqual(page.data, b'abcddxef')

    def test_setitem3(self):
        page = SearchPage(b'abcd', 1, 1)
        page[b'X'] = b'x'
        self.assertEqual(page.data, b'Xxabcd')

    def test_setitem4(self):
        page = SearchPage(b'', 1, 1)
        page[b'X'] = b'x'
        self.assertEqual(page.data, b'Xx')

    def test_setitem5(self):
        page = SearchPage(b'abcd', 1, 0)
        page[b'a'] = b''
        self.assertEqual(page.data, b'abcd')

    def test_setitem6(self):
        page = SearchPage(b'abcd', 1, 0)
        page[b'e'] = b''
        self.assertEqual(page.data, b'abcde')

    def test_setitem7(self):
        page = SearchPage(b'abcd', 1, 0)
        page[b'X'] = b''
        self.assertEqual(page.data, b'Xabcd')

    def test_setitem8(self):
        page = SearchPage(b'', 1, 0)
        page[b'X'] = b''
        self.assertEqual(page.data, b'X')

    def test_setitem9(self):
        for _ in range(100):
            entry = self.make_page_entry(38)
            page = self.make_page(38, random.randint(1, 20))
            page[entry[:18]] = entry[18:]
            self.assertIn(entry[:18], page)
            items = page.items()
            self.assertEqual(items, sorted(items))
