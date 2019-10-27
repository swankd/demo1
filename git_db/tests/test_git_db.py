
import tempfile
import unittest

from git_db import GitSet


class TestGitSet(unittest.TestCase):
    def test1(self):
        with tempfile.TemporaryDirectory() as dir_:
            gd = GitSet(dir_, 'stuff', do_create=True)
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
