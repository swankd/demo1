
import tempfile
import unittest

from git_db.gitdict import GitDict


class TestGitDict(unittest.TestCase):
    def test1(self):
        with tempfile.TemporaryDirectory() as dir_:
            gd = GitDict(dir_, 'stuff', do_create=True)
            self.assertNotIn('xyz', gd)
            self.assertEqual(len(gd), 0)
            gd.report()

            gd['xyz'] = '123'
            self.assertIn('xyz', gd)
            self.assertEqual(gd['xyz'], b'123')
            self.assertEqual(len(gd), 1)
            self.assertEqual(set(gd.keys()), {b'xyz'})

            gd['abc'] = '456' * 9
            self.assertIn('xyz', gd)
            self.assertIn('abc', gd)
            self.assertEqual(gd['xyz'], b'123')
            self.assertEqual(gd['abc'], b'456' * 9)
            self.assertEqual(len(gd), 2)
            self.assertEqual(set(gd.keys()), {b'xyz', b'abc'})

            gd['def'] = '789' * 999
            self.assertIn('xyz', gd)
            self.assertIn('abc', gd)
            self.assertIn('def', gd)
            self.assertEqual(gd['xyz'], b'123')
            self.assertEqual(gd['abc'], b'456' * 9)
            self.assertEqual(gd['def'], b'789' * 999)
            self.assertEqual(len(gd), 3)
            self.assertEqual(set(gd.keys()), {b'xyz', b'abc', b'def'})
