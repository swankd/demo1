
import h5py
import json
import tempfile
import unittest

from h5graph import H5Graph
from h5graph.h5graph import H5UniqueId


class TestH5UniqueId(unittest.TestCase):
    def test1(self):
        with tempfile.NamedTemporaryFile() as f:
            elements = H5UniqueId(h5py.File(f.name), 'stuff', do_create=True)
            self.assertEqual(len(elements), 0)

            x = elements.element_id('x')
            y = elements.element_id('y')
            self.assertEqual(len(elements), 2)

            self.assertNotEqual(x, y)  # uniqueness
            self.assertEqual(x, elements.element_id('x'))  # consistency
            self.assertEqual(y, elements.element_id('y'))  # consistency
            self.assertEqual('x', elements.element(x))  # inverse
            self.assertEqual('y', elements.element(y))  # inverse
            self.assertEqual(len(elements), 2)


class TestH5Graph(unittest.TestCase):
    def test1(self):
        with tempfile.NamedTemporaryFile() as f:
            graph = H5Graph(f.name, 'w', do_create=True)
            self.assertEqual(graph.n_nouns, 0)
            self.assertEqual(graph.n_verbs, 0)
            self.assertEqual(graph.n_in_edges, 0)
            self.assertEqual(graph.n_out_edges, 0)

            x = graph.nouns.element_id('x')
            y = graph.nouns.element_id('y')
            z = graph.verbs.element_id('z')
            graph.in_edges[x] = json.dumps((y, z))
            graph.out_edges[y] = json.dumps((x, z))

            self.assertEqual(graph.n_nouns, 2)
            self.assertEqual(graph.n_verbs, 1)
            self.assertEqual(graph.n_in_edges, 1)
            self.assertEqual(graph.n_out_edges, 1)
            graph.report()
