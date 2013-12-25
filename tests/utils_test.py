import unittest

from scons_package.utils import topology_sort


class TestTopologySort(unittest.TestCase):

    def test_empty_graph(self):
        nodes = []
        def get_neighbors(node):
            raise Exception()
        self.assertEqual([], list(topology_sort(nodes, get_neighbors)))

    def test_singleton(self):
        nodes = [1]
        graph = {1: []}
        self.assertEqual([1], list(topology_sort(nodes, lambda n: graph[n])))

        nodes = [1]
        graph = {1: [1]}  # Self-reference
        self.assertEqual([1], list(topology_sort(nodes, lambda n: graph[n])))

    def test_topology_sort(self):
        nodes = [1, 2]
        graph = {1: [], 2: [1]}
        order = [1, 2]
        self.assertEqual(order, list(topology_sort(nodes, lambda n: graph[n])))

        nodes = [1, 2, 3, 4]
        graph = {1: [2], 2: [3], 3: [4], 4: []}
        order = [4, 3, 2, 1]
        self.assertEqual(order, list(topology_sort(nodes, lambda n: graph[n])))

        nodes = [1, 2, 3, 4, 5, 6, 7]
        graph = {1: [], 2: [1], 3: [1], 4: [2], 5: [2], 6: [3], 7: [3]}
        order = [1, 2, 3, 4, 5, 6, 7]
        self.assertEqual(order, list(topology_sort(nodes, lambda n: graph[n])))

    def test_invalid_topology(self):
        nodes = [1, 2]
        graph = {1: [2], 2: [1]}
        self.assertRaises(ValueError, topology_sort, nodes, lambda n: graph[n])

        nodes = [1, 2, 3, 4]
        graph = {1: [2], 2: [3], 3: [4], 4: [1]}
        self.assertRaises(ValueError, topology_sort, nodes, lambda n: graph[n])


if __name__ == '__main__':
    unittest.main()
