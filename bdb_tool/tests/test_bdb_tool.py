
import tempfile
import unittest

from bdb_tool import BdbUniqueId


class TestBdbUniqueId(unittest.TestCase):
    def test1(self):
        with tempfile.TemporaryDirectory() as dir_:
            elements = BdbUniqueId(dir_, '')
            x = elements.element_id(b'x')
            y = elements.element_id(b'y')
            self.assertNotEqual(x, y)  # uniqueness
            self.assertEqual(x, elements.element_id(b'x'))  # consistency
            self.assertEqual(y, elements.element_id(b'y'))  # consistency
            self.assertEqual(b'x', elements.element(x))  # inverse
            self.assertEqual(b'y', elements.element(y))  # inverse
