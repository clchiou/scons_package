import unittest

import SCons.Script

from scons_package.label import *


SCons.Script.Dir.path = 'a/b/c'


class TestPackageName(unittest.TestCase):

    def test_package_name(self):
        self.assertNotEqual('a', PackageName.make_package_name('a'))
        self.assertEqual('a', str(PackageName.make_package_name('a')))

        self.assertEqual('a', PackageName.make_package_name('a').path)
        self.assertEqual('a/b', PackageName.make_package_name('a/b').path)
        self.assertEqual('a/b/c', PackageName.make_package_name('a/b/c').path)

        p1 = PackageName.make_package_name('a/b/c')
        p2 = PackageName.make_package_name('a/b/c')
        self.assertEqual(p1, p2)
        self.assertEqual(hash(p1), hash(p2))

        p1 = PackageName.make_package_name('a/b')
        p2 = PackageName.make_package_name('a/b/c')
        self.assertNotEqual(p1, p2)
        self.assertNotEqual(hash(p1), hash(p2))

    def test_invalid_package_name(self):
        self.assertRaises(ValueError, PackageName.make_package_name, '/a/b/c')
        self.assertRaises(ValueError, PackageName.make_package_name, 'a/b/c/')
        self.assertRaises(ValueError, PackageName.make_package_name, 'a#b')


class TestTargetName(unittest.TestCase):

    def test_target_name(self):
        self.assertNotEqual('a', TargetName('a'))
        self.assertEqual('a', str(TargetName('a')))

        self.assertEqual('a', TargetName('a').path)
        self.assertEqual('a/b', TargetName('a/b').path)
        self.assertEqual('a/b/c', TargetName('a/b/c').path)

        t1 = TargetName('a/b/c')
        t2 = TargetName('a/b/c')
        self.assertEqual(t1, t2)
        self.assertEqual(hash(t1), hash(t2))

        t1 = TargetName('a/b')
        t2 = TargetName('a/b/c')
        self.assertNotEqual(t1, t2)
        self.assertNotEqual(hash(t1), hash(t2))

    def test_invalid_target_name(self):
        self.assertRaises(ValueError, TargetName, '')
        self.assertRaises(ValueError, TargetName, '/a/b/c')
        self.assertRaises(ValueError, TargetName, 'a/b/c/')
        self.assertRaises(ValueError, TargetName, 'a#b')


class TestLabel(unittest.TestCase):

    def test_label(self):
        self.assertNotEqual('#a/b/c:d/e/f', Label.make_label('#a/b/c:d/e/f'))
        self.assertEqual('#a/b/c:d/e/f', str(Label.make_label('#a/b/c:d/e/f')))

        self.assertEqual('#a/b/c:c', str(Label.make_label('#a/b/c')))
        self.assertEqual('#a/b/c:c', str(Label.make_label('#a/b/c:')))
        self.assertEqual('#a/b/c:c', str(Label.make_label('#:')))
        self.assertEqual('#a/b/c:c', str(Label.make_label(':')))
        self.assertEqual('#a/b/c:c', str(Label.make_label('')))
        self.assertEqual('#a/b/c:d/e/f', str(Label.make_label(':d/e/f')))
        self.assertEqual('#a/b/c:d/e/f', str(Label.make_label('d/e/f')))

        self.assertEqual('a/b/c/d/e/f', Label.make_label('#a/b/c:d/e/f').path)

        l1 = Label.make_label('#a/b/c:d/e/f')
        l2 = Label.make_label('#a/b/c:d/e/f')
        self.assertEqual(l1, l2)
        self.assertEqual(hash(l1), hash(l2))

        l1 = Label.make_label('#a/b/c:d/e/f')
        l2 = Label.make_label('#a/b/c:d/e')
        self.assertNotEqual(l1, l2)
        self.assertNotEqual(hash(l1), hash(l2))

        l1 = Label.make_label('#a/b/c:d/e/f')
        l2 = Label.make_label('#a/b:d/e/f')
        self.assertNotEqual(l1, l2)
        self.assertNotEqual(hash(l1), hash(l2))

    def test_make_label_list(self):
        labels = Label.make_label_list(': :')
        self.assertTrue(2, len(labels))
        self.assertEqual(Label.make_label(':'), labels[0])
        self.assertEqual(Label.make_label(':'), labels[1])

        labels = Label.make_label_list(['#g:x', '#h:y'])
        self.assertTrue(2, len(labels))
        self.assertEqual(Label.make_label('#g:x'), labels[0])
        self.assertEqual(Label.make_label('#h:y'), labels[1])

    def test_subclass(self):
        self.assertTrue(isinstance(LabelOfFile.make_label(':'), LabelOfFile))
        self.assertTrue(all(isinstance(label, LabelOfFile)
            for label in LabelOfFile.make_label_list(': :')))

        self.assertTrue(isinstance(LabelOfRule.make_label(':'), LabelOfRule))
        self.assertTrue(all(isinstance(label, LabelOfRule)
            for label in LabelOfRule.make_label_list(': :')))

    def test_invalid_label(self):
        self.assertRaises(ValueError, Label.make_label, 'a/b/c:')


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
