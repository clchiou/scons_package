import unittest

from scons_package.label import PackageName
from scons_package.package_registry import PackageTrie


class TestPackageTrie(unittest.TestCase):

    def test_package_trie(self):
        a = PackageName.make_package_name('a')
        b = PackageName.make_package_name('a/b')
        c = PackageName.make_package_name('a/b/c')
        d = PackageName.make_package_name('a/y/y/y/d')
        e = PackageName.make_package_name('a/x/x/x/e')
        f = PackageName.make_package_name('f')
        h = PackageName.make_package_name('f/h')

        trie = PackageTrie()
        trie.add(a)
        trie.add(b)
        trie.add(d)

        self.assertEqual(a, trie.search(a))
        self.assertEqual(b, trie.search(b))
        self.assertEqual(b, trie.search(c))
        self.assertEqual(d, trie.search(d))
        self.assertEqual(a, trie.search(e))
        self.assertEqual(None, trie.search(f))
        self.assertEqual(None, trie.search(h))

    def test_package_trie_shorter(self):
        a = PackageName.make_package_name('a')
        b = PackageName.make_package_name('a/b')
        c = PackageName.make_package_name('a/b/c')

        # Add in order a, c, b to trigger package_name is shorter case
        trie = PackageTrie()
        trie.add(a)
        trie.add(c)
        trie.add(b)

        self.assertEqual(a, trie.search(a))
        self.assertEqual(b, trie.search(b))
        self.assertEqual(c, trie.search(c))


if __name__ == '__main__':
    unittest.main()
