
import tempfile
import unittest

from git_db import GitSet


class TestGitSet(unittest.TestCase):
    def test1(self):
        with tempfile.TemporaryDirectory() as dir_:
            gitset = GitSet(dir_, 'r', do_create=True)
            self.assertNotIn('xyz', gitset)
            self.assertEqual(len(gitset), 0)

            gitset.add('xyz')
            self.assertIn('xyz', gitset)
            self.assertEqual(len(gitset), 1)

            gitset.add('abc')
            self.assertIn('xyz', gitset)
            self.assertIn('abc', gitset)
            self.assertEqual(len(gitset), 2)

            gitset.add('def')
            self.assertIn('xyz', gitset)
            self.assertIn('abc', gitset)
            self.assertIn('def', gitset)
            self.assertEqual(len(gitset), 3)
