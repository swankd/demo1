
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
            self.assertIsNone(page.find(entry))

    def test18_present(self):
        for _ in range(100):
            entry = self.make_page_entry(18)
            page = self.make_page(18, random.randint(1, 20), entry)
            self.assertEqual(page.find(entry), b'')

    def test38_missing(self):
        for _ in range(10):
            entry = self.make_page_entry(38)
            page = self.make_page(38, random.randint(1, 20))
            self.assertIsNone(page.find(entry[:18]))

    def test38_present(self):
        for _ in range(100):
            entry = self.make_page_entry(38)
            page = self.make_page(38, random.randint(1, 20), entry)
            self.assertEqual(page.find(entry[:18]), entry[18:])
